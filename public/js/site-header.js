(function() {
  'use strict';

  const script = document.currentScript;
  const root = (script && script.dataset.siteRoot) || '';
  const parent = (script && script.dataset.siteParent) || root + 'index.html';

  // 1. Legacy header enhancement (for question-bank or older pages)
  function initLegacyHeader() {
    const header = document.querySelector('header.site-nav');
    if (!header || header.dataset.g9Enhanced) return;
    header.dataset.g9Enhanced = 'true';

    document.body.classList.add('g9-fixed-header');
    header.classList.add('site-nav-enhanced');

    const brand = header.querySelector('.brand-link');
    const nav = header.querySelector('.nav-links');

    if (brand && nav) {
      if (!header.querySelector('.site-leading')) {
        const leading = document.createElement('div');
        leading.className = 'site-leading';
        const back = document.createElement('button');
        back.type = 'button';
        back.className = 'site-icon-btn';
        back.title = 'Back';
        back.setAttribute('aria-label', 'Go back');
        back.textContent = '←';
        back.addEventListener('click', () => { history.back(); });
        leading.appendChild(back);
        header.insertBefore(leading, brand);
        leading.appendChild(brand);
      }

      if (!header.querySelector('.site-actions')) {
        const actions = document.createElement('div');
        actions.className = 'site-actions';

        const searchBtn = document.createElement('button');
        searchBtn.type = 'button';
        searchBtn.className = 'site-icon-btn g9-search-btn';
        searchBtn.title = 'Search Grade9V3 (Ctrl/⌘ K)';
        searchBtn.setAttribute('aria-label', 'Search Grade9V3');
        searchBtn.textContent = '🔍';
        searchBtn.addEventListener('click', openSearch);

        const themeBtn = document.createElement('button');
        themeBtn.type = 'button';
        themeBtn.className = 'site-icon-btn g9-theme-btn';
        themeBtn.title = 'Toggle Dark / Light Theme';
        themeBtn.setAttribute('aria-label', 'Toggle theme');
        themeBtn.textContent = '🌓';
        themeBtn.addEventListener('click', () => {
          if (window.Grade9Display && window.Grade9Display.toggleTheme) {
            window.Grade9Display.toggleTheme();
          } else {
            const current = document.documentElement.dataset.theme;
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.dataset.theme = next;
            try { localStorage.setItem('g9-theme', next); } catch (e) {}
          }
        });

        actions.append(searchBtn, themeBtn);

        const displayBtn = nav.querySelector('.g9-display-trigger-btn');
        if (displayBtn) {
          actions.appendChild(displayBtn);
        }

        header.appendChild(actions);
      }
    }
  }

  // 2. Global search dialog
  const dialog = document.createElement('dialog');
  dialog.className = 'g9-search-dialog';
  dialog.setAttribute('aria-labelledby', 'g9SearchTitle');

  const wrap = document.createElement('div');
  wrap.className = 'g9-search-wrap';

  const top=document.createElement('div');
  top.className = 'g9-search-top';

  const title = document.createElement('strong');
  title.id = 'g9SearchTitle';
  title.textContent = 'Search Grade9V3.5';

  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'site-icon-btn';
  close.textContent = '×';
  close.setAttribute('aria-label', 'Close search');
  close.addEventListener('click', () => dialog.close());

  top.append(title, close);

  const input = document.createElement('input');
  input.type = 'search';
  input.placeholder = 'Search pages, concepts, questions, or topics…';
  input.autocomplete = 'off';
  input.setAttribute('aria-label', 'Search Grade9V3');

  const hint = document.createElement('div');
  hint.className = 'g9-search-hint';
  hint.textContent = 'Tip: press Ctrl/⌘ K from anywhere to search.';

  const results = document.createElement('div');
  results.className = 'g9-search-results';
  results.setAttribute('aria-live', 'polite');

  wrap.append(top, input, hint, results);
  dialog.appendChild(wrap);

  if (document.body) {
    document.body.appendChild(dialog);
  } else {
    document.addEventListener('DOMContentLoaded', () => document.body.appendChild(dialog));
  }

  // 3. Search Data Loader
  let searchDataPromise = null;
  function loadSearchData() {
    if (searchDataPromise) return searchDataPromise;
    searchDataPromise = fetch(root + 'data/learner-search-index.v1.json')
      .then(res => {
        if (!res.ok) throw new Error('Search index fetch failed: ' + res.status);
        return res.json();
      })
      .catch(() => {
        // Fallback to question-bank-data.js if present
        return new Promise(resolve => {
          if (window.GRADE9_QUESTION_BANK) {
            resolve(mapQbData(window.GRADE9_QUESTION_BANK));
          } else {
            const s = document.createElement('script');
            s.src = root + 'data/question-bank-data.js';
            s.onload = () => resolve(mapQbData(window.GRADE9_QUESTION_BANK || {}));
            s.onerror = () => resolve([]);
            document.head.appendChild(s);
          }
        });
      });
    return searchDataPromise;
  }

  function mapQbData(qb) {
    const list = [];
    (qb.destinations || []).forEach(d => {
      list.push({
        id: d.path,
        title: d.title,
        url: d.path,
        type: 'PAGE',
        search_text: [d.title, d.kind, ...(d.keywords || [])].join(' ')
      });
    });
    (qb.questions || []).forEach(q => {
      list.push({
        id: q.id,
        title: (q.exam || '') + ' ' + (q.year || '') + ' - ' + (q.topic || ''),
        url: 'question-bank/index.html?q=' + encodeURIComponent(q.id),
        type: 'QUESTION',
        search_text: [q.id, q.subject, q.topic, q.stem].join(' ')
      });
    });
    return list;
  }

  function normalize(v) {
    return String(v || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  }

  function resultLink(titleText, subtitle, href, kind) {
    const a = document.createElement('a');
    a.className = 'g9-search-result';
    a.href = href;

    const main = document.createElement('span');
    main.className = 'g9-search-result-main';
    main.textContent = titleText;

    const sub = document.createElement('span');
    sub.className = 'g9-search-result-sub';
    sub.textContent = subtitle;

    const badge = document.createElement('span');
    badge.className = 'g9-search-result-kind';
    badge.textContent = kind || 'ITEM';

    a.append(main, sub, badge);
    return a;
  }

  async function renderSearch() {
    const term = normalize(input.value);
    results.replaceChildren();
    if (!term) {
      const p = document.createElement('p');
      p.className = 'g9-search-empty';
      p.textContent = 'Type to search the portal, concepts, and canonical Question Bank.';
      results.appendChild(p);
      return;
    }

    const data = await loadSearchData().catch(() => []);
    const tokens = term.split(/\s+/).filter(Boolean);

    const matched = (Array.isArray(data) ? data : []).filter(item => {
      const hay = normalize([item.title, item.id, item.search_text, item.type].join(' '));
      return tokens.every(t => hay.includes(t));
    }).slice(0, 10);

    if (matched.length === 0) {
      const p = document.createElement('p');
      p.className = 'g9-search-empty';
      p.textContent = 'No matching results found.';
      results.appendChild(p);
      return;
    }

    matched.forEach(item => {
      const itemUrl = item.url.startsWith('http') || item.url.startsWith('/') ? item.url : (root + item.url);
      const sub = item.search_text ? item.search_text.slice(0, 120) + '…' : (item.id || '');
      results.appendChild(resultLink(item.title || item.id, sub, itemUrl, item.type));
    });
  }

  let searchTimer = null;
  input.addEventListener('input', () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(renderSearch, 60);
  });

  function openSearch(e) {
    if (e && e.preventDefault) e.preventDefault();
    if (typeof dialog.showModal === 'function' && !dialog.open) {
      dialog.showModal();
    } else {
      dialog.setAttribute('open', '');
    }
    input.focus();
    renderSearch();
  }

  // 4. Bind universal triggers
  function bindTriggers() {
    initLegacyHeader();

    document.querySelectorAll('[data-g9-action="search"], .g9-search-trigger, .g9-search-btn').forEach(btn => {
      btn.onclick = openSearch;
    });

    document.querySelectorAll('[data-g9-action="theme"], .g9-theme-toggle').forEach(btn => {
      btn.onclick = (e) => {
        e.preventDefault();
        if (window.Grade9Display && window.Grade9Display.toggleTheme) {
          window.Grade9Display.toggleTheme();
        } else {
          const current = document.documentElement.dataset.theme;
          const next = current === 'dark' ? 'light' : 'dark';
          document.documentElement.dataset.theme = next;
          try { localStorage.setItem('g9-theme', next); } catch (err) {}
        }
      };
    });

    document.querySelectorAll('[data-g9-action="display"], .g9-display-btn').forEach(btn => {
      btn.onclick = (e) => {
        e.preventDefault();
        if (window.Grade9Display && window.Grade9Display.togglePopover) {
          window.Grade9Display.togglePopover();
        } else {
          const panel = document.querySelector('[data-g9-display-panel]');
          if (panel) panel.toggleAttribute('hidden');
        }
      };
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindTriggers);
  } else {
    bindTriggers();
  }

  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openSearch();
    }
    if (e.key === 'Escape' && dialog.open) {
      dialog.close();
    }
  });

  // Global API
  window.Grade9Header = {
    openSearch,
    closeSearch: () => dialog.close()
  };
})();
