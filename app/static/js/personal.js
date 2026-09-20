/*
 * Comportamiento de la vista Personal: filtrado por modalidad/estado de
 * asignación/búsqueda, panel lateral (drawer) con la ficha de la persona,
 * y los modales de alta/edición/eliminación. Se carga solo en
 * personal.html (ver base.html: block extra_js).
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
  const drawer = document.getElementById("personDrawer");
  const drawerBackdrop = document.getElementById("drawerBackdrop");
  const drawerClose = document.getElementById("drawerClose");

  const drawerAvatar = document.getElementById("drawerAvatar");
  const drawerStatus = document.getElementById("drawerStatus");
  const drawerStatusLabel = document.getElementById("drawerStatusLabel");
  const drawerTag = document.getElementById("drawerTag");
  const drawerName = document.getElementById("drawerName");
  const drawerEmail = document.getElementById("drawerEmail");
  const drawerDepartment = document.getElementById("drawerDepartment");
  const drawerLocation = document.getElementById("drawerLocation");
  const drawerSince = document.getElementById("drawerSince");
  const drawerAssetCounter = document.getElementById("drawerAssetCounter");
  const drawerAssetList = document.getElementById("drawerAssetList");

  let currentFilter = "all";
  let searchQuery = "";
  let currentPersonaId = null;

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function fillSpec(target, value) {
    target.textContent = value || i18n.noData;
  }

  function renderAssetList(activos, persona) {
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

      const headerMain = el("div", "asset-chip__header-main");
      headerMain.appendChild(el("h4", "asset-chip__name", asset.nombre));
      headerMain.appendChild(el("span", "badge", asset.categoria));
      header.appendChild(headerMain);

      const removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.className = "asset-chip__remove";
      removeBtn.setAttribute("aria-label", i18n.removeAssetLabel);
      removeBtn.appendChild(el("span", "material-symbols-outlined", "link_off"));
      removeBtn.addEventListener("click", (event) => {
        event.stopPropagation();
        abrirQuitarActivo(persona, asset);
      });
      header.appendChild(removeBtn);

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
    currentPersonaId = personaId;

    rows.forEach((row) => row.classList.toggle("is-selected", row.dataset.personaId === personaId));

    drawerAvatar.textContent = persona.iniciales;
    drawerTag.textContent = persona.codigo ? `#${persona.codigo}` : "";
    drawerName.textContent = persona.nombre;
    drawerEmail.textContent = persona.email || i18n.noData;

    fillSpec(drawerDepartment, persona.departamento);
    const modalidadYUbicacion = [persona.modalidad, persona.ubicacion].filter(Boolean).join(" — ");
    fillSpec(drawerLocation, modalidadYUbicacion);
    fillSpec(drawerSince, persona.incorporacion);

    const modifier = persona.tieneActivos ? "assigned" : "neutral";
    drawerStatus.className = `status-pill status-pill--${modifier}`;
    drawerStatusLabel.textContent = persona.tieneActivos ? i18n.statusComplete : i18n.statusPending;

    const count = persona.activos.length;
    drawerAssetCounter.textContent = count === 1 ? `1 ${i18n.assetSingular}` : `${count} ${i18n.assetPlural}`;
    renderAssetList(persona.activos, persona);

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

  // --- Modal "Nuevo Colaborador" ---
  const nuevoColaboradorModal = wireModal("nuevoColaboradorModal", "nuevoColaboradorBackdrop", [
    "closeNuevoColaboradorBtn",
    "cancelNuevoColaboradorBtn",
  ]);
  const openNuevoColaboradorBtn = document.getElementById("openNuevoColaboradorBtn");
  if (openNuevoColaboradorBtn) openNuevoColaboradorBtn.addEventListener("click", nuevoColaboradorModal.open);

  // --- Modal "Editar Colaborador" ---
  const editarColaboradorModal = wireModal("editarColaboradorModal", "editarColaboradorBackdrop", [
    "closeEditarColaboradorBtn",
    "cancelEditarColaboradorBtn",
  ]);
  const editarColaboradorForm = document.getElementById("editarColaboradorForm");
  const editarColaboradorContexto = document.getElementById("editarColaboradorContexto");

  function setFieldValue(id, value) {
    const field = document.getElementById(id);
    if (field) field.value = value || "";
  }

  function abrirEdicion(personaId) {
    const persona = personaById[personaId];
    if (!persona || !editarColaboradorForm) return;

    editarColaboradorForm.action = `/personal/${persona.id}/editar`;
    if (editarColaboradorContexto) editarColaboradorContexto.textContent = persona.nombre;

    setFieldValue("editar-email", persona.email);
    setFieldValue("editar-departamento", persona.departamento);
    setFieldValue("editar-ubicacion", persona.ubicacion);

    document.querySelectorAll('input[name="editar-modalidad"]').forEach((radio) => {
      radio.checked = radio.value === (persona.modalidad || "");
    });

    editarColaboradorModal.open();
  }

  // --- Modal "Eliminar Colaborador" ---
  const eliminarColaboradorModal = wireModal("eliminarColaboradorModal", "eliminarColaboradorBackdrop", [
    "closeEliminarColaboradorBtn",
    "cancelEliminarColaboradorBtn",
  ]);
  const eliminarColaboradorForm = document.getElementById("eliminarColaboradorForm");
  const eliminarColaboradorBody = document.getElementById("eliminarColaboradorBody");
  const eliminarColaboradorSubmit = document.getElementById("eliminarColaboradorSubmit");

  function abrirEliminacion(personaId) {
    const persona = personaById[personaId];
    if (!persona || !eliminarColaboradorForm) return;

    eliminarColaboradorForm.action = `/personal/${persona.id}/eliminar`;

    // Si tiene una cuenta de acceso vinculada, el servidor va a rechazar el
    // borrado igual (ver personal_controller.eliminar) — acá se lo decimos
    // antes de que intente, en vez de dejar que mande el form para nada.
    if (eliminarColaboradorSubmit) eliminarColaboradorSubmit.hidden = persona.tieneCuenta;

    if (eliminarColaboradorBody) {
      const plantilla = persona.tieneCuenta
        ? i18n.deleteBlockedHasAccount
        : persona.tieneActivos
          ? i18n.deleteConfirmBodyWithAssets
          : i18n.deleteConfirmBody;
      eliminarColaboradorBody.textContent = plantilla
        .replace("{nombre}", persona.nombre)
        .replace("{n}", String(persona.cantidadActivos));
    }

    eliminarColaboradorModal.open();
  }

  // --- Modal "Quitar activo asignado" ---
  const quitarActivoModal = wireModal("quitarActivoModal", "quitarActivoBackdrop", [
    "closeQuitarActivoBtn",
    "cancelQuitarActivoBtn",
  ]);
  const quitarActivoForm = document.getElementById("quitarActivoForm");
  const quitarActivoBody = document.getElementById("quitarActivoBody");

  function abrirQuitarActivo(persona, asset) {
    if (!persona || !asset || !quitarActivoForm) return;

    quitarActivoForm.action = `/personal/${persona.id}/activos/${asset.id}/quitar`;
    if (quitarActivoBody) {
      quitarActivoBody.textContent = i18n.unassignConfirmBody.replace("{nombre}", asset.nombre);
    }

    quitarActivoModal.open();
  }

  const drawerEditBtn = document.getElementById("drawerEditBtn");
  const drawerDeleteBtn = document.getElementById("drawerDeleteBtn");
  if (drawerEditBtn) drawerEditBtn.addEventListener("click", () => currentPersonaId && abrirEdicion(currentPersonaId));
  if (drawerDeleteBtn) {
    drawerDeleteBtn.addEventListener("click", () => currentPersonaId && abrirEliminacion(currentPersonaId));
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    closeDrawer();
    nuevoColaboradorModal.close();
    editarColaboradorModal.close();
    eliminarColaboradorModal.close();
    quitarActivoModal.close();
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
