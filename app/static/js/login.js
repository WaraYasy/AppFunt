/*
 * Comportamiento de /login: desliza entre el panel de bienvenida y el
 * formulario, y alterna la visibilidad de la contraseña. Se carga solo
 * en login.html (página standalone, no pasa por base.html).
 */
document.addEventListener("DOMContentLoaded", () => {
  const deck = document.getElementById("loginDeck");
  const btnLoginTrigger = document.getElementById("btnLoginTrigger");
  const btnScrollHint = document.getElementById("btnScrollHint");
  const btnBackWelcome = document.getElementById("btnBackWelcome");
  const inputPassword = document.getElementById("inputPassword");
  const btnTogglePwd = document.getElementById("btnTogglePwd");
  const inputUsername = document.querySelector('input[name="username"]');

  if (!deck) return;

  // Si el servidor reabre la página con errores de validación, arrancamos
  // directo en el panel del formulario (no tiene sentido volver a mostrar
  // la bienvenida y obligar a hacer clic de nuevo).
  let formActivo = document.querySelector(".field--invalid") !== null;

  function mostrarFormulario() {
    deck.classList.add("is-form-active");
    formActivo = true;
    setTimeout(() => inputUsername && inputUsername.focus(), 650);
  }

  function mostrarBienvenida() {
    deck.classList.remove("is-form-active");
    formActivo = false;
  }

  if (formActivo) mostrarFormulario();

  [btnLoginTrigger, btnScrollHint].forEach((btn) => {
    if (btn) btn.addEventListener("click", mostrarFormulario);
  });

  if (btnBackWelcome) btnBackWelcome.addEventListener("click", mostrarBienvenida);

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && formActivo) mostrarBienvenida();
  });

  if (btnTogglePwd && inputPassword) {
    btnTogglePwd.addEventListener("click", () => {
      const esPassword = inputPassword.getAttribute("type") === "password";
      inputPassword.setAttribute("type", esPassword ? "text" : "password");
      const icono = btnTogglePwd.querySelector(".material-symbols-outlined");
      if (icono) icono.textContent = esPassword ? "visibility_off" : "visibility";
    });
  }
});
