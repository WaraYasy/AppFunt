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
  const personalDataEl = document.getElementById("assetsPersonalData");
  const personal = personalDataEl ? JSON.parse(personalDataEl.textContent) : [];

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

  // --- Selector de custodio con buscador (ver macros/forms.html: campo_asignacion).
  // El <select> nativo (`fieldId`) sigue siendo el que valida y se manda con
  // el form; este widget solo lo maneja desde arriba. ---
  function wireAssignPicker(fieldId, personalList) {
    const nativeSelect = document.getElementById(fieldId);
    const picker = document.querySelector(`.assign-picker[data-picker-for="${fieldId}"]`);
    if (!nativeSelect || !picker) return { render: () => {}, setValue: () => {} };

    const currentLabel = picker.querySelector("[data-current-label]");
    const assignBtn = picker.querySelector("[data-assign-btn]");
    const assignBtnLabel = picker.querySelector("[data-assign-btn-label]");
    const clearBtn = picker.querySelector("[data-clear-btn]");
    const panel = picker.querySelector("[data-panel]");
    const searchInput = picker.querySelector("[data-search]");
    const resultsEl = picker.querySelector("[data-results]");

    function personaById(id) {
      return personalList.find((persona) => persona.id === id) || null;
    }

    function render() {
      const persona = personaById(nativeSelect.value);
      currentLabel.textContent = persona ? persona.nombre : i18n.assignUnassignedLabel;
      assignBtnLabel.textContent = persona ? i18n.assignChangeButton : i18n.assignButton;
      clearBtn.hidden = !persona;
    }

    function closePanel() {
      panel.hidden = true;
    }

    function renderResultados(query) {
      resultsEl.replaceChildren();
      const q = query.trim().toLowerCase();
      const coincidencias = personalList.filter(
        (persona) =>
          !q || persona.nombre.toLowerCase().includes(q) || (persona.departamento || "").toLowerCase().includes(q)
      );

      if (coincidencias.length === 0) {
        resultsEl.appendChild(el("p", "assign-picker__empty", i18n.assignNoResults));
        return;
      }

      coincidencias.forEach((persona) => {
        const boton = document.createElement("button");
        boton.type = "button";
        boton.className = "assign-picker__result";
        boton.appendChild(el("span", "assign-picker__result-avatar", persona.iniciales));
        const texto = el("span", "assign-picker__result-text");
        texto.appendChild(el("span", "assign-picker__result-name", persona.nombre));
        if (persona.departamento) texto.appendChild(el("span", "assign-picker__result-meta", persona.departamento));
        boton.appendChild(texto);
        boton.addEventListener("click", () => {
          nativeSelect.value = persona.id;
          render();
          closePanel();
        });
        resultsEl.appendChild(boton);
      });
    }

    function openPanel() {
      panel.hidden = false;
      searchInput.value = "";
      renderResultados("");
      searchInput.focus();
    }

    assignBtn.addEventListener("click", () => (panel.hidden ? openPanel() : closePanel()));
    clearBtn.addEventListener("click", () => {
      nativeSelect.value = "";
      render();
      closePanel();
    });
    searchInput.addEventListener("input", (event) => renderResultados(event.target.value));
    document.addEventListener("click", (event) => {
      if (!picker.contains(event.target)) closePanel();
    });

    render();
    return {
      render,
      setValue(id) {
        nativeSelect.value = id || "";
        render();
      },
    };
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
  let currentEstado = "";
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
  wireAssignPicker("id_personal", personal);

  // --- Modal "Editar Activo" ---
  const editarActivoModal = wireModal("editarActivoModal", "editarActivoBackdrop", [
    "closeEditarActivoBtn",
    "cancelEditarActivoBtn",
  ]);
  const editarActivoForm = document.getElementById("editarActivoForm");
  const editarActivoContexto = document.getElementById("editarActivoContexto");
  const editarAsignarPicker = wireAssignPicker("editar-id_personal", personal);

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
    editarAsignarPicker.setValue(asset.idPersonal);

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
      const matchesEstado = !currentEstado || row.dataset.estado === currentEstado;
      const matchesSearch = !searchQuery || row.textContent.toLowerCase().includes(searchQuery);
      const show = matchesCategory && matchesEstado && matchesSearch;

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

  // Accesos directos del dashboard (ver home.quick_actions en index.html):
  // ?nuevo=1 abre el modal de alta, ?estado=disponible/asignado filtra de
  // entrada, ?buscar=1 pone el foco en la búsqueda para tipear la serie.
  const paramsIniciales = new URLSearchParams(window.location.search);
  if (paramsIniciales.get("nuevo") === "1") nuevoActivoModal.open();

  const estadoInicial = paramsIniciales.get("estado");
  if (estadoInicial) {
    currentEstado = estadoInicial;
    applyFilters();
  }

  if (paramsIniciales.get("buscar") === "1" && searchInput) searchInput.focus();
});
