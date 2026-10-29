"""Drag-to-resize sidebar (no partial collapse — min width = full nav labels)."""

import streamlit as st
import streamlit.components.v1 as components


def inject_sidebar_resize() -> None:
    components.html(
        """
<script>
(function () {
  const KEY = "ns_sidebar_width_px";
  /* Do not drag narrower than full expanded nav (avoids wrapped labels) */
  const MIN = 288;
  const MAX = 420;
  const DEFAULT_W = 300;

  if (window.parent.__nsSidebarResizeInit) return;
  window.parent.__nsSidebarResizeInit = true;
  const doc = window.parent.document;
  const win = doc.defaultView || window.parent;

  const style = doc.createElement("style");
  style.textContent = `
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    section[data-testid="stSidebar"] > div[data-testid="stVerticalBlock"] > div:first-child button,
    [data-testid="stHeader"] button[kind="headerNoPadding"] {
      display: none !important;
    }
    #ns-sidebar-resizer {
      position: fixed;
      top: 0;
      bottom: 0;
      width: 8px;
      margin-left: -4px;
      z-index: 1000002;
      cursor: col-resize;
      background: transparent;
      transition: background 0.15s ease;
    }
    #ns-sidebar-resizer:hover,
    #ns-sidebar-resizer.ns-dragging {
      background: rgba(0, 120, 212, 0.35);
    }
    section[data-testid="stSidebar"].ns-resize-active {
      transition: none !important;
    }
    body.ns-sidebar-dragging {
      cursor: col-resize !important;
      user-select: none !important;
    }
  `;
  doc.head.appendChild(style);

  function sidebar() {
    return doc.querySelector('section[data-testid="stSidebar"]');
  }

  function clamp(w) {
    return Math.min(MAX, Math.max(MIN, w));
  }

  function ensureHandle() {
    let handle = doc.getElementById("ns-sidebar-resizer");
    if (!handle) {
      handle = doc.createElement("div");
      handle.id = "ns-sidebar-resizer";
      handle.title = "Drag to resize sidebar (not narrower than full menu)";
      doc.body.appendChild(handle);

      let dragging = false;
      let startX = 0;
      let startW = 0;

      handle.addEventListener("mousedown", (e) => {
        const sb = sidebar();
        if (!sb) return;
        dragging = true;
        handle.classList.add("ns-dragging");
        doc.body.classList.add("ns-sidebar-dragging");
        sb.classList.add("ns-resize-active");
        startX = e.clientX;
        startW = sb.getBoundingClientRect().width;
        e.preventDefault();
      });

      win.addEventListener("mousemove", (e) => {
        if (!dragging) return;
        const sb = sidebar();
        if (!sb) return;
        applyWidth(sb, clamp(startW + (e.clientX - startX)));
      });

      win.addEventListener("mouseup", () => {
        if (!dragging) return;
        dragging = false;
        handle.classList.remove("ns-dragging");
        doc.body.classList.remove("ns-sidebar-dragging");
        const sb = sidebar();
        if (sb) {
          sb.classList.remove("ns-resize-active");
          const w = clamp(sb.getBoundingClientRect().width);
          applyWidth(sb, w);
          try { window.parent.localStorage.setItem(KEY, String(Math.round(w))); } catch (err) {}
        }
      });
    }
    return handle;
  }

  function applyWidth(sb, w) {
    const cw = clamp(w);
    sb.style.width = cw + "px";
    sb.style.minWidth = cw + "px";
    sb.style.maxWidth = cw + "px";
    sb.classList.remove("ns-sidebar-narrow");
    doc.documentElement.classList.remove("ns-sidebar-narrow-mode");
    positionHandle();
  }

  function positionHandle() {
    const sb = sidebar();
    const handle = ensureHandle();
    if (!sb || !handle) return;
    const rect = sb.getBoundingClientRect();
    if (rect.width < MIN - 4) {
      applyWidth(sb, MIN);
      return;
    }
    handle.style.display = "block";
    handle.style.left = rect.right + "px";
  }

  let restored = false;
  function restoreOnce() {
    if (restored) return;
    const sb = sidebar();
    if (!sb) return;
    let w = DEFAULT_W;
    try {
      const raw = window.parent.localStorage.getItem(KEY);
      if (raw) {
        const parsed = parseInt(raw, 10);
        if (parsed >= MIN && parsed <= MAX) w = parsed;
      }
    } catch (err) {}
    applyWidth(sb, w);
    restored = true;
    positionHandle();
  }

  const obs = new MutationObserver(() => {
    positionHandle();
    restoreOnce();
    const sb = sidebar();
    if (sb && sb.getBoundingClientRect().width < MIN - 4) applyWidth(sb, MIN);
  });
  obs.observe(doc.body, { childList: true, subtree: true, attributes: true });

  win.addEventListener("resize", positionHandle);
  setInterval(positionHandle, 800);
  restoreOnce();
})();
</script>
        """,
        height=0,
    )
