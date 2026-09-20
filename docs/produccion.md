# Preparación de la base de datos de producción

Runbook para pasar de la base SQLite/dev a MySQL en producción. Pensado para
seguirse una vez, a mano — no hay nada acá que deba correrse automáticamente.

## 0. Contexto: cómo se crean las tablas hoy

La app **no usa Flask-Migrate** (decisión explícita del proyecto). El esquema
se crea con `Base.metadata.create_all(bind=engine)`, que corre solo una vez
al arrancar la app ([app/\_\_init\_\_.py](../app/__init__.py)).

Esto importa por dos motivos:

- **`create_all()` solo crea tablas que no existen.** No altera tablas
  existentes. Si mañana agregás una columna a un modelo, correr la app de
  nuevo contra una base que ya tiene esa tabla **no la va a actualizar** —
  vas a necesitar un `ALTER TABLE` a mano.
- No hay historial de migraciones. Cualquier cambio de esquema en producción
  es una operación manual, sin rollback automático. Anotá en algún lado
  (changelog, commit) cada `ALTER TABLE` que corras contra producción.

## 1. Variables de entorno (`.env`)

El repo trae [.env.example](../.env.example) como plantilla:

```
FLASK_ENV=development
SECRET_KEY=cambia-esto
DATABASE_URL=mysql+pymysql://usuario:password@localhost:3306/appwara
```

Para producción, copiá ese archivo a `.env` (nunca lo commitees) y reemplazá:

- **`SECRET_KEY`**: no dejes `cambia-esto`. Generá uno real:
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```
  Firma las cookies de sesión (login, CSRF, remember-me) — si se filtra o se
  reusa el de dev, cualquiera puede falsificar una sesión.
- **`DATABASE_URL`**: la cadena de conexión real a tu MySQL de producción
  (host, puerto, usuario, password, nombre de base — ver paso 2).
- **`FLASK_ENV`**: dejalo en `production` (o quitalo) — no corras la app con
  `debug=True` contra producción, expone un debugger interactivo con
  ejecución de código arbitrario si algo tira un 500.

## 2. Provisionar la base MySQL

Corré esto vos mismo contra tu servidor MySQL (con un usuario administrador,
no con el que va a usar la app):

```sql
CREATE DATABASE appwara
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'appwara_app'@'%' IDENTIFIED BY 'una-clave-fuerte-y-distinta-a-todo';

GRANT SELECT, INSERT, UPDATE, DELETE ON appwara.* TO 'appwara_app'@'%';
FLUSH PRIVILEGES;
```

Notas:

- **`utf8mb4`, no `utf8`**: los datos tienen acentos y eñes (`Ingeniería`,
  `Diseño`, `Administración`, nombres de personas). El `utf8` de MySQL es en
  realidad un subconjunto recortado; `utf8mb4` es el que soporta Unicode
  completo. Si la base queda creada con el charset por defecto del servidor
  y no es `utf8mb4`, vas a tener problemas silenciosos con esos valores.
- **Privilegios mínimos**: el usuario de la app solo necesita
  `SELECT/INSERT/UPDATE/DELETE`. No le des `CREATE`/`ALTER`/`DROP` — esas
  las corrés vos a mano cuando hace falta (ver punto 0), no la app en
  caliente.
- Ajustá el host (`'%'` es "desde cualquier host" — restringilo a la IP real
  del servidor de la app si podés) y la contraseña por algo que generes vos.

## 3. Verificar la conexión antes de arrancar la app

Con el `.env` ya apuntando a producción:

```bash
python3 -c "
from app.config import Config
from sqlalchemy import create_engine, text
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
with engine.connect() as conn:
    conn.execute(text('SELECT 1'))
print('Conexión OK')
"
```

Si esto falla, arreglalo acá antes de seguir — no tiene sentido levantar la
app todavía.

## 4. Crear las tablas (primera vez)

Con la base vacía y la conexión verificada, alcanza con levantar la app una
vez — `create_all()` corre en `create_app()` y crea `personas`, `assets` y
`admins` solo. No hace falta ningún comando extra ni ningún script de
"init db".

## 5. Crear la primera cuenta de acceso (IT)

Sin esto nadie puede entrar: `/`, `/activos` y `/personas` están protegidas
con `@login_required` y no hay ninguna cuenta `Admin` todavía.

```python
# crear_admin.py — corré una vez apuntando a producción, después borralo
# (o al menos no lo dejes con la clave en texto plano en el repo/servidor)
from app import create_app
from app.database import SessionLocal, generar_uuid
from app.models.admin import Admin

app = create_app()
with app.app_context():
    db = SessionLocal()
    cuenta = Admin(id=generar_uuid(), username="tu.usuario")
    cuenta.set_password("una-clave-segura-de-produccion")
    db.add(cuenta)
    db.commit()
    print("Cuenta creada:", cuenta.username)
```

Si querés que el sidebar muestre tu nombre real en vez del username, primero
necesitás una fila en `Persona` y le pasás su `id` como `id_persona=...`
al crear el `Admin`.

## 6. Cosas que conviene resolver antes de ir a producción (no están hechas)

Ninguno de estos puntos está implementado todavía — son recomendaciones,
no pasos ya cubiertos por el código actual:

- **`pool_pre_ping` / `pool_recycle` en el engine.** [app/database.py](../app/database.py)
  crea el engine sin esto. MySQL cierra conexiones idle por su cuenta
  (`wait_timeout`, default 8h en muchas instalaciones); sin `pool_pre_ping`,
  la primera consulta después de un rato de inactividad puede tirar
  `MySQL server has gone away`. Es un problema real de estabilidad en
  producción, no cosmético.
- **Cookies de sesión seguras.** `Config` no define `SESSION_COOKIE_SECURE`
  ni `SESSION_COOKIE_SAMESITE` — con HTTPS en producción convendría
  `SESSION_COOKIE_SECURE = True` para que la cookie de sesión (y la de
  "recordar dispositivo") no viaje nunca por HTTP plano.
- **Servidor WSGI de producción.** Hoy [run.py](../run.py) solo tiene
  `app.run(debug=True)`, el servidor de desarrollo de Flask. No está pensado
  para producción (rendimiento, sin manejo de múltiples workers). Vas a
  necesitar algo como gunicorn/waitress delante, más un proxy (nginx/etc.)
  — esto es un tema aparte de la base de datos, lo menciono porque suele
  ir de la mano del mismo despliegue.
- **Backups.** No hay ningún mecanismo de backup automatizado hoy. Como
  mínimo, un `mysqldump` programado (cron) antes de cualquier `ALTER TABLE`
  manual, y con la frecuencia que te parezca razonable para el resto.

## 7. Checklist final

- [ ] `.env` de producción con `SECRET_KEY` real y `DATABASE_URL` correcta
- [ ] Base creada con `utf8mb4` / `utf8mb4_unicode_ci`
- [ ] Usuario de MySQL para la app con privilegios mínimos (sin DDL)
- [ ] Conexión verificada (paso 3)
- [ ] App levantada una vez → tablas creadas
- [ ] Primera cuenta `Admin` creada y probada en `/login`
- [ ] Datos de prueba (smoke tests) **no** están en esta base — arranca vacía
      salvo la cuenta de IT
