/*
 * Comportamiento de la vista Activos: filtrado por categoría/búsqueda,
 * panel lateral (drawer) con la ficha del activo, y los modales de
 * alta/edición/eliminación. Se carga solo en assets.html (ver base.html:
 * block extra_js).
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

  // --- Helper genérico para abrir/cerrar un par modal+backdrop ---
  function wireModal(modalId, backdropId, extraCloseIds) {
    const modal = document.getElementById(modalId);
    const backdrop = document.getElementById(backdropId);
    if (!modal || !backdrop) return { open: () => {}, close: () => {} };

    function open() {
      modal.classList.add("is-open");
      backdrop.classList.add("is-open");
    }

    function close() {
      modal.classList.remove("is-open");
      backdrop.classList.remove("is-open");
    }

    backdrop.addEventListener("click", close);
    (extraCloseIds || []).forEach((id) => {
      const btn = document.getElementById(id);
      if (btn) btn.addEventListener("click", close);
    });

    return { open, close };
  }

  // --- Drawer de detalle ---
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
  let currentAssetId = null;

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
      drawerCustodianCard.appendChild(el("p", "empty-note", i18n.drawerNoCustodian));
      return;
    }

    const identity = el("div", "custodian-card__identity");
    identity.appendChild(el("div", "custodian-card__avatar", usuario.iniciales));
    const identityText = el("div");
    identityText.appendChild(el("div", "custodian-card__name", usuario.nombre));
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
    currentAssetId = assetId;

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

    renderCustodian(asset.custodio);

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

  // --- Modal "Nuevo Activo" ---
  const nuevoActivoModal = wireModal("nuevoActivoModal", "nuevoActivoBackdrop", [
    "closeNuevoActivoBtn",
    "cancelNuevoActivoBtn",
  ]);
  const openNuevoActivoBtn = document.getElementById("openNuevoActivoBtn");
  if (openNuevoActivoBtn) openNuevoActivoBtn.addEventListener("click", nuevoActivoModal.open);

  // --- Modal "Editar Activo" ---
  const editarActivoModal = wireModal("editarActivoModal", "editarActivoBackdrop", [
    "closeEditarActivoBtn",
    "cancelEditarActivoBtn",
  ]);
  const editarActivoForm = document.getElementById("editarActivoForm");
  const editarActivoContexto = document.getElementById("editarActivoContexto");
  const editarIdPersonalSelect = document.getElementById("editar-id_personal");

  function setFieldValue(id, value) {
    const field = document.getElementById(id);
    if (field) field.value = value || "";
  }

  function abrirEdicion(assetId) {
    const asset = assetsById[assetId];
    if (!asset || !editarActivoForm) return;

    editarActivoForm.action = `/activos/${asset.id}/editar`;

    if (editarActivoContexto) {
      const partes = [asset.nombre, asset.categoria, asset.numeroSerie].filter(Boolean);
      editarActivoContexto.textContent = partes.join(" · ");
    }

    setFieldValue("editar-ubicacion", asset.ubicacion);
    setFieldValue("editar-cpu", asset.cpu);
    setFieldValue("editar-ram", asset.ram);
    setFieldValue("editar-almacenamiento", asset.almacenamiento);
    setFieldValue("editar-sistema_operativo", asset.sistemaOperativo);

    // El select de custodio se arma en el servidor con <option> por cada
    // persona; acá solo elegimos la que corresponde (o "" = sin asignar).
    if (editarIdPersonalSelect) {
      editarIdPersonalSelect.value = asset.idPersonal || "";
    }

    editarActivoModal.open();
  }

  // --- Modal "Eliminar Activo" ---
  const eliminarActivoModal = wireModal("eliminarActivoModal", "eliminarActivoBackdrop", [
    "closeEliminarActivoBtn",
    "cancelEliminarActivoBtn",
  ]);
  const eliminarActivoForm = document.getElementById("eliminarActivoForm");
  const eliminarActivoBody = document.getElementById("eliminarActivoBody");

  function abrirEliminacion(assetId) {
    const asset = assetsById[assetId];
    if (!asset || !eliminarActivoForm) return;

    eliminarActivoForm.action = `/activos/${asset.id}/eliminar`;
    if (eliminarActivoBody) {
      eliminarActivoBody.textContent = i18n.deleteConfirmBody.replace("{nombre}", asset.nombre);
    }

    eliminarActivoModal.open();
  }

  const drawerEditBtn = document.getElementById("drawerEditBtn");
  const drawerDeleteBtn = document.getElementById("drawerDeleteBtn");
  if (drawerEditBtn) drawerEditBtn.addEventListener("click", () => currentAssetId && abrirEdicion(currentAssetId));
  if (drawerDeleteBtn) {
    drawerDeleteBtn.addEventListener("click", () => currentAssetId && abrirEliminacion(currentAssetId));
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    closeDrawer();
    nuevoActivoModal.close();
    editarActivoModal.close();
    eliminarActivoModal.close();
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
