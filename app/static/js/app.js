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

// Botones con data-action enfocan la búsqueda global y, opcionalmente,
// le asignan un placeholder o valor de ayuda (ver topbar.html, home.css).
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("globalSearch");
  if (!searchInput) return;

  document.querySelectorAll("[data-action]").forEach((trigger) => {
    trigger.addEventListener("click", () => {
      const { placeholder, value } = trigger.dataset;

      if (placeholder) searchInput.placeholder = placeholder;
      if (value) searchInput.value = value;

      searchInput.focus();
    });
  });
});
