/**
 * Media Picker — Phase 2
 *
 * Usage in any form template:
 *
 *   <input type="hidden" name="image_url" id="myImageUrl" value="{{ current_url }}">
 *   <input type="hidden" name="media_id"  id="myMediaId"  value="{{ current_id }}">
 *
 *   <button type="button"
 *           data-media-picker
 *           data-target-url="#myImageUrl"
 *           data-target-id="#myMediaId"
 *           data-preview="#myPreview"
 *           data-type="image">             ← optional: pre-filter to images only
 *     Choose from Library
 *   </button>
 *
 *   <div id="myPreview"></div>
 *
 * The picker writes the selected file's URL into data-target-url
 * and the Media.pk into data-target-id (optional).
 */

(function () {
  "use strict";

  // ── State ────────────────────────────────────────────────────
  const state = {
    page: 1,
    q: "",
    type: "",
    folderId: "",
    selectedItem: null,      // { id, url, title, is_image }
    currentTrigger: null,    // The button that opened the picker
    searchTimer: null,
    apiUrl: "/media/api/picker/",
  };

  // ── DOM refs (resolved after DOMContentLoaded) ───────────────
  let overlay, modal, grid, loading, empty, stats,
      pagination, searchInput, selectedInfo,
      insertBtn, folderList;

  // ── Init ─────────────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {
    overlay      = document.getElementById("mediaPickerOverlay");
    modal        = document.getElementById("mediaPickerModal");
    grid         = document.getElementById("mpGrid");
    loading      = document.getElementById("mpLoading");
    empty        = document.getElementById("mpEmpty");
    stats        = document.getElementById("mpStats");
    pagination   = document.getElementById("mpPagination");
    searchInput  = document.getElementById("mpSearch");
    selectedInfo = document.getElementById("mpSelectedInfo");
    insertBtn    = document.getElementById("mediaPickerInsert");
    folderList   = document.getElementById("mpFolderList");

    if (!overlay) return; // modal not in DOM (not authenticated)

    bindEvents();
  });

  // ── Event Binding ─────────────────────────────────────────────
  function bindEvents() {
    // Open: event delegation — catches dynamically added buttons
    document.addEventListener("click", function (e) {
      const trigger = e.target.closest("[data-media-picker]");
      if (trigger) {
        e.preventDefault();
        openPicker(trigger);
      }
    });

    // Close
    document.getElementById("mediaPickerClose").addEventListener("click", closePicker);
    document.getElementById("mediaPickerCancel").addEventListener("click", closePicker);
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) closePicker();
    });

    // ESC key
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && overlay.style.display !== "none") closePicker();
    });

    // Insert
    insertBtn.addEventListener("click", insertSelected);

    // Search with 350ms debounce
    searchInput.addEventListener("input", function () {
      clearTimeout(state.searchTimer);
      state.searchTimer = setTimeout(function () {
        state.q = searchInput.value.trim();
        state.page = 1;
        fetchMedia();
      }, 350);
    });

    // Type tabs
    document.querySelectorAll(".mp-type-tab").forEach(function (tab) {
      tab.addEventListener("click", function () {
        document.querySelectorAll(".mp-type-tab").forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        state.type = tab.dataset.type;
        state.page = 1;
        fetchMedia();
      });
    });

    // Grid item selection (event delegation)
    grid.addEventListener("click", function (e) {
      const item = e.target.closest(".mp-item");
      if (!item) return;
      selectItem(item);
    });

    // Folder clicks (event delegation — populated dynamically)
    folderList.addEventListener("click", function (e) {
      const btn = e.target.closest(".mp-folder-btn");
      if (!btn) return;
      document.querySelectorAll(".mp-folder-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.folderId = btn.dataset.folder;
      state.page = 1;
      fetchMedia();
    });
  }

  // ── Open / Close ─────────────────────────────────────────────
  function openPicker(trigger) {
    state.currentTrigger = trigger;
    state.selectedItem = null;
    state.page = 1;
    state.q = "";
    state.folderId = "";

    // Pre-filter by type if trigger specifies it
    const triggerType = trigger.dataset.type || "";
    state.type = triggerType;

    // Sync type tabs
    document.querySelectorAll(".mp-type-tab").forEach(function (tab) {
      tab.classList.toggle("active", tab.dataset.type === triggerType);
    });

    // Reset UI
    searchInput.value = "";
    updateInsertButton(null);
    document.querySelectorAll(".mp-folder-btn").forEach(b => b.classList.remove("active"));
    const allBtn = folderList.querySelector('[data-folder=""]');
    if (allBtn) allBtn.classList.add("active");

    overlay.style.display = "flex";
    document.body.style.overflow = "hidden";

    fetchMedia();
  }

  function closePicker() {
    overlay.style.display = "none";
    document.body.style.overflow = "";
    state.currentTrigger = null;
    state.selectedItem = null;
  }

  // ── Fetch Media from API ──────────────────────────────────────
  function fetchMedia() {
    showLoading(true);
    grid.innerHTML = "";
    empty.style.display = "none";

    const params = new URLSearchParams({
      page: state.page,
      q: state.q,
      type: state.type,
      folder: state.folderId,
    });

    fetch(state.apiUrl + "?" + params.toString(), {
      headers: { "X-Requested-With": "XMLHttpRequest" },
      credentials: "same-origin",
    })
      .then(function (res) {
        if (!res.ok) throw new Error("API error " + res.status);
        return res.json();
      })
      .then(function (data) {
        showLoading(false);
        renderFolders(data.folders);
        renderGrid(data.results);
        renderPagination(data);
        stats.textContent =
          data.total_count + " file" + (data.total_count !== 1 ? "s" : "") +
          (state.q ? ' matching "' + state.q + '"' : "");
      })
      .catch(function (err) {
        showLoading(false);
        stats.textContent = "Failed to load media.";
        console.error("Media picker fetch error:", err);
      });
  }

  // ── Render Folders in Sidebar ─────────────────────────────────
  function renderFolders(folders) {
    // Build flat → nested map
    const map = {};
    folders.forEach(function (f) { map[f.id] = { ...f, children: [] }; });

    const roots = [];
    folders.forEach(function (f) {
      if (f.parent_id && map[f.parent_id]) {
        map[f.parent_id].children.push(map[f.id]);
      } else {
        roots.push(map[f.id]);
      }
    });

    function buildItems(nodes, depth) {
      return nodes.map(function (node) {
        const indent = depth * 12;
        const children = node.children.length
          ? '<ul class="mp-folder-children">' + buildItems(node.children, depth + 1).join("") + "</ul>"
          : "";
        return (
          '<li>' +
          '<button class="mp-folder-btn" data-folder="' + node.id + '" ' +
          'style="padding-left:' + (10 + indent) + 'px">' +
          '<i class="fa-solid fa-folder" style="color:#f59e0b;font-size:0.75rem;"></i> ' +
          escapeHtml(node.name) +
          '</button>' +
          children +
          '</li>'
        );
      });
    }

    // Keep the "All Media" button, replace the rest
    const allBtn = folderList.querySelector("li:first-child");
    folderList.innerHTML = "";
    if (allBtn) folderList.appendChild(allBtn);

    if (roots.length > 0) {
      folderList.insertAdjacentHTML("beforeend", buildItems(roots, 0).join(""));
    }

    // Re-mark active
    folderList.querySelectorAll(".mp-folder-btn").forEach(function (btn) {
      btn.classList.toggle(
        "active",
        btn.dataset.folder === String(state.folderId)
      );
    });
  }

  // ── Render Grid ───────────────────────────────────────────────
  function renderGrid(results) {
    if (results.length === 0) {
      empty.style.display = "flex";
      return;
    }
    empty.style.display = "none";

    const html = results.map(function (item) {
      const thumb = item.is_image
        ? '<img src="' + escapeHtml(item.url) + '" alt="' + escapeHtml(item.title) + '" loading="lazy">'
        : '<span class="mp-file-icon"><i class="fa-solid ' + getFileIcon(item.type) + '"></i></span>';

      return (
        '<div class="mp-item" ' +
        'data-id="' + item.id + '" ' +
        'data-url="' + escapeHtml(item.url) + '" ' +
        'data-title="' + escapeHtml(item.title) + '" ' +
        'data-is-image="' + item.is_image + '" ' +
        'title="' + escapeHtml(item.title) + '">' +
        '<div class="mp-item-thumb">' + thumb + '</div>' +
        '<div class="mp-item-info">' +
        '<div class="mp-item-name">' + escapeHtml(truncate(item.title, 20)) + "</div>" +
        '<div class="mp-item-meta">' + escapeHtml(item.size_display) +
        (item.dimensions ? " · " + item.dimensions : "") +
        "</div>" +
        "</div>" +
        "</div>"
      );
    });

    grid.innerHTML = html.join("");
  }

  // ── Render Pagination ─────────────────────────────────────────
  function renderPagination(data) {
    if (data.total_pages <= 1) {
      pagination.innerHTML = "";
      return;
    }
    pagination.innerHTML =
      '<button class="mp-page-btn" id="mpPrevPage" ' + (!data.has_previous ? "disabled" : "") + ">← Prev</button>" +
      '<span class="mp-page-info">Page ' + data.page + " of " + data.total_pages + "</span>" +
      '<button class="mp-page-btn" id="mpNextPage" ' + (!data.has_next ? "disabled" : "") + ">Next →</button>";

    const prev = document.getElementById("mpPrevPage");
    const next = document.getElementById("mpNextPage");
    if (prev) prev.addEventListener("click", function () { state.page--; fetchMedia(); });
    if (next) next.addEventListener("click", function () { state.page++; fetchMedia(); });
  }

  // ── Select Item ───────────────────────────────────────────────
  function selectItem(itemEl) {
    document.querySelectorAll(".mp-item.selected").forEach(function (el) {
      el.classList.remove("selected");
    });
    itemEl.classList.add("selected");

    state.selectedItem = {
      id: itemEl.dataset.id,
      url: itemEl.dataset.url,
      title: itemEl.dataset.title,
      is_image: itemEl.dataset.isImage === "true",
    };

    updateInsertButton(state.selectedItem);
  }

  function updateInsertButton(item) {
    if (item) {
      insertBtn.disabled = false;
      selectedInfo.textContent = "Selected: " + item.title;
    } else {
      insertBtn.disabled = true;
      selectedInfo.textContent = "No file selected";
    }
  }

  // ── Insert Selected into Form ─────────────────────────────────
  function insertSelected() {
    if (!state.selectedItem || !state.currentTrigger) return;

    const trigger = state.currentTrigger;
    const item = state.selectedItem;

    // Write URL to target field
    const urlTarget = trigger.dataset.targetUrl;
    if (urlTarget) {
      const urlInput = document.querySelector(urlTarget);
      if (urlInput) urlInput.value = item.url;
    }

    // Write Media.pk to optional id field
    const idTarget = trigger.dataset.targetId;
    if (idTarget) {
      const idInput = document.querySelector(idTarget);
      if (idInput) idInput.value = item.id;
    }

    // Update preview element if specified
    const previewTarget = trigger.dataset.preview;
    if (previewTarget) {
      const previewEl = document.querySelector(previewTarget);
      if (previewEl) {
        if (item.is_image) {
          previewEl.innerHTML =
            '<div class="preview-wrapper" style="position:relative;display:inline-block;margin-top:10px;">' +
            '<img src="' + escapeHtml(item.url) + '" style="max-width:300px;max-height:200px;border:1px solid #e5e7eb;border-radius:4px;display:block;" alt="' + escapeHtml(item.title) + '">' +
            '<p style="margin-top:4px;font-size:12px;color:#666;">' + escapeHtml(item.title) + "</p>" +
            "</div>";
        } else {
          previewEl.innerHTML =
            '<p style="margin-top:8px;font-size:13px;color:#374151;">' +
            '<i class="fa-solid fa-file" style="margin-right:6px;"></i>' +
            escapeHtml(item.title) +
            "</p>";
        }
      }
    }

    // Fire a custom event so any form-specific JS can react
    trigger.dispatchEvent(
      new CustomEvent("mediaPicked", {
        bubbles: true,
        detail: { id: item.id, url: item.url, title: item.title },
      })
    );

    closePicker();
  }

  // ── Helpers ───────────────────────────────────────────────────
  function showLoading(visible) {
    loading.style.display = visible ? "flex" : "none";
    if (visible) grid.innerHTML = "";
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function truncate(str, n) {
    return str && str.length > n ? str.slice(0, n) + "…" : str;
  }

  function getFileIcon(type) {
    if (type === "video") return "fa-video";
    if (type === "image") return "fa-image";
    return "fa-file";
  }
})();
