/*
 * Comportamiento global del shell de la app (sidebar + topbar).
 * Se carga en todas las páginas vía base.html.
 */

document.addEventListener("keydown", (event) => {
  const isSearchShortcut = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k";
  if (!isSearchShortcut) return;

  const searchInput = document.getElementById("globalSearch");
  if (!searchInput) return;

  event.preventDefault();
  searchInput.focus();
});

// Buscador global del topbar: no filtra nada en el lugar (aparece en
// Dashboard/Activos/Personas, no siempre hay algo que filtrar ahí mismo).
// Al presionar Enter, manda a la búsqueda real de Activos con ese texto.
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("globalSearch");
  if (!searchInput) return;

  searchInput.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") return;
    const valor = searchInput.value.trim();
    if (!valor) return;
    window.location.href = `/activos?q=${encodeURIComponent(valor)}`;
  });
});

// Menú de Configuración (sidebar): idioma / tema. Cada opción es un form
// que hace un POST real, así que el menú solo necesita abrir y cerrar.
document.addEventListener("DOMContentLoaded", () => {
  const trigger = document.getElementById("settingsMenuTrigger");
  const panel = document.getElementById("settingsMenuPanel");
  const menu = document.getElementById("settingsMenu");
  if (!trigger || !panel || !menu) return;

  function abrir() {
    panel.hidden = false;
    trigger.setAttribute("aria-expanded", "true");
  }

  function cerrar() {
    panel.hidden = true;
    trigger.setAttribute("aria-expanded", "false");
  }

  trigger.addEventListener("click", () => {
    if (panel.hidden) abrir();
    else cerrar();
  });

  document.addEventListener("click", (event) => {
    if (!panel.hidden && !menu.contains(event.target)) cerrar();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) cerrar();
  });
});
