/*
 * Comportamiento de la vista Activos: filtrado por categoría/búsqueda
 * y panel lateral (drawer) con la ficha del activo seleccionado.
 * Se carga solo en assets.html (ver base.html: block extra_js).
 */

document.addEventListener("DOMContentLoaded", () => {
  const dataEl = document.getElementById("assetsData");
  const i18nEl = document.getElementById("assetsI18n");
  if (!dataEl || !i18nEl) return;

  const assets = JSON.parse(dataEl.textContent);
  const i18n = JSON.parse(i18nEl.textContent);
  const assetsById = Object.fromEntries(assets.map((asset) => [asset.id, asset]));

  const rows = document.querySelectorAll(".asset-row");
  const noResultsRow = document.getElementById("noResultsRow");
  const visibleCountEl = document.getElementById("visibleCount");
  const filterPills = document.querySelectorAll("#filterPills .filter-pill");
  const searchInput = document.getElementById("assetsSearch");

  const drawer = document.getElementById("assetDrawer");
  const drawerBackdrop = document.getElementById("drawerBackdrop");
  const drawerClose = document.getElementById("drawerClose");

  const drawerIcon = document.getElementById("drawerIcon");
  const drawerStatus = document.getElementById("drawerStatus");
  const drawerStatusLabel = document.getElementById("drawerStatusLabel");
  const drawerTag = document.getElementById("drawerTag");
  const drawerTitle = document.getElementById("drawerTitle");
  const drawerSerial = document.getElementById("drawerSerial");
  const drawerCpu = document.getElementById("drawerCpu");
  const drawerRam = document.getElementById("drawerRam");
  const drawerStorage = document.getElementById("drawerStorage");
  const drawerOs = document.getElementById("drawerOs");
  const drawerWarranty = document.getElementById("drawerWarranty");
  const drawerCustodianCard = document.getElementById("drawerCustodianCard");

  let currentCategory = "all";
  let searchQuery = "";

  function fillSpec(el, value) {
    el.textContent = value || i18n.drawerNoData;
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function renderCustodian(usuario) {
    drawerCustodianCard.replaceChildren();

    if (!usuario) {
      drawerCustodianCard.appendChild(el("p", "custodian-card__empty", i18n.drawerNoCustodian));
      return;
    }

    const identity = el("div", "custodian-card__identity");
    identity.appendChild(el("div", "custodian-card__avatar", usuario.iniciales));
    const identityText = el("div");
    identityText.appendChild(el("div", "custodian-card__name", usuario.nombre));
    identityText.appendChild(el("div", "custodian-card__role", usuario.rol || ""));
    identity.appendChild(identityText);

    const grid = el("div", "custodian-card__grid");
    grid.appendChild(buildGridEntry(i18n.drawerDepartment, usuario.departamento));
    grid.appendChild(buildGridEntry(i18n.drawerLocation, usuario.ubicacion));

    drawerCustodianCard.appendChild(identity);
    drawerCustodianCard.appendChild(grid);
  }

  function buildGridEntry(label, value) {
    const entry = el("div");
    entry.appendChild(el("span", "custodian-card__grid-label", label));
    entry.appendChild(el("span", "custodian-card__grid-value", value || i18n.drawerNoData));
    return entry;
  }

  function openDrawer(assetId) {
    const asset = assetsById[assetId];
    if (!asset) return;

    rows.forEach((row) => row.classList.toggle("is-selected", row.dataset.assetId === assetId));

    drawerIcon.textContent = asset.icono;
    drawerTag.textContent = asset.codigo ? `#${asset.codigo}` : "";
    drawerTitle.textContent = asset.nombre;
    drawerSerial.textContent = asset.numeroSerie || i18n.drawerNoData;

    fillSpec(drawerCpu, asset.cpu);
    fillSpec(drawerRam, asset.ram);
    fillSpec(drawerStorage, asset.almacenamiento);
    fillSpec(drawerOs, asset.sistemaOperativo);
    fillSpec(drawerWarranty, asset.garantia);

    const modifier = asset.asignado ? "assigned" : asset.estado === "Disponible" ? "available" : "neutral";
    drawerStatus.className = `status-pill status-pill--${modifier}`;
    drawerStatusLabel.textContent = asset.asignado ? i18n.statusInUse : asset.estado;

    renderCustodian(asset.usuario);

    drawer.classList.add("is-open");
    drawer.setAttribute("aria-hidden", "false");
    drawerBackdrop.classList.add("is-open");
  }

  function closeDrawer() {
    drawer.classList.remove("is-open");
    drawer.setAttribute("aria-hidden", "true");
    drawerBackdrop.classList.remove("is-open");
    rows.forEach((row) => row.classList.remove("is-selected"));
  }

  rows.forEach((row) => {
    row.addEventListener("click", () => openDrawer(row.dataset.assetId));
  });

  document.querySelectorAll("[data-open-asset]").forEach((btn) => {
    btn.addEventListener("click", (event) => {
      event.stopPropagation();
      openDrawer(btn.dataset.openAsset);
    });
  });

  drawerClose.addEventListener("click", closeDrawer);
  drawerBackdrop.addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeDrawer();
  });

  function applyFilters() {
    let visible = 0;

    rows.forEach((row) => {
      const matchesCategory = currentCategory === "all" || row.dataset.categoria === currentCategory;
      const matchesSearch = !searchQuery || row.textContent.toLowerCase().includes(searchQuery);
      const show = matchesCategory && matchesSearch;

      row.style.display = show ? "" : "none";
      if (show) visible += 1;
    });

    if (visibleCountEl) visibleCountEl.textContent = String(visible);
    if (noResultsRow) noResultsRow.style.display = visible === 0 && rows.length > 0 ? "" : "none";
  }

  filterPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      filterPills.forEach((p) => p.classList.remove("is-active"));
      pill.classList.add("is-active");
      currentCategory = pill.dataset.cat;
      applyFilters();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", (event) => {
      searchQuery = event.target.value.trim().toLowerCase();
      applyFilters();
    });
  }
});
