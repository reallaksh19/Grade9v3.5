/**
 * Grade9V3 Display & Accessibility Controls
 * Manages global font adjustment and UI zoom scale across all pages and explorers.
 * Persists preferences in localStorage ('grade9v3_font_scale', 'grade9v3_ui_scale').
 * Synchronizes in real-time across tabs via storage event.
 */

(function () {
  'use strict';

  const STORAGE_KEY_FONT = 'grade9v3_font_scale';
  const STORAGE_KEY_SCALE = 'grade9v3_ui_scale';

  let fontScale = 1.0;
  let uiScale = 1.0;

  // Read saved preferences
  try {
    const savedFont = localStorage.getItem(STORAGE_KEY_FONT);
    if (savedFont) {
      const parsed = parseFloat(savedFont);
      if (!isNaN(parsed) && parsed >= 0.75 && parsed <= 1.6) fontScale = parsed;
    }
    const savedScale = localStorage.getItem(STORAGE_KEY_SCALE);
    if (savedScale) {
      const parsed = parseFloat(savedScale);
      if (!isNaN(parsed) && parsed >= 0.7 && parsed <= 1.5) uiScale = parsed;
    }
  } catch (e) {
    console.warn('Grade9V3: localStorage unavailable for display preferences', e);
  }

  function applyDisplaySettings() {
    // 1. Apply Font Scale
    document.documentElement.style.setProperty('--font-scale', fontScale.toString());
    document.documentElement.style.fontSize = (16 * fontScale) + 'px';

    // 2. Apply UI Zoom Scale
    document.documentElement.style.setProperty('--ui-scale', uiScale.toString());
    if (document.body) {
      document.body.style.zoom = uiScale.toString();
    }

    // 3. Update active UI controls if rendered
    updateWidgetUI();
  }

  function setFontScale(scale, save = true) {
    fontScale = Math.max(0.75, Math.min(1.6, parseFloat(scale)));
    if (save) {
      try { localStorage.setItem(STORAGE_KEY_FONT, fontScale.toFixed(2)); } catch (e) {}
    }
    applyDisplaySettings();
  }

  function setUiScale(scale, save = true) {
    uiScale = Math.max(0.7, Math.min(1.5, parseFloat(scale)));
    if (save) {
      try { localStorage.setItem(STORAGE_KEY_SCALE, uiScale.toFixed(2)); } catch (e) {}
    }
    applyDisplaySettings();
  }

  function stepFont(delta) {
    const next = Math.round((fontScale + delta) * 100) / 100;
    setFontScale(next);
  }

  function stepScale(delta) {
    const next = Math.round((uiScale + delta) * 100) / 100;
    setUiScale(next);
  }

  function resetDisplay() {
    setFontScale(1.0);
    setUiScale(1.0);
  }

  function togglePopover() {
    const popover = document.getElementById('g9-display-popover');
    if (popover) {
      popover.classList.toggle('active');
    }
  }

  function openPopover() {
    const popover = document.getElementById('g9-display-popover');
    if (popover) {
      popover.classList.add('active');
    }
  }

  function closePopover() {
    const popover = document.getElementById('g9-display-popover');
    if (popover) {
      popover.classList.remove('active');
    }
  }

  // Cross-tab synchronization
  window.addEventListener('storage', (e) => {
    if (e.key === STORAGE_KEY_FONT && e.newValue) {
      setFontScale(parseFloat(e.newValue), false);
    } else if (e.key === STORAGE_KEY_SCALE && e.newValue) {
      setUiScale(parseFloat(e.newValue), false);
    }
  });

  // Apply immediately upon script execution
  applyDisplaySettings();

  // Re-apply once body is loaded to ensure body.style.zoom is set
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWidget);
  } else {
    initWidget();
  }

  function updateWidgetUI() {
    const fontSlider = document.getElementById('g9-font-slider');
    const fontLabel = document.getElementById('g9-font-val');
    const scaleSlider = document.getElementById('g9-scale-slider');
    const scaleLabel = document.getElementById('g9-scale-val');

    const fontPct = Math.round(fontScale * 100) + '%';
    const scalePct = Math.round(uiScale * 100) + '%';

    if (fontSlider) fontSlider.value = fontScale;
    if (fontLabel) fontLabel.textContent = fontPct;
    if (scaleSlider) scaleSlider.value = uiScale;
    if (scaleLabel) scaleLabel.textContent = scalePct;

    // Update all inline badges
    document.querySelectorAll('.g9-inline-font-val').forEach(el => {
      el.textContent = fontPct;
    });
    document.querySelectorAll('.g9-inline-scale-val').forEach(el => {
      el.textContent = scalePct;
    });
  }

  function initWidget() {
    applyDisplaySettings();

    // Prevent duplicate injection
    if (document.getElementById('g9-display-widget-root')) {
      updateWidgetUI();
      return;
    }

    // Inject CSS for the display widget
    const style = document.createElement('style');
    style.id = 'g9-display-widget-styles';
    style.textContent = `
      #g9-display-widget-root {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 2147483647;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      }
      .g9-display-trigger {
        background: #161b22;
        border: 1px solid #58a6ff;
        color: #f0f6fc;
        padding: 7px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.6);
        transition: all 0.2s ease;
        backdrop-filter: blur(8px);
      }
      .g9-display-trigger:hover {
        background: #21262d;
        border-color: #79c0ff;
        color: #79c0ff;
        transform: translateY(-1px);
        box-shadow: 0 6px 22px rgba(88, 166, 255, 0.25);
      }
      .g9-display-popover {
        position: fixed;
        bottom: 60px;
        right: 20px;
        width: 290px;
        background: #161b22;
        border: 1px solid #444c56;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 12px 36px rgba(0,0,0,0.75);
        display: none;
        flex-direction: column;
        gap: 14px;
        z-index: 2147483647;
        backdrop-filter: blur(14px);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      }
      .g9-display-popover.active {
        display: flex;
      }
      .g9-popover-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(68, 76, 86, 0.5);
        padding-bottom: 8px;
      }
      .g9-popover-title {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #c9d1d9;
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .g9-popover-actions {
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .g9-close-btn {
        background: transparent;
        border: none;
        color: #8b949e;
        font-size: 16px;
        cursor: pointer;
        padding: 0 4px;
        line-height: 1;
        transition: color 0.15s;
      }
      .g9-close-btn:hover {
        color: #f0f6fc;
      }
      .g9-control-row {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .g9-control-label-wrap {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11.5px;
        font-weight: 600;
        color: #c9d1d9;
      }
      .g9-val-badge {
        font-family: ui-monospace, monospace;
        color: #58a6ff;
        font-weight: 700;
        background: rgba(56, 139, 253, 0.12);
        border: 1px solid rgba(56, 139, 253, 0.3);
        padding: 1px 6px;
        border-radius: 4px;
      }
      .g9-slider {
        width: 100%;
        accent-color: #58a6ff;
        cursor: pointer;
        height: 6px;
      }
      .g9-btn-pill-row {
        display: flex;
        gap: 5px;
        margin-top: 2px;
      }
      .g9-pill {
        background: #21262d;
        border: 1px solid #30363d;
        color: #9aa4b2;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 10.5px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.1s ease;
        flex: 1;
        text-align: center;
      }
      .g9-pill:hover {
        background: #2d333b;
        color: #58a6ff;
        border-color: #58a6ff;
      }
      .g9-reset-btn {
        background: transparent;
        border: 1px solid #30363d;
        color: #9aa4b2;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s;
      }
      .g9-reset-btn:hover {
        background: rgba(248, 81, 73, 0.1);
        border-color: #f85149;
        color: #ff7b72;
      }
      .g9-popover-hint {
        font-size: 10px;
        color: #8b949e;
        line-height: 1.4;
        border-top: 1px solid rgba(68, 76, 86, 0.3);
        padding-top: 6px;
      }
      .g9-display-trigger-btn {
        background: var(--bg-card, #161b22);
        border: 1px solid var(--border, #30363d);
        color: var(--text, #c9d1d9);
        font-size: 12px;
        font-weight: 600;
        padding: 5px 10px;
        border-radius: 6px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        transition: all 0.15s;
      }
      .g9-display-trigger-btn:hover {
        border-color: var(--accent, #58a6ff);
        color: var(--accent, #58a6ff);
      }
    `;
    document.head.appendChild(style);

    // Create widget container anchored directly to documentElement (immune to body zoom/scroll)
    const container = document.createElement('div');
    container.id = 'g9-display-widget-root';

    container.innerHTML = `
      <button class="g9-display-trigger" id="g9-display-toggle-btn" title="Global Display & Accessibility (Font & UI Scale)">
        <span>🔤 / 🔍</span>
        <span>Display & Scale</span>
      </button>

      <div class="g9-display-popover" id="g9-display-popover">
        <div class="g9-popover-header">
          <span class="g9-popover-title">⚙️ Display &amp; Scale</span>
          <div class="g9-popover-actions">
            <button class="g9-reset-btn" id="g9-btn-reset" title="Reset Font &amp; Scale to 100%">Reset</button>
            <button class="g9-close-btn" id="g9-btn-close" title="Close">✕</button>
          </div>
        </div>

        <!-- Font Size Slider -->
        <div class="g9-control-row">
          <div class="g9-control-label-wrap">
            <span>🔤 Global Font Size</span>
            <span class="g9-val-badge" id="g9-font-val">100%</span>
          </div>
          <input type="range" class="g9-slider" id="g9-font-slider" min="0.80" max="1.45" step="0.05" value="1.0">
          <div class="g9-btn-pill-row">
            <button class="g9-pill" data-font="0.85">85%</button>
            <button class="g9-pill" data-font="1.00">100%</button>
            <button class="g9-pill" data-font="1.15">115%</button>
            <button class="g9-pill" data-font="1.30">130%</button>
          </div>
        </div>

        <!-- UI Zoom Scale Slider -->
        <div class="g9-control-row">
          <div class="g9-control-label-wrap">
            <span>🔍 Global UI Zoom</span>
            <span class="g9-val-badge" id="g9-scale-val">100%</span>
          </div>
          <input type="range" class="g9-slider" id="g9-scale-slider" min="0.75" max="1.35" step="0.05" value="1.0">
          <div class="g9-btn-pill-row">
            <button class="g9-pill" data-scale="0.80">80%</button>
            <button class="g9-pill" data-scale="0.90">90%</button>
            <button class="g9-pill" data-scale="1.00">100%</button>
            <button class="g9-pill" data-scale="1.20">120%</button>
          </div>
        </div>

        <div class="g9-popover-hint">
          💡 Persists in localStorage and syncs across open tabs in real-time.
        </div>
      </div>
    `;

    // Append to documentElement so position:fixed is always relative to the viewport window
    document.documentElement.appendChild(container);

    // Event handlers
    const toggleBtn = document.getElementById('g9-display-toggle-btn');
    const popover = document.getElementById('g9-display-popover');
    const closeBtn = document.getElementById('g9-btn-close');
    const fontSlider = document.getElementById('g9-font-slider');
    const scaleSlider = document.getElementById('g9-scale-slider');
    const resetBtn = document.getElementById('g9-btn-reset');

    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      popover.classList.toggle('active');
    });

    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      popover.classList.remove('active');
    });

    document.addEventListener('click', (e) => {
      if (!container.contains(e.target) && !e.target.closest('.g9-display-trigger-btn') && !e.target.closest('.display-controls-wrap')) {
        popover.classList.remove('active');
      }
    });

    fontSlider.addEventListener('input', (e) => {
      setFontScale(e.target.value);
    });

    scaleSlider.addEventListener('input', (e) => {
      setUiScale(e.target.value);
    });

    resetBtn.addEventListener('click', () => {
      resetDisplay();
    });

    // Preset pills
    container.querySelectorAll('.g9-pill').forEach(pill => {
      pill.addEventListener('click', (e) => {
        if (pill.dataset.font) {
          setFontScale(pill.dataset.font);
        } else if (pill.dataset.scale) {
          setUiScale(pill.dataset.scale);
        }
      });
    });

    // Initial update
    updateWidgetUI();
  }

  // Expose global API
  window.Grade9Display = {
    setFontScale,
    setUiScale,
    stepFont,
    stepScale,
    resetDisplay,
    togglePopover,
    openPopover,
    closePopover,
    getFontScale: () => fontScale,
    getUiScale: () => uiScale
  };
})();
