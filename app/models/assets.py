from app.extensions import db


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<Asset {self.nombre}>"
