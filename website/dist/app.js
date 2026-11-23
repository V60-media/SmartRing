/* SeeMyHealth desktop prototype — router, overlays, accordion, tabs, cart, forms, typescale QC */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } }
  };

  /* ---------------- Smooth scroll (Lenis) ---------------- */
  // Lenis eases the real window scroll, so sticky, scroll-timeline CSS and every scroll listener
  // below keep working unchanged. Skipped for reduced motion or if the CDN script didn't load.
  var lenis = null;
  if (window.Lenis && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    lenis = new window.Lenis({ lerp: 0.1, wheelMultiplier: 1, smoothWheel: true });
    (function raf(t) { lenis.raf(t); requestAnimationFrame(raf); })(performance.now());
    // scrollable panels inside overlays (cart, sizing, contact) keep their own native scroll
    $$(".overlay, .panel, .dev-panel").forEach(function (el) { el.setAttribute("data-lenis-prevent", ""); });
  }
  function scrollToY(y, opts) {                       // one entry point for programmatic scrolling
    opts = opts || {};
    if (lenis) lenis.scrollTo(y, { immediate: !!opts.immediate, force: true });
    else window.scrollTo({ top: typeof y === "number" ? y : y.getBoundingClientRect().top + window.scrollY, behavior: opts.immediate ? "auto" : "smooth" });
  }

  /* ---------------- Router (plain #name hashes) ---------------- */
  var pages = {};
  $$(".page").forEach(function (p) { pages[p.dataset.route] = p; });
  // hashes that open a page with a preselected tab
  var aliases = {
    "faq-general": ["faq", "general"], "faq-products": ["faq", "products"], "faq-app": ["faq", "app"],
    "faq-orders": ["faq", "orders"], "faq-warranty": ["faq", "warranty"]
  };
  var current = null;
  var overlayRoutes = { contact: "contact" };

  function route() {
    var hash = decodeURIComponent(location.hash.replace(/^#/, "")) || "home";
    if (overlayRoutes[hash]) {
      if (!current) { current = pages.home; current.hidden = false; }
      openOverlay(overlayRoutes[hash]);
      return;
    }
    var name = hash, tab = null;
    if (aliases[hash]) { name = aliases[hash][0]; tab = aliases[hash][1]; }
    var anchor = null;
    if (!pages[name]) {
      // in-page anchor on the current page?
      var el = document.getElementById(hash);
      var owner = el && el.closest(".page");
      if (owner) {
        if (current !== owner) { if (current) current.hidden = true; current = owner; current.hidden = false; }
        scrollToY(el);
        return;
      }
      name = hash === "" ? "home" : "not-found";
    }
    if (current !== pages[name]) {
      if (current) current.hidden = true;
      current = pages[name];
      current.hidden = false;
      scrollToY(0, { immediate: true });
    }
    if (tab) selectTab(current, tab);
    var meta = (window.ROUTE_META || {})[name] || {};
    if (meta.title) document.title = meta.title;
    var md = $('meta[name="description"]');
    if (md && meta.description) md.setAttribute("content", meta.description);
    $$(".site-nav__links a").forEach(function (a) {
      a.toggleAttribute("aria-current", false);
    });
    var navMatches = $$('.page:not([hidden]) .site-nav__links a[href="#' + name + '"]');
    if (navMatches.length === 1) navMatches[0].setAttribute("aria-current", "page");
    closeAll();
    if (anchor) anchor.scrollIntoView();
  }
  window.addEventListener("hashchange", route);

  /* ---------------- Overlays ---------------- */
  var lastFocus = null;
  function openOverlay(name) {
    var o = document.getElementById("overlay-" + name);
    if (!o) return;
    closeAll();
    lastFocus = document.activeElement;
    o.classList.add("is-open");
    o.setAttribute("aria-hidden", "false");
    document.body.classList.add("has-overlay");
    if (lenis) lenis.stop();                          // page underneath stays put while a panel is open
    var f = $("[autofocus], button, a, input", o.querySelector(".panel") || o);
    if (f) setTimeout(function () { f.focus(); }, 50);
    if (name === "video") { var v = $("video", o); if (v) { try { v.play(); } catch (e) {} } }
  }
  function closeAll() {
    if (overlayRoutes[location.hash.replace(/^#/, "")] && history.replaceState) {
      history.replaceState(null, "", "#" + (current ? current.dataset.route : "home"));
    }
    $$(".overlay.is-open").forEach(function (o) {
      o.classList.remove("is-open");
      o.setAttribute("aria-hidden", "true");
      var v = $("video", o); if (v) v.pause();
    });
    document.body.classList.remove("has-overlay");
    if (lenis) lenis.start();
    if (lastFocus && lastFocus.focus) { lastFocus.focus(); lastFocus = null; }
  }

  document.addEventListener("click", function (e) {
    var t = e.target;
    var opener = t.closest("[data-open]");
    if (opener) { e.preventDefault(); openOverlay(opener.dataset.open); return; }
    if (t.closest("[data-close]") || t.classList.contains("overlay")) { e.preventDefault(); closeAll(); return; }

    var acc = t.closest(".accordion__btn");
    if (acc) {
      var open = acc.getAttribute("aria-expanded") === "true";
      acc.setAttribute("aria-expanded", String(!open));
      return;
    }
    var tabBtn = t.closest("[role=tab]");
    if (tabBtn) { selectTab(tabBtn.closest("[data-tabs]"), tabBtn.dataset.tab); return; }

    var opt = t.closest("[data-option]");
    if (opt) {
      var group = opt.closest("[data-option-group]");
      $$("[data-option]", group).forEach(function (b) { b.setAttribute("aria-pressed", String(b === opt)); });
      var label = group && group.dataset.optionGroup && document.querySelector('[data-option-label="' + group.dataset.optionGroup + '"]');
      if (label) label.textContent = opt.dataset.option;
      return;
    }
    var qty = t.closest("[data-qty]");
    if (qty) { changeQty(qty.dataset.id, +qty.dataset.qty); return; }
    var add = t.closest("[data-add-to-cart]");
    if (add) { addToCart(add); return; }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeAll();
    if ((e.metaKey || e.ctrlKey) && e.key === "\\") { e.preventDefault(); toggleDevPanel(); }
  });

  /* ---------------- Tabs ---------------- */
  function selectTab(root, id) {
    if (!root) return;
    var scope = root.matches("[data-tabs]") ? root : $("[data-tabs]", root);
    if (!scope) return;
    $$("[role=tab]", scope).forEach(function (b) {
      var on = b.dataset.tab === id;
      b.setAttribute("aria-selected", String(on));
      b.tabIndex = on ? 0 : -1;
    });
    $$("[role=tabpanel]", scope).forEach(function (p) { p.hidden = p.dataset.tab !== id; });
  }

  /* ---------------- Cart ---------------- */
  var cart = store.get("smh-cart") || [];
  function money(n) { return "$" + n.toFixed(2).replace(/\.00$/, ""); }
  function addToCart(btn) {
    var scope = btn.closest("[data-product]");
    var variant = scope ? $$("[data-option][aria-pressed=true]", scope).map(function (b) { return b.dataset.option; }).join(" · ") : "";
    var id = btn.dataset.id + "|" + variant;
    var line = cart.filter(function (l) { return l.id === id; })[0];
    if (line) line.qty += 1;
    else cart.push({ id: id, name: btn.dataset.name, price: +btn.dataset.price, img: btn.dataset.img || "", variant: variant, qty: 1 });
    saveCart();
    openOverlay("cart");
  }
  function changeQty(id, d) {
    cart.forEach(function (l) { if (l.id === id) l.qty += d; });
    cart = cart.filter(function (l) { return l.qty > 0; });
    saveCart();
  }
  function saveCart() { store.set("smh-cart", cart); renderCart(); }
  function renderCart() {
    var count = cart.reduce(function (s, l) { return s + l.qty; }, 0);
    $$("[data-cart-count]").forEach(function (c) { c.textContent = count; c.hidden = count === 0; });
    var o = document.getElementById("overlay-cart");
    if (!o) return;
    $("[data-cart-empty]", o).hidden = count > 0;
    $("[data-cart-full]", o).hidden = count === 0;
    var list = $("[data-cart-lines]", o);
    var tpl = $("#tpl-cart-line");
    if (!list || !tpl) return;
    list.innerHTML = "";
    cart.forEach(function (l) {
      var n = tpl.content.cloneNode(true);
      $("[data-f=name]", n).textContent = l.name;
      $("[data-f=variant]", n).textContent = l.variant;
      $("[data-f=price]", n).textContent = money(l.price * l.qty);
      $("[data-f=qty]", n).textContent = l.qty;
      var img = $("[data-f=img]", n); if (img && l.img) img.src = l.img;
      $$("[data-qty]", n).forEach(function (b) { b.dataset.id = l.id; });
      list.appendChild(n);
    });
    var sub = cart.reduce(function (s, l) { return s + l.price * l.qty; }, 0);
    $$("[data-cart-heading-count]", o).forEach(function (el) { el.textContent = count ? " (" + count + ")" : ""; });
    $$("[data-cart-items]", o).forEach(function (el) { el.textContent = count; });
    $$("[data-cart-subtotal]", o).forEach(function (el) { el.textContent = money(sub); });
  }

  /* ---------------- Forms (no backend: validate + confirm in page) ---------------- */
  document.addEventListener("submit", function (e) {
    var form = e.target.closest("[data-form]");
    if (!form) return;
    e.preventDefault();
    var ok = true;
    $$("[required]", form).forEach(function (input) {
      var field = input.closest(".field");
      var valid = input.checkValidity();
      if (field) field.classList.toggle("is-invalid", !valid);
      if (!valid && ok) { input.focus(); }
      ok = ok && valid;
    });
    if (!ok) return;
    var done = $("[data-form-done]", form.parentNode);
    if (done) { form.hidden = true; done.hidden = false; }
  });

  /* ---------------- Typescale QC switch ---------------- */
  function setTypescale(v) {
    document.documentElement.dataset.typescale = v;
    $$("[data-typescale-set]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.typescaleSet === v)); });
    store.set("smh-typescale", v);
  }
  function toggleTypescale() { setTypescale(document.documentElement.dataset.typescale === "figma" ? "normalized" : "figma"); }
  $$("[data-typescale-set]").forEach(function (b) { b.addEventListener("click", function () { setTypescale(b.dataset.typescaleSet); }); });
  var kbd = $(".dev-panel kbd"); if (kbd && !/Mac|iP/.test(navigator.platform)) kbd.textContent = "Ctrl+\\";
  setTypescale(store.get("smh-typescale") || "figma");

  /* ---------------- Hero parallax: image scrolls at 80% of page speed ---------------- */
  var savedSpeed = parseFloat(store.get("smh-hero-speed")); var HERO_SPEED = (isNaN(savedSpeed) ? 80 : savedSpeed) / 100;
  var heroTicking = false;
  var HERO_NATIVE = window.CSS && CSS.supports("animation-timeline: scroll()");
  function updateHeroParallax() {
    heroTicking = false;
    var hero = $(".home-hero"), inner = $(".home-hero__sticky-inner");
    if (!hero || !inner) return;
    if (HERO_NATIVE) {
      // Compositor-driven: the browser moves the image in the same frame as the scroll, so there's
      // nothing for JS to catch up on (no jitter at any speed). JS only feeds in the numbers.
      var h = hero.offsetHeight, top0 = hero.getBoundingClientRect().top + window.scrollY;
      inner.style.position = "relative"; inner.style.top = ""; inner.style.transform = "";
      inner.style.animationRange = top0 + "px " + (top0 + h) + "px"; // vars aren't accepted here
      inner.style.setProperty("--par-shift", (h * (1 - HERO_SPEED)) + "px");
      inner.classList.add("is-native-parallax");
      return;
    }
    var d = Math.max(0, -hero.getBoundingClientRect().top);       // how far the hero has scrolled up
    var maxLag = Math.max(0, hero.offsetHeight - inner.offsetHeight); // how far sticky can travel natively
    // No clamp: the image keeps its parallax past the hero's bottom, and the next section
    // (higher z-index, opaque) slides over it instead of the image scrolling away.
    d = Math.min(d, hero.offsetHeight);                            // once the hero is fully covered, stop
    var desired = d * (1 - HERO_SPEED);                            // image top, relative to the hero
    // JS runs a frame after the browser scrolls, so whatever the transform corrects shows up as jitter.
    // Pick the base the browser moves natively that's closest to the target speed:
    //   speed < 50%  -> sticky (native 0%), JS corrects by d*speed
    //   speed >= 50% -> normal flow (native 100%), JS corrects by d*(1-speed)
    var sticky = HERO_SPEED < 0.5;
    inner.style.position = sticky ? "sticky" : "relative";
    inner.style.top = sticky ? "0" : "";
    var natural = sticky ? Math.min(d, maxLag) : 0;
    inner.style.transform = "translate3d(0," + (desired - natural) + "px,0)";
  }
  if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    if (!HERO_NATIVE) window.addEventListener("scroll", function () {
      if (!heroTicking) { heroTicking = true; requestAnimationFrame(updateHeroParallax); }
    }, { passive: true });
    window.addEventListener("resize", function () { requestAnimationFrame(updateHeroParallax); });
    window.addEventListener("hashchange", function () { requestAnimationFrame(updateHeroParallax); });
  }

  /* ---------------- Temp control panel (Cmd/Ctrl + \\) ---------------- */
  var devPanel = $(".dev-panel");
  function toggleDevPanel(force) {
    if (!devPanel) return;
    var show = typeof force === "boolean" ? force : devPanel.hidden;
    devPanel.hidden = !show;
    store.set("smh-dev-panel", show ? "1" : "0");
  }
  toggleDevPanel(store.get("smh-dev-panel") === "1");

  // Generic panel controls: each slider is built here, remembered per browser (key "smh-tune-<id>"),
  // and calls onChange(value) immediately and on every move. "Copy values" puts them all on the clipboard.
  var tuneValues = {};
  function panelGroup(title) {
    if (!devPanel) return;
    var g = document.createElement("div"); g.className = "dev-panel__group"; g.innerHTML = "<strong>" + title + "</strong>";
    devPanel.appendChild(g);
  }
  function panelSlider(id, label, min, max, step, def, onChange, fmt) {
    var saved = parseFloat(store.get("smh-tune-" + id)), v = isNaN(saved) ? def : saved;
    fmt = fmt || function (x) { return String(x); };
    tuneValues[id] = v;
    if (devPanel) {
      var row = document.createElement("label"); row.className = "dev-panel__row";
      row.innerHTML = label + ' <output></output><input type="range" min="' + min + '" max="' + max + '" step="' + step + '" value="' + v + '">';
      var input = row.querySelector("input"), out = row.querySelector("output");
      out.textContent = fmt(v);
      input.addEventListener("input", function () {
        v = +input.value; tuneValues[id] = v; out.textContent = fmt(v);
        store.set("smh-tune-" + id, String(v)); onChange(v);
      });
      row.addEventListener("dblclick", function () {          // double-click a row: back to default
        input.value = def; input.dispatchEvent(new Event("input"));
      });
      devPanel.appendChild(row);
    }
    onChange(v);
    return v;
  }
  if (devPanel) {
    var tuneBtns = document.createElement("div"); tuneBtns.className = "dev-panel__group";
    tuneBtns.innerHTML = '<span>Double-click a slider to reset</span><button type="button">Copy values</button>';
    tuneBtns.querySelector("button").addEventListener("click", function (e) {
      var txt = JSON.stringify(tuneValues, null, 1), btn = e.currentTarget;
      (navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).then(function () { btn.textContent = "Copied!"; }, function () { window.prompt("Copy these values:", txt); })
        .then(function () { setTimeout(function () { btn.textContent = "Copy values"; }, 1500); });
    });
    devPanel.appendChild(tuneBtns);
  }
  var pct = function (x) { return Math.round(x * 100) + "%"; };
  var scr = function (x) { return x + " screen"; };

  var speedInput = $("[data-hero-speed]"), speedOut = $("[data-hero-speed-out]");
  function setHeroSpeed(pct) {
    HERO_SPEED = pct / 100;
    if (speedInput) speedInput.value = pct;
    if (speedOut) speedOut.textContent = pct + "%";
    store.set("smh-hero-speed", String(pct)); tuneValues["hero-speed"] = pct / 100;
    updateHeroParallax();
  }
  if (speedInput) speedInput.addEventListener("input", function () { setHeroSpeed(+speedInput.value); });
  setHeroSpeed(Math.round(HERO_SPEED * 100));

  /* ---------------- Home showcase: scroll-driven product steps ---------------- */
  // The section is N×100svh tall with a sticky 100svh stage. Scroll progress through it picks
  // the active step (bg + copy + tab) and fills the active tab's progress bar.
  var showcase = $(".home-showcase");
  if (showcase) {
    var scBgs = $$(".home-showcase__bg", showcase), scCopies = $$(".home-showcase__copy", showcase);
    var scTabs = $$(".product-tabs li", showcase), scN = scCopies.length, scActive = 0, scTick = false;
    var scWrap = $(".home-showcase__bgs", showcase), SC_PAR = 0.25, SC_T = 0.5, SC_DRIFT = 8; // entry/exit parallax, wipe length (share of a step), drift per step (% of image)
    var scRefresh = function () { if (typeof updateShowcase === "function") updateShowcase(); };
    panelGroup("Product showcase");
    panelSlider("sc-par", "Bg parallax in/out", 0, 0.6, 0.05, 0.25, function (v) { SC_PAR = v; scRefresh(); }, pct);
    panelSlider("sc-drift", "Bg drift per product", 0, 16, 1, 8, function (v) { SC_DRIFT = v; scRefresh(); }, function (v) { return v + "%"; });
    panelSlider("sc-wipe", "Bg wipe length", 0.1, 1, 0.05, 0.5, function (v) { SC_T = v; scRefresh(); }, function (v) { return Math.round(v * 100) + "% of a step"; });
    var setStep = function (i) {
      if (i === scActive) return;
      var prev = scActive; scActive = i;
      scBgs.forEach(function (el, k) { el.classList.toggle("is-active", k === i); });
      var fwd = i > prev;
      scCopies.forEach(function (el, k) {
        var on = k === i;
        if (on) {
          // park the incoming lines on the side they enter from, without animating, then release
          el.classList.add("no-trans");
          el.classList.remove("is-leaving", "is-leaving-down");
          el.classList.toggle("from-above", !fwd);
          void el.offsetWidth;
          el.classList.remove("no-trans");
          el.classList.add("is-active");
        } else if (k === prev) {
          el.classList.remove("is-active", "from-above");
          el.classList.add(fwd ? "is-leaving" : "is-leaving-down");  // exits away from the scroll direction
        } else {
          el.classList.remove("is-active");
        }
        el.setAttribute("aria-hidden", on ? "false" : "true");
        $$("a", el).forEach(function (a) { if (on) a.removeAttribute("tabindex"); else a.setAttribute("tabindex", "-1"); });
      });
      scTabs.forEach(function (li, k) { li.classList.toggle("is-active", k === i); li.classList.toggle("is-done", k < i); });
    };
    var updateShowcase = function () {
      scTick = false;
      if (!showcase.offsetParent) return;                       // home page hidden
      var r = showcase.getBoundingClientRect(), range = r.height - window.innerHeight;
      var p = Math.min(1, Math.max(0, -r.top / Math.max(1, range))); // 0..1 through the pinned part
      var x = Math.min(scN - 0.0001, p * scN), i = Math.floor(x);
      setStep(i);
      if (scTabs[i]) scTabs[i].style.setProperty("--p", (x - i).toFixed(4));

      // The bg never stands still: there's always one parallax term moving with scroll.
      //  - entering:  the wrapper lags while the section comes up        (r.top > 0)
      //  - pinned:    each image drifts up through its own step (below)
      //  - leaving:   the wrapper lags again while the section scrolls off (r.bottom < vh)
      var vh = window.innerHeight;
      var enter = Math.min(vh, Math.max(0, r.top)), leave = Math.min(vh, Math.max(0, vh - r.bottom));
      if (scWrap) scWrap.style.transform = "translate3d(0," + (-SC_PAR * enter + SC_PAR * leave).toFixed(2) + "px,0)";
      // Continuous position (not clamped to steps) so the drift keeps going right to the end.
      var xc = Math.max(0, Math.min(scN, -r.top / Math.max(1, range) * scN));
      var reveal = scBgs.map(function (bg, k) { return k === 0 ? 1 : Math.min(1, Math.max(0, (xc - (k - SC_T / 2)) / SC_T)); });
      scBgs.forEach(function (bg, k) {
        var t = reveal[k];
        if (k > 0) bg.style.clipPath = "inset(" + ((1 - t) * 100).toFixed(3) + "% 0 0 0)";
        // u: where this image is in its own life, -0.5 (starting to wipe in) .. 1.5 (fully covered).
        var u = Math.max(-0.5, Math.min(1.5, xc - k));
        var y = 6 - u * SC_DRIFT;                                   // keeps sliding up the whole time
        var sc = 1.12 - (t * 0.04);                                 // slight settle as it lands
        bg.style.transform = "translate3d(0," + y.toFixed(3) + "%,0) scale(" + sc.toFixed(4) + ")";
      });
    };
    window.addEventListener("scroll", function () { if (!scTick) { scTick = true; requestAnimationFrame(updateShowcase); } }, { passive: true });
    window.addEventListener("resize", updateShowcase);
    // Tabs jump to their step instead of navigating away.
    scTabs.forEach(function (li, k) {
      var a = $("a", li); if (!a) return;
      a.addEventListener("click", function (e) {
        e.preventDefault();
        var range = showcase.offsetHeight - window.innerHeight;
        var top = showcase.getBoundingClientRect().top + window.scrollY + range * (k + 0.02) / scN;
        scrollToY(top);
      });
    });
    // Split each heading into clip lines (after webfonts load; again on resize so breaks stay right).
    var splitShowcase = function () {
      scCopies.forEach(function (el) {
        var h = $("h2", el); if (!h) return;
        if (!h.dataset.text) h.dataset.text = h.textContent.trim();
        h.textContent = h.dataset.text;
        splitLines(h).forEach(function (s, n) { s.style.setProperty("--i", n); });
      });
    };
    var scResizeT = null;
    window.addEventListener("resize", function () { clearTimeout(scResizeT); scResizeT = setTimeout(splitShowcase, 150); });
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(splitShowcase, splitShowcase);
    updateShowcase();
  }

  /* ---------------- Home benefits: tiles arrive one by one, each at its own speed ---------------- */
  var benefits = $(".home-benefits");
  if (benefits) {
    var rem = function () { return parseFloat(getComputedStyle(document.documentElement).fontSize) || 16; };
    // Timeline in screens (s = how many viewport heights the section has scrolled):
    //   0-1  showcase lifts off (garage door) - point 1 underneath;  then a point every L screens
    // Photos float past in the side lanes like ordinary content, but each at its own speed:
    //   at    = when its top crosses the bottom edge (screens), spaced so they come one at a time
    //   speed = multiple of scroll speed (>1 feels closer, <1 further away); "spread" scales the difference
    var KB = [
      { sel: ".kb-tile--d", speed: 1.00 },   // hands, left
      { sel: ".kb-tile--e", speed: 1.30 },   // notebook, left
      { sel: ".kb-tile--c", speed: 0.80 },   // headphones, right
      { sel: ".kb-tile--b", speed: 1.15 },   // woman, right
      { sel: ".kb-tile--a", speed: 0.90 }    // ring close-up, left
    ].map(function (o) { o.el = $(o.sel, benefits); o.at = 0; return o; }).filter(function (o) { return o.el; });
    var KB_SWITCH = [1.5, 2.5], KB_CENTRE = [1, 2, 3];   // point switches; where each point sits dead centre
    var KB_SPREAD = 1, kbFirst = 0.2, kbGap = 0.55;
    var kbRefresh = function () { if (typeof updateBenefits === "function") updateBenefits(); };
    var kbRetime = function () { KB.forEach(function (o, n) { o.at = kbFirst + n * kbGap; }); kbRefresh(); };
    // point length L (screens): point 1 centred at 1 (right as the showcase finishes lifting), then every L
    var kbSetLength = function (L) {
      KB_CENTRE = [1, 1 + L, 1 + 2 * L];
      KB_SWITCH = [1 + L / 2, 1 + 1.5 * L];
      benefits.style.height = ((1 + 2.5 * L) + 1) * 100 + "svh";   // pinned until the last point has had its share
      kbRefresh();
    };
    panelGroup("Early Risk Detection");
    var kbTextRow = $("[data-kb-speed]"); if (kbTextRow && devPanel) devPanel.appendChild(kbTextRow.closest("label"));   // existing text-rise slider joins this group
    panelSlider("kb-len", "Screens per point", 0.5, 2, 0.1, 1, kbSetLength, scr);
    panelSlider("kb-first2", "First photo enters at", 0, 1.5, 0.05, 0.2, function (v) { kbFirst = v; kbRetime(); }, scr);
    panelSlider("kb-gap2", "Gap between photos", 0.1, 1.2, 0.05, 0.55, function (v) { kbGap = v; kbRetime(); }, scr);
    panelSlider("kb-spread", "Photo speed difference", 0, 2, 0.1, 1, function (v) { KB_SPREAD = v; kbRefresh(); }, function (v) { return v.toFixed(1) + "\u00d7"; });
    var kbTick = false, kbCopy = $(".kb-copy", benefits), kbPoints = $$(".kb-point", benefits), kbActive = 0;
    // Same line-clip swap as the showcase copy (CSS is shared): old lines exit, then new lines rise.
    var kbSetPoint = function (i) {
      if (i === kbActive) return;
      var prev = kbActive, fwd = i > prev; kbActive = i;
      kbPoints.forEach(function (el, k) {
        if (k === i) {
          el.classList.add("no-trans"); el.classList.remove("is-leaving", "is-leaving-down");
          el.classList.toggle("from-above", !fwd); void el.offsetWidth;
          el.classList.remove("no-trans"); el.classList.add("is-active");
        } else if (k === prev) {
          el.classList.remove("is-active", "from-above"); el.classList.add(fwd ? "is-leaving" : "is-leaving-down");
        } else el.classList.remove("is-active");
        el.setAttribute("aria-hidden", k === i ? "false" : "true");
      });
    };
    var kbSplit = function () {
      kbPoints.forEach(function (el) {
        var h = $("h2", el); if (!h) return;
        if (!h.dataset.text) h.dataset.text = h.textContent.trim();
        h.textContent = h.dataset.text;
        splitLines(h).forEach(function (s, n) { s.style.setProperty("--i", n); });
      });
    };
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(kbSplit, kbSplit);
    var kbResizeT = null;
    window.addEventListener("resize", function () { clearTimeout(kbResizeT); kbResizeT = setTimeout(kbSplit, 150); });
    // Centred copy rises slowly: KB_TEXT of the scroll distance (control panel slider, stored per browser).
    var kbSaved = parseFloat(store.get("smh-kb-speed")), KB_TEXT = (isNaN(kbSaved) ? 15 : kbSaved) / 100;
    var kbIn = $("[data-kb-speed]"), kbOut = $("[data-kb-speed-out]");
    var setKbSpeed = function (pct) {
      KB_TEXT = pct / 100;
      if (kbIn) kbIn.value = pct;
      if (kbOut) kbOut.textContent = pct + "%";
      store.set("smh-kb-speed", String(pct)); tuneValues["kb-text-rise"] = pct / 100;
      updateBenefits();
    };
    if (kbIn) kbIn.addEventListener("input", function () { setKbSpeed(+kbIn.value); });
    var updateBenefits = function () {
      kbTick = false;
      if (!benefits.offsetParent) return;
      var r = benefits.getBoundingClientRect(), vh = window.innerHeight;
      var s = -r.top / vh, u = rem();
      var i = s < KB_SWITCH[0] ? 0 : s < KB_SWITCH[1] ? 1 : 2;
      kbSetPoint(i);
      // Each point rises slowly through its own screen and is dead centre at its KB_CENTRE.
      if (kbCopy) kbCopy.style.transform = "translate3d(0, calc(-50% + " + (-KB_TEXT * (s - KB_CENTRE[i]) * vh).toFixed(1) + "px), 0)";
      KB.forEach(function (o) {
        var sp = 1 + (o.speed - 1) * KB_SPREAD;                         // 1 = moves exactly with the page
        var y = vh * 1.02 - (s - o.at) * sp * vh;                       // below the screen until `at`, then rises at its speed
        o.el.style.transform = "translate3d(0," + y.toFixed(1) + "px,0)";
      });
    };
    // With Lenis, update in the same frame Lenis moves the page (no one-frame lag on the floating photos).
    if (lenis) lenis.on("scroll", updateBenefits);
    else window.addEventListener("scroll", function () { if (!kbTick) { kbTick = true; requestAnimationFrame(updateBenefits); } }, { passive: true });
    window.addEventListener("resize", updateBenefits);
    setKbSpeed(Math.round(KB_TEXT * 100));
  }

  /* ---------------- Decode Your Health: 6-article slider ---------------- */
  // Arrows, dots and the small thumb (which previews the next article) all move one index;
  // slides, thumbs, dots and the 01—06 counter are kept in step. Wraps around at both ends.
  $$(".home-tracking[data-slider]").forEach(function (sec) {
    var slides = $$(".home-tracking__slide", sec), thumbs = $$("[data-thumb]", sec), dots = $$("[data-dot]", sec);
    var count = $("[data-count]", sec), n = slides.length, cur = 0;
    if (!n) return;
    var go = function (i) {
      cur = (i + n) % n; pendingNext = false;
      slides.forEach(function (el, k) {
        var on = k === cur, was = el.classList.contains("is-active");
        if (on && !was) {                                   // park incoming lines below without animating, then release
          el.classList.add("no-trans"); el.classList.remove("is-leaving"); void el.offsetWidth; el.classList.remove("no-trans");
        }
        el.classList.toggle("is-active", on);
        el.classList.toggle("is-leaving", !on && was);      // outgoing lines exit upward
        if (!on && !was) el.classList.remove("is-leaving");
        el.setAttribute("aria-hidden", on ? "false" : "true");
      });
      thumbs.forEach(function (el, k) { el.classList.toggle("is-active", k === cur); });
      dots.forEach(function (el, k) {
        el.classList.remove("is-active"); void el.offsetWidth;      // re-trigger the ring animation from 0
        el.classList.toggle("is-active", k === cur); el.setAttribute("aria-current", k === cur ? "true" : "false");
      });
      if (count) count.textContent = String(cur + 1).padStart(2, "0");
    };
    // Autoplay: the active dot's ring animation is the timer; when it finishes, move on.
    // Clicking restarts it (the ring re-runs because the class is re-applied). Paused while the
    // pointer is over the slider or the section is off-screen.
    var TRACK_DUR = 6;                                   // seconds per article
    sec.style.setProperty("--track-dur", TRACK_DUR + "s");
    var TRACK_HOLD = 400, pendingNext = false;           // ms the closed ring stays visible before the next article
    dots.forEach(function (d) {
      d.addEventListener("animationend", function (e) {
        if (e.animationName !== "track-ring" || !d.classList.contains("is-active")) return;
        var at = cur;                                     // hold the fully closed ring for a beat, then advance
        setTimeout(function () { if (cur === at && !sec.classList.contains("is-paused")) go(cur + 1); else if (cur === at) pendingNext = true; }, TRACK_HOLD);
      });
    });
    var hover = false, visible = false;
    var setPaused = function () {
      sec.classList.toggle("is-paused", hover || !visible);
      if (pendingNext && !hover && visible) { pendingNext = false; go(cur + 1); }   // ring had closed while paused
    };
    [$(".home-tracking__card", sec), $(".home-tracking__thumb", sec), $(".slider-arrows", sec), $(".home-tracking__dots", sec)].forEach(function (el) {
      if (!el) return;
      el.addEventListener("mouseenter", function () { hover = true; setPaused(); });
      el.addEventListener("mouseleave", function () { hover = false; setPaused(); });
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { visible = en[0].isIntersecting; setPaused(); }, { threshold: 0.35 }).observe($(".home-tracking__card", sec) || sec);
    } else visible = true;
    setPaused();
    // Split each slide's heading and paragraph into clip lines (after fonts load; again on resize).
    var splitTrack = function () {
      slides.forEach(function (sl) {
        $$(".t-h6, .t-body", sl).forEach(function (el) {
          if (!el.dataset.text) el.dataset.text = el.textContent.trim();
          el.textContent = el.dataset.text;
          splitLines(el).forEach(function (s, n) { s.style.setProperty("--i", n); });
        });
      });
    };
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(splitTrack, splitTrack);
    var trackResizeT = null;
    window.addEventListener("resize", function () { clearTimeout(trackResizeT); trackResizeT = setTimeout(splitTrack, 150); });
    $$("[data-next]", sec).forEach(function (b) { b.addEventListener("click", function () { go(cur + 1); }); });
    $$("[data-prev]", sec).forEach(function (b) { b.addEventListener("click", function () { go(cur - 1); }); });
    dots.forEach(function (b, k) { b.addEventListener("click", function () { go(k); }); });
    go(0);
  });

  /* ---------------- Heading reveal on scroll (same motion as the hero heading) ---------------- */
  // Only H1s (one per page) rise line by line inside a clip when they scroll into view. Lines are
  // split at reveal time and the plain text is put back afterwards, so later resizes re-wrap normally.
  var REVEAL_SEL = "h1";
  var REVEAL_SKIP = ".home-hero h1, .stat-card, .kb-copy, .home-showcase__copy, .overlay, .panel, .ts-switch, .dev-panel, .site-nav, .site-footer";
  function revealHeading(el) {
    var plain = el.textContent;
    var spans = splitLines(el);
    el.classList.remove("reveal-wait");
    el.classList.add("reveal-ready");
    spans.forEach(function (s, i) { s.style.setProperty("--intro-delay", i * 110 + "ms"); });
    requestAnimationFrame(function () { requestAnimationFrame(function () { el.classList.add("reveal-play"); }); });
    setTimeout(function () {                                     // done: back to plain text
      el.textContent = plain.trim(); el.removeAttribute("aria-label");
      el.classList.remove("reveal-ready", "reveal-play", "is-split");
    }, 1100 + spans.length * 110 + 100);
  }
  function initHeadingReveal() {
    if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        revealHeading(en.target);
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.01 });
    $$(REVEAL_SEL).forEach(function (el) {
      if (el.closest(REVEAL_SKIP) || el.children.length || !el.textContent.trim()) return; // only plain-text headings
      el.classList.add("reveal-wait");
      io.observe(el);
    });
  }

  if (devPanel && tuneBtns) devPanel.appendChild(tuneBtns);              // copy/reset row goes last
  renderCart();
  route();
  updateHeroParallax();
  playIntro();
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(initHeadingReveal, initHeadingReveal);

  /* ---------------- Entrance intro (home, first load) ---------------- */
  // Wrap each rendered line of a heading in a clip window so it can rise from below.
  function splitLines(el) {
    var words = el.textContent.trim().split(/\s+/);
    el.innerHTML = words.map(function (w) { return '<span class="intro-w">' + w + "</span>"; }).join(" ");
    var lines = [], lastTop = null;
    $$(".intro-w", el).forEach(function (w) {
      var t = w.offsetTop;
      if (t !== lastTop) { lines.push([]); lastTop = t; }
      lines[lines.length - 1].push(w.textContent);
    });
    el.setAttribute("aria-label", words.join(" ")); el.classList.add("is-split");
    el.innerHTML = lines.map(function (l) {
      return '<span class="intro-line" aria-hidden="true"><span>' + l.join(" ") + "</span></span>";
    }).join("");
    return $$(".intro-line > span", el);
  }
  function playIntro() {
    var root = document.documentElement;
    if (!root.classList.contains("intro-pending")) return;
    var page = $("#main-home"); if (!page) { root.classList.remove("intro-pending"); return; }
    var nav = $(".site-nav", page.closest(".page") || document) || $(".site-nav");
    var at = function (el, kind, ms) { if (el) { el.setAttribute("data-intro", kind); el.style.setProperty("--intro-delay", ms + "ms"); } };

    // Navbar drops from above, middle out: the two centre links, then the outer links, then logo + cart.
    var STEP = 80;                                                  // overlap: each starts long before the last ends
    var links = nav ? $$(".site-nav__links li", nav) : [];
    var mid = (links.length - 1) / 2;
    links.forEach(function (li, i) { at(li, "down", Math.floor(Math.abs(i - mid)) * STEP); });
    var ring = Math.floor(mid) + 1;                                 // one step after the outermost links
    at(nav && $(".site-nav__logo", nav), "down", ring * STEP);
    at(nav && $(".site-nav__cart", nav), "down", ring * STEP);

    // Hero: heading lines rise inside their clip, then the rest follows.
    var h1 = $(".home-hero h1"), t = 250;
    at($(".home-hero__lede"), "up", t + 350);
    at($(".home-hero__cta"), "up", t + 450);
    at($(".home-hero__product"), "up", t + 600);
    at($(".home-hero__sticky-inner img"), "fade", 0);

    var go = function () {
      // split after webfonts load, so line breaks match what's finally rendered
      if (h1) splitLines(h1).forEach(function (s, i) { s.style.setProperty("--intro-delay", (t + i * 110) + "ms"); });
      requestAnimationFrame(function () {
        root.classList.add("intro-play");
        requestAnimationFrame(function () { root.classList.remove("intro-pending"); });
        setTimeout(function () { root.classList.remove("intro-play"); }, 2500); // drop transitions so hover etc. behave
      });
    };
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(go, go);
  }
})();
