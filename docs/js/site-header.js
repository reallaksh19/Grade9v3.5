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

  function ensureTestLink() {
    const header = document.querySelector('header.g9-shell-header[data-site-test-entry]');
    const nav = header && header.querySelector('.g9-header-nav');
    if (!nav || nav.querySelector('a[data-site-test]')) return;
    const link = document.createElement('a');
    link.href = root+'test/index.html';
    link.className = 'test-link';
    link.setAttribute('data-site-test', '');
    link.textContent = 'TEST';
    nav.appendChild(link);
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

  const tabsContainer = document.createElement('div');
  tabsContainer.className = 'g9-search-tabs';
  tabsContainer.setAttribute('role', 'tablist');
  tabsContainer.hidden = true;

  const results = document.createElement('div');
  results.className = 'g9-search-results';
  results.setAttribute('aria-live', 'polite');

  wrap.append(top, input, hint, tabsContainer, results);
  dialog.appendChild(wrap);

  if (document.body) {
    document.body.appendChild(dialog);
  } else {
    document.addEventListener('DOMContentLoaded', () => document.body.appendChild(dialog));
  }

  // 3. Search Data Loader with robust multi-depth path resolution
  let searchDataPromise = null;
  function getCandidateSearchUrls() {
    let scriptRoot = (script && script.dataset.siteRoot);
    if (!scriptRoot && script && script.src) {
      try {
        const u = new URL(script.src, window.location.href);
        const idx = u.pathname.lastIndexOf('/js/');
        if (idx !== -1) {
          scriptRoot = u.pathname.slice(0, idx + 1);
        }
      } catch (e) {}
    }
    const prefix = scriptRoot || '';
    const candidates = [
      prefix + 'data/learner-search-index.v1.json',
      '/data/learner-search-index.v1.json',
      '../data/learner-search-index.v1.json',
      '../../data/learner-search-index.v1.json',
      'data/learner-search-index.v1.json'
    ];
    return Array.from(new Set(candidates));
  }

  function loadSearchData() {
    if (searchDataPromise) return searchDataPromise;
    const urls = getCandidateSearchUrls();

    async function tryFetch() {
      for (const u of urls) {
        try {
          const res = await fetch(u);
          if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) return data;
          }
        } catch (e) {}
      }
      throw new Error('All search index candidate URLs failed');
    }

    searchDataPromise = tryFetch()
      .catch((err) => {
        console.warn('Search index fetch failed, falling back to QB data:', err);
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
        url: 'question-bank/index.html?q=' + encodeURIComponent(q.id) + '#' + encodeURIComponent(q.id),
        type: 'QUESTION',
        search_text: [q.id, q.subject, q.topic, q.stem].join(' ')
      });
    });
    return list;
  }

  function normalize(v) {
    return String(v || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  }

  function getCategory(item) {
    if (item.category) return item.category;
    const t = String(item.type || '').toUpperCase();
    if (t === 'QUESTION') return 'question';
    if (t === 'TOPIC' || t === 'SUBTOPIC' || t === 'CONCEPT') return 'curriculum';
    if (t.includes('CORE_1A') || t.includes('CORE_2') || item.sub_type === 'CORE_1A' || item.sub_type === 'CORE_2' || (item.url && item.url.includes('12-7-tablet'))) return 'tablet';
    return 'tablet';
  }

  function getReadableKind(type) {
    const t = String(type || '').toUpperCase();
    if (t === 'EXPLORE_RESOURCE') return 'EXPLORER';
    if (t === 'LEARN_RESOURCE') return 'CORE STUDY';
    if (t === 'PRACTICE_RESOURCE') return 'PRACTICE';
    if (t === 'CONCEPT') return 'CONCEPT';
    if (t === 'QUESTION') return 'QUESTION';
    if (t === 'TOPIC') return 'TOPIC';
    if (t === 'SUBTOPIC') return 'SUBTOPIC';
    if (t === 'HINT' || t === 'RUNG') return 'HINT';
    return t || 'PAGE';
  }

  function scoreItem(item, tokens, term) {
    let score = 1000;
    const titleNorm = normalize(item.title);
    const idNorm = normalize(item.id);
    const textNorm = normalize(item.search_text);

    if (idNorm === term || item.id === term || item.id === 'Q-' + term || idNorm === 'q ' + term) score += 25000;
    else if (idNorm.includes(term)) score += 5000;

    if (titleNorm === term) score += 15000;
    else if (titleNorm.startsWith(term)) score += 6000;
    else if (tokens.every(tok => titleNorm.includes(tok))) score += 3000;
    else if (tokens.some(tok => titleNorm.includes(tok))) score += 1000;

    if (tokens.every(tok => textNorm.includes(tok))) score += 500;
    if (textNorm.includes(term)) score += 300;

    return score;
  }

  function resultLink(item, href) {
    const a = document.createElement('a');
    a.className = 'g9-search-result';
    a.href = href;
    if (item.target === '_blank') {
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
    }

    const main = document.createElement('span');
    main.className = 'g9-search-result-main';
    main.textContent = item.title || item.id;

    const sub = document.createElement('span');
    if (item.breadcrumb) {
      sub.className = 'g9-search-breadcrumb';
      sub.textContent = item.breadcrumb;
    } else {
      sub.className = 'g9-search-result-sub';
      sub.textContent = item.search_text ? item.search_text.slice(0, 110) + '…' : (item.id || '');
    }

    const badge = document.createElement('span');
    badge.className = 'g9-search-result-kind';
    const rawBadge = item.badge || getReadableKind(item.type);
    badge.textContent = rawBadge;

    const bNorm = rawBadge.toLowerCase();
    if (bNorm.includes('core 1a')) badge.classList.add('g9-badge-core1a');
    else if (bNorm.includes('core 2')) badge.classList.add('g9-badge-core2');
    else if (bNorm.includes('ncert')) badge.classList.add('g9-badge-ncert');
    else if (bNorm.includes('jee') || bNorm.includes('iit')) badge.classList.add('g9-badge-jee');
    else if (item.type === 'TOPIC' || item.type === 'SUBTOPIC') badge.classList.add('g9-badge-topic');

    a.append(main, sub, badge);
    return a;
  }

  let activeCategory = 'all';

  async function renderSearch() {
    const term = normalize(input.value);
    results.replaceChildren();
    if (!term) {
      tabsContainer.hidden = true;
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
      return tokens.every(t => {
        if (hay.includes(t)) return true;
        if (t.length >= 4) {
          const stem = t.slice(0, 4);
          if (hay.includes(stem)) return true;
        }
        return false;
      });
    });

    if (matched.length === 0) {
      tabsContainer.hidden = true;
      const p = document.createElement('p');
      p.className = 'g9-search-empty';
      p.textContent = 'No matching results found.';
      results.appendChild(p);
      return;
    }

    // Sort by relevance score
    matched.sort((a, b) => scoreItem(b, tokens, term) - scoreItem(a, tokens, term));

    let effectiveRoot = (script && script.dataset.siteRoot);
    if (!effectiveRoot && script && script.src) {
      try {
        const u = new URL(script.src, window.location.href);
        const idx = u.pathname.lastIndexOf('/js/');
        if (idx !== -1) {
          effectiveRoot = u.pathname.slice(0, idx + 1);
        }
      } catch (e) {}
    }
    effectiveRoot = effectiveRoot || '';

    // Calculate dynamic counts
    const countAll = matched.length;
    const countQuestions = matched.filter(m => getCategory(m) === 'question').length;
    const countTablets = matched.filter(m => getCategory(m) === 'tablet').length;
    const countCurriculum = matched.filter(m => getCategory(m) === 'curriculum').length;

    // Reset tab if current active has 0 results
    if (activeCategory === 'question' && countQuestions === 0) activeCategory = 'all';
    if (activeCategory === 'tablet' && countTablets === 0) activeCategory = 'all';
    if (activeCategory === 'curriculum' && countCurriculum === 0) activeCategory = 'all';

    // Render tabs
    tabsContainer.hidden = false;
    tabsContainer.replaceChildren();
    const tabDefs = [
      { id: 'all', label: 'All', count: countAll },
      { id: 'question', label: 'Questions', count: countQuestions },
      { id: 'tablet', label: 'Core 1A & 2 Tablets', count: countTablets },
      { id: 'curriculum', label: 'Topics & Concepts', count: countCurriculum },
    ];
    tabDefs.forEach(def => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'g9-search-tab' + (activeCategory === def.id ? ' active' : '');
      btn.setAttribute('role', 'tab');
      btn.setAttribute('aria-selected', String(activeCategory === def.id));

      const lbl = document.createElement('span');
      lbl.textContent = def.label;

      const badgeCount = document.createElement('span');
      badgeCount.className = 'g9-search-tab-count';
      badgeCount.textContent = String(def.count);

      btn.append(lbl, badgeCount);
      btn.addEventListener('click', () => {
        activeCategory = def.id;
        renderSearch();
      });
      tabsContainer.appendChild(btn);
    });

    const createBridge = () => {
      const bridge = document.createElement('a');
      bridge.className = 'g9-search-qb-bridge';
      bridge.href = effectiveRoot + 'question-bank/index.html?q=' + encodeURIComponent(input.value.trim());
      const leftText = document.createElement('span');
      leftText.textContent = `View all ${countQuestions} questions in Question Bank`;
      const rightArrow = document.createElement('span');
      rightArrow.textContent = '›';
      bridge.append(leftText, rightArrow);
      return bridge;
    };

    const renderCard = item => {
      let itemUrl = item.url || '';
      if (!itemUrl.startsWith('http') && !itemUrl.startsWith('/')) {
        itemUrl = effectiveRoot + itemUrl;
      }
      return resultLink(item, itemUrl);
    };

    if (activeCategory === 'all') {
      const tablets = matched.filter(m => getCategory(m) === 'tablet');
      const curriculum = matched.filter(m => getCategory(m) === 'curriculum');
      const questions = matched.filter(m => getCategory(m) === 'question');

      if (tablets.length) {
        const secHdr = document.createElement('div');
        secHdr.className = 'g9-search-section-header';
        secHdr.textContent = `📑 Core 1A & 2 Tablets (${tablets.length})`;
        results.appendChild(secHdr);
        tablets.slice(0, 6).forEach(item => results.appendChild(renderCard(item)));
      }

      if (curriculum.length) {
        const secHdr = document.createElement('div');
        secHdr.className = 'g9-search-section-header';
        secHdr.textContent = `📚 Topics & Concepts (${curriculum.length})`;
        results.appendChild(secHdr);
        curriculum.slice(0, 4).forEach(item => results.appendChild(renderCard(item)));
      }

      if (questions.length) {
        const secHdr = document.createElement('div');
        secHdr.className = 'g9-search-section-header';
        secHdr.textContent = `🎯 Questions in Question Bank (${questions.length})`;
        results.appendChild(secHdr);
        results.appendChild(createBridge());
        questions.slice(0, 8).forEach(item => results.appendChild(renderCard(item)));
      }
    } else if (activeCategory === 'question') {
      if (countQuestions > 0) results.appendChild(createBridge());
      const questions = matched.filter(m => getCategory(m) === 'question');
      questions.slice(0, 20).forEach(item => results.appendChild(renderCard(item)));
    } else if (activeCategory === 'tablet') {
      const tablets = matched.filter(m => getCategory(m) === 'tablet');
      tablets.slice(0, 20).forEach(item => results.appendChild(renderCard(item)));
    } else if (activeCategory === 'curriculum') {
      const curriculum = matched.filter(m => getCategory(m) === 'curriculum');
      curriculum.slice(0, 20).forEach(item => results.appendChild(renderCard(item)));
    }
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
    ensureTestLink();

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

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.g9-header-dropdown')) {
      document.querySelectorAll('.g9-header-dropdown[open]').forEach(d => d.removeAttribute('open'));
    }
  });

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
    if (e.key === 'Escape') {
      if (dialog.open) dialog.close();
      document.querySelectorAll('.g9-header-dropdown[open]').forEach(d => d.removeAttribute('open'));
    }
  });

  // Global API
  window.Grade9Header = {
    openSearch,
    closeSearch: () => dialog.close()
  };
})();
