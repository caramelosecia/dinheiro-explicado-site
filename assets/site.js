(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return [].slice.call((c || document).querySelectorAll(s)); };
  var calmo = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* menu do celular */
  var bm = $(".btn-menu"), menu = $("#menu");
  if (bm && menu) bm.addEventListener("click", function () {
    var a = menu.classList.toggle("aberto");
    bm.setAttribute("aria-expanded", a);
    document.body.classList.toggle("menu-aberto", a);
  });

  /* menu Assuntos */
  $$(".drop").forEach(function (d) {
    var b = $(".drop-btn", d);
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      var a = d.classList.toggle("aberto");
      b.setAttribute("aria-expanded", a);
    });
  });
  document.addEventListener("click", function (e) {
    $$(".drop.aberto").forEach(function (d) { if (!d.contains(e.target)) { d.classList.remove("aberto"); $(".drop-btn", d).setAttribute("aria-expanded", false); } });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") $$(".drop.aberto").forEach(function (d) { d.classList.remove("aberto"); $(".drop-btn", d).setAttribute("aria-expanded", false); });
  });

  /* topo encolhe, progresso de leitura e voltar ao topo */
  var topo = $(".topo"), prog = $(".progresso i"), sobe = $(".ir-topo"), art = $("article .texto");
  function rolar() {
    var y = window.scrollY || 0;
    if (topo) topo.classList.toggle("rolou", y > 40);
    if (sobe) sobe.classList.toggle("mostra", y > 900);
    if (prog && art) {
      var r = art.getBoundingClientRect(), total = r.height - window.innerHeight * 0.6;
      prog.style.transform = "scaleX(" + Math.min(1, Math.max(0, -r.top / (total || 1))) + ")";
    }
  }
  window.addEventListener("scroll", rolar, { passive: true }); rolar();
  if (sobe) sobe.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: calmo ? "auto" : "smooth" }); });

  /* aparecer ao rolar */
  var els = $$(".revela");
  if ("IntersectionObserver" in window && !calmo) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("visivel"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    els.forEach(function (el, i) { el.style.transitionDelay = (i % 3) * 70 + "ms"; io.observe(el); });
  } else els.forEach(function (el) { el.classList.add("visivel"); });

  /* página de artigos: filtro e busca */
  var lista = $("#lista");
  if (lista) {
    var bt = $$(".filtros button"), cs = $$("#lista .card"), q = $("#busca"), f = "", cont = $(".contagem");
    var norm = function (s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };
    function ap() {
      var t = norm(q.value.trim()), n = 0;
      cs.forEach(function (c) {
        var ok = (!f || c.dataset.assunto === f) && (!t || norm(c.dataset.busca).indexOf(t) > -1);
        c.hidden = !ok; if (ok) { n++; c.classList.add("visivel"); }
      });
      $("#nada").hidden = n > 0;
      if (cont) cont.textContent = (t || f) ? n + (n === 1 ? " artigo encontrado" : " artigos encontrados") : "";
    }
    function sel(v) { f = v; bt.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.f === v); }); ap(); }
    bt.forEach(function (b) { b.addEventListener("click", function () { sel(b.dataset.f); }); });
    q.addEventListener("input", ap);
    var ps = new URLSearchParams(location.search), pa = ps.get("assunto");
    if (ps.get("q")) q.value = ps.get("q");
    sel(pa && bt.some(function (b) { return b.dataset.f === pa; }) ? pa : "");
    if (location.hash === "#busca") setTimeout(function () { q.focus(); }, 50);
  }

  /* compartilhar */
  var w = $("[data-whats]");
  if (w) w.href = "https://wa.me/?text=" + encodeURIComponent(document.title.split(" | ")[0] + " " + location.href);
  var cp = $("[data-copiar]");
  if (cp) cp.addEventListener("click", function () {
    var ok = function () { $("span", cp).textContent = "Link copiado!"; cp.classList.add("ok"); setTimeout(function () { $("span", cp).textContent = "Copiar link"; cp.classList.remove("ok"); }, 2200); };
    try { navigator.clipboard.writeText(location.href).then(ok, function () {}); } catch (e) {}
  });

  /* calculadoras */
  var brl = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
  function num(v) {
    v = String(v || "").trim().replace(/[^\d,.-]/g, "");
    if (v.indexOf(",") > -1) v = v.replace(/\./g, "").replace(",", ".");
    var n = parseFloat(v); return isFinite(n) ? n : 0;
  }
  function pmt(pv, i, n) { return i > 0 ? pv * i / (1 - Math.pow(1 + i, -n)) : pv / n; }
  function anima(el, alvo) {
    if (!el) return;
    if (calmo) { el.textContent = brl.format(alvo); return; }
    var ini = el._v || 0, t0 = null;
    el._v = alvo;
    function passo(t) {
      if (!t0) t0 = t;
      var k = Math.min(1, (t - t0) / 450), e = 1 - Math.pow(1 - k, 3);
      el.textContent = brl.format(ini + (alvo - ini) * e);
      if (k < 1) requestAnimationFrame(passo);
    }
    requestAnimationFrame(passo);
  }
  $$("form.calc").forEach(function (fm) {
    var tipo = fm.dataset.calc, R = function (k) { return $('[data-r="' + k + '"]', fm); };
    function calc() {
      if (tipo === "renda") {
        var d = num(fm.divida.value), m = Math.max(1, Math.round(num(fm.meses.value))), j = num(fm.juros.value) / 100;
        var p = d > 0 ? pmt(d, j, m) : 0;
        anima(R("mes"), p); anima(R("semana"), p * 12 / 52); anima(R("dia"), p / 22); anima(R("total"), p * m);
      } else {
        var v = num(fm.valor.value), t = num(fm.taxa.value) / 100, n = Math.max(1, Math.round(num(fm.parcelas.value)));
        var pc = v > 0 ? pmt(v, t, n) : 0, tot = pc * n, ju = Math.max(0, tot - v);
        anima(R("parcela"), pc); anima(R("total"), tot); anima(R("juros"), ju);
        R("pct").textContent = v > 0 ? Math.round(ju / v * 100) + "%" : "—";
        R("barra").style.width = (tot > 0 ? ju / tot * 100 : 0) + "%";
      }
    }
    fm.addEventListener("input", calc);
    fm.addEventListener("submit", function (e) { e.preventDefault(); calc(); });
    $$("input[inputmode=decimal]", fm).forEach(function (i) {
      i.addEventListener("blur", function () {
        var n = num(i.value);
        if (i.name === "divida" || i.name === "valor") i.value = n.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      });
    });
    calc();
  });
})();
