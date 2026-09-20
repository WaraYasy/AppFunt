/*
 * Comportamiento de la vista Personal: filtrado por modalidad/estado de
 * asignación/búsqueda, y panel lateral (drawer) con la ficha de la persona
 * seleccionada. Se carga solo en personal.html (ver base.html: block extra_js).
 */

document.addEventListener("DOMContentLoaded", () => {
  const dataEl = document.getElementById("personalData");
  const i18nEl = document.getElementById("personalI18n");
  if (!dataEl || !i18nEl) return;

  const personal = JSON.parse(dataEl.textContent);
  const i18n = JSON.parse(i18nEl.textContent);
  const personaById = Object.fromEntries(personal.map((persona) => [persona.id, persona]));

  const rows = document.querySelectorAll(".person-row");
  const noResultsRow = document.getElementById("noResultsRow");
  const visibleCountEl = document.getElementById("visibleCount");
  const filterPills = document.querySelectorAll("#filterPills .filter-pill");
  const searchInput = document.getElementById("personalSearch");

  const drawer = document.getElementById("personDrawer");
  const drawerBackdrop = document.getElementById("drawerBackdrop");
  const drawerClose = document.getElementById("drawerClose");

  const drawerAvatar = document.getElementById("drawerAvatar");
  const drawerStatus = document.getElementById("drawerStatus");
  const drawerStatusLabel = document.getElementById("drawerStatusLabel");
  const drawerTag = document.getElementById("drawerTag");
  const drawerName = document.getElementById("drawerName");
  const drawerEmail = document.getElementById("drawerEmail");
  const drawerRole = document.getElementById("drawerRole");
  const drawerDepartment = document.getElementById("drawerDepartment");
  const drawerLocation = document.getElementById("drawerLocation");
  const drawerSince = document.getElementById("drawerSince");
  const drawerAssetCounter = document.getElementById("drawerAssetCounter");
  const drawerAssetList = document.getElementById("drawerAssetList");

  let currentFilter = "all";
  let searchQuery = "";

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function fillSpec(target, value) {
    target.textContent = value || i18n.noData;
  }

  function renderAssetList(activos) {
    drawerAssetList.replaceChildren();

    if (!activos || activos.length === 0) {
      drawerAssetList.appendChild(el("p", "empty-note", i18n.noAssets));
      return;
    }

    activos.forEach((asset) => {
      const chip = el("div", "asset-chip card");

      const icon = el("div", "asset-chip__icon");
      icon.appendChild(el("span", "material-symbols-outlined", asset.icono));
      chip.appendChild(icon);

      const body = el("div", "asset-chip__body");
      const header = el("div", "asset-chip__header");
      header.appendChild(el("h4", "asset-chip__name", asset.nombre));
      header.appendChild(el("span", "badge", asset.categoria));
      body.appendChild(header);

      const meta = asset.numeroSerie || asset.codigo;
      if (meta) body.appendChild(el("div", "asset-chip__meta", meta));

      chip.appendChild(body);
      drawerAssetList.appendChild(chip);
    });
  }

  function openDrawer(personaId) {
    const persona = personaById[personaId];
    if (!persona) return;

    rows.forEach((row) => row.classList.toggle("is-selected", row.dataset.personaId === personaId));

    drawerAvatar.textContent = persona.iniciales;
    drawerTag.textContent = persona.codigo ? `#${persona.codigo}` : "";
    drawerName.textContent = persona.nombre;
    drawerEmail.textContent = persona.email || i18n.noData;

    fillSpec(drawerRole, persona.rol);
    fillSpec(drawerDepartment, persona.departamento);
    const modalidadYUbicacion = [persona.modalidad, persona.ubicacion].filter(Boolean).join(" — ");
    fillSpec(drawerLocation, modalidadYUbicacion);
    fillSpec(drawerSince, persona.incorporacion);

    const modifier = persona.tieneActivos ? "assigned" : "neutral";
    drawerStatus.className = `status-pill status-pill--${modifier}`;
    drawerStatusLabel.textContent = persona.tieneActivos ? i18n.statusComplete : i18n.statusPending;

    const count = persona.activos.length;
    drawerAssetCounter.textContent = count === 1 ? `1 ${i18n.assetSingular}` : `${count} ${i18n.assetPlural}`;
    renderAssetList(persona.activos);

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
    row.addEventListener("click", () => openDrawer(row.dataset.personaId));
  });

  document.querySelectorAll("[data-open-person]").forEach((btn) => {
    btn.addEventListener("click", (event) => {
      event.stopPropagation();
      openDrawer(btn.dataset.openPerson);
    });
  });

  drawerClose.addEventListener("click", closeDrawer);
  drawerBackdrop.addEventListener("click", closeDrawer);

  // Modal "Nuevo Colaborador"
  const nuevoColaboradorModal = document.getElementById("nuevoColaboradorModal");
  const nuevoColaboradorBackdrop = document.getElementById("nuevoColaboradorBackdrop");
  const openNuevoColaboradorBtn = document.getElementById("openNuevoColaboradorBtn");
  const closeNuevoColaboradorBtn = document.getElementById("closeNuevoColaboradorBtn");
  const cancelNuevoColaboradorBtn = document.getElementById("cancelNuevoColaboradorBtn");

  function openNuevoColaboradorModal() {
    if (!nuevoColaboradorModal) return;
    nuevoColaboradorModal.classList.add("is-open");
    nuevoColaboradorBackdrop.classList.add("is-open");
  }

  function closeNuevoColaboradorModal() {
    if (!nuevoColaboradorModal) return;
    nuevoColaboradorModal.classList.remove("is-open");
    nuevoColaboradorBackdrop.classList.remove("is-open");
  }

  if (openNuevoColaboradorBtn) openNuevoColaboradorBtn.addEventListener("click", openNuevoColaboradorModal);
  if (closeNuevoColaboradorBtn) closeNuevoColaboradorBtn.addEventListener("click", closeNuevoColaboradorModal);
  if (cancelNuevoColaboradorBtn) cancelNuevoColaboradorBtn.addEventListener("click", closeNuevoColaboradorModal);
  if (nuevoColaboradorBackdrop) nuevoColaboradorBackdrop.addEventListener("click", closeNuevoColaboradorModal);

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    closeDrawer();
    closeNuevoColaboradorModal();
  });

  function applyFilters() {
    let visible = 0;

    rows.forEach((row) => {
      const tieneActivos = row.dataset.tieneActivos === "true";
      const modalidad = row.dataset.modalidad;

      let matchesFilter = true;
      if (currentFilter === "with_assets") matchesFilter = tieneActivos;
      else if (currentFilter === "pending") matchesFilter = !tieneActivos;
      else if (currentFilter === "remote") matchesFilter = modalidad === "Remoto";
      else if (currentFilter === "onsite") matchesFilter = modalidad === "Presencial";

      const matchesSearch = !searchQuery || row.textContent.toLowerCase().includes(searchQuery);
      const show = matchesFilter && matchesSearch;

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
      currentFilter = pill.dataset.filter;
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
