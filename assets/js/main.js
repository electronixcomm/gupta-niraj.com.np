// Mobile nav toggle
(function () {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open);
    });
    nav.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => nav.classList.remove('open'));
    });
  }
})();

// Tabs (subject pages)
(function () {
  document.querySelectorAll('[data-tabs]').forEach(group => {
    const tabs = group.querySelectorAll('.tab');
    const panels = group.querySelectorAll('.tabpanel');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const target = tab.dataset.tab;
        tabs.forEach(t => t.classList.toggle('active', t === tab));
        panels.forEach(p => p.classList.toggle('active', p.dataset.panel === target));
        // update URL hash without scroll jump
        history.replaceState(null, '', '#' + target);
      });
    });
    // open via hash
    const hash = location.hash.replace('#', '');
    if (hash) {
      const match = group.querySelector(`.tab[data-tab="${hash}"]`);
      if (match) match.click();
    }
  });
})();

// Q&A accordion
(function () {
  document.querySelectorAll('.qa-q').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('.qa-item').classList.toggle('open');
    });
  });
})();

// MCQ reveal
(function () {
  document.querySelectorAll('.mcq').forEach(mcq => {
    const opts = mcq.querySelectorAll('.mcq-options li');
    opts.forEach(opt => {
      opt.addEventListener('click', () => {
        if (mcq.classList.contains('show-answer')) return;
        opts.forEach(o => {
          if (o.dataset.correct === 'true') o.classList.add('correct');
          else if (o === opt) o.classList.add('wrong');
        });
        mcq.classList.add('show-answer');
      });
    });
  });
})();

// Subject filter chips (teaching hub)
(function () {
  const chips = document.querySelectorAll('.filter-bar .chip');
  const cards = document.querySelectorAll('[data-types]');
  if (!chips.length || !cards.length) return;
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.toggle('active', c === chip));
      const filter = chip.dataset.filter;
      cards.forEach(card => {
        const types = (card.dataset.types || '').split(',');
        card.style.display = (filter === 'all' || types.includes(filter)) ? '' : 'none';
      });
    });
  });
})();

// Reveal-on-scroll
(function () {
  if (!('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in-view'); io.unobserve(e.target); }
    });
  }, { threshold: .12 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
})();

// Set active nav based on current page
(function () {
  const path = location.pathname.replace(/\/$/, '');
  document.querySelectorAll('.nav a').forEach(a => {
    const href = a.getAttribute('href');
    if (!href || href.startsWith('#')) return;
    const aPath = new URL(href, location.origin + location.pathname).pathname.replace(/\/$/, '');
    if (aPath === path) a.style.color = 'var(--navy-900)';
  });
})();
