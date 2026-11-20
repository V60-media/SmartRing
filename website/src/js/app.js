/* SeeMyHealth desktop prototype — router, overlays, accordion, tabs, cart, forms, typescale QC */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } }
  };

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
        el.scrollIntoView({ behavior: "smooth" });
        return;
      }
      name = hash === "" ? "home" : "not-found";
    }
    if (current !== pages[name]) {
      if (current) current.hidden = true;
      current = pages[name];
      current.hidden = false;
      window.scrollTo(0, 0);
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
    if ((e.metaKey || e.ctrlKey) && e.key === "\\") { e.preventDefault(); toggleTypescale(); }
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
  var kbd = $(".ts-switch kbd"); if (kbd && !/Mac|iP/.test(navigator.platform)) kbd.textContent = "Ctrl+\\";
  setTypescale(store.get("smh-typescale") || "figma");

  renderCart();
  route();
})();
