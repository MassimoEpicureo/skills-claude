/* Rack3D — rendu three.js (r147, scripts classiques) de l'implantation. Unités : m. X = plan X, Z = plan Y, Y = hauteur. */
window.Rack3D = (function () {
  function css(name, fb) {
    var v = getComputedStyle(document.documentElement).getPropertyValue('--' + name).trim();
    if (!v) return fb;
    if (/^#[0-9a-f]{8}$/i.test(v)) v = v.slice(0, 7);
    return v;
  }
  function mount(el, D, opt) {
    opt = opt || {};
    var T = window.THREE, k = 0.001;
    var W = el.clientWidth || 960, H = el.clientHeight || 600;
    var R = new T.WebGLRenderer({ antialias: true, preserveDrawingBuffer: !!opt.preserve });
    R.setPixelRatio(opt.dpr || Math.min(2, window.devicePixelRatio || 1));
    R.setSize(W, H);
    el.appendChild(R.domElement);
    var S = new T.Scene();
    var C = new T.PerspectiveCamera(38, W / H, 0.1, 600);
    var ctl = T.OrbitControls ? new T.OrbitControls(C, R.domElement) : null;
    S.add(new T.HemisphereLight(0xffffff, 0x8a8f99, 0.85));
    var sun = new T.DirectionalLight(0xffffff, 0.75); sun.position.set(-30, 60, 20); S.add(sun);
    var fill = new T.DirectionalLight(0xffffff, 0.25); fill.position.set(40, 20, -30); S.add(fill);

    var colors = {};
    function mat(c, extra) { return new T.MeshLambertMaterial(Object.assign({ color: new T.Color(c) }, extra || {})); }
    var box = new T.BoxGeometry(1, 1, 1);
    var M = new T.Matrix4(), Q = new T.Quaternion(), P = new T.Vector3(), Sc = new T.Vector3();
    function inst(list, material, name) {
      var m = new T.InstancedMesh(box, material, Math.max(1, list.length));
      list.forEach(function (b, i) { P.set(b[0], b[1], b[2]); Sc.set(b[3], b[4], b[5]); M.compose(P, Q, Sc); m.setMatrixAt(i, M); });
      m.count = list.length; m.name = name || ''; S.add(m); return m;
    }
    var ex = D.ext[0] * k, ez = D.ext[1] * k;
    var mats = {};
    function themed() {
      S.background = new T.Color(css('paper', '#f6f5f1'));
      floor.material.color.set(css('aisle-floor', '#e9e6de'));
      Object.keys(mats).forEach(function (key) { mats[key].m.color.set(css(mats[key].t, mats[key].f)); });
      draw();
    }
    function tm(token, fb, extra) { var m = mat(css(token, fb), extra); mats[token + Object.keys(mats).length] = { m: m, t: token, f: fb }; return m; }

    var floor = new T.Mesh(new T.PlaneGeometry(ex + 12, ez + 12), mat('#e9e6de'));
    floor.rotation.x = -Math.PI / 2; floor.position.set(ex / 2 - 2, 0, ez / 2); S.add(floor);
    // mur ouest
    inst([[-0.15, 3, ez / 2, 0.3, 6, ez + 6]], mat('#c9c6bf'), 'mur');

    // échelles : 2 fûts + treillis
    var posts = [], postsH = [], lines = [];
    D.frames.forEach(function (f) {
      var x = f[0] * k, z = f[1] * k + 0.04, h = f[2] * k, tall = f[2] >= D.H_RIVE;
      [x + 0.04, x + D.DEPTH * k - 0.04].forEach(function (px) { (tall ? postsH : posts).push([px, h / 2, z, 0.08, h, 0.07]); });
      var a = x + 0.06, b = x + D.DEPTH * k - 0.06, step = 1.05, y = 0.15, s = 0;
      lines.push(a, y, z, b, y, z);
      while (y + step < h - 0.1) { var y2 = y + step; if (s++ % 2) lines.push(a, y, z, b, y2, z); else lines.push(b, y, z, a, y2, z); y = y2; }
      lines.push(a, h - 0.1, z, b, h - 0.1, z);
    });
    inst(posts, tm('echelle', '#2f5fd0'), 'echelles');
    inst(postsH, tm('echelle-haute', '#173a8c'), 'echelles-hautes');
    var lg = new T.BufferGeometry(); lg.setAttribute('position', new T.Float32BufferAttribute(lines, 3));
    var lm = new T.LineBasicMaterial({ color: new T.Color(css('echelle', '#2f5fd0')) });
    mats['lines'] = { m: lm, t: 'echelle', f: '#2f5fd0' };
    S.add(new T.LineSegments(lg, lm));

    // lisses par référence + plateaux fils + butées
    var beams = {}, decks = [], stops = [];
    D.bays.forEach(function (b) {
      var x = b[0] * k, z = (b[1] + D.BAY / 2) * k, ref = b[2], sec = D.refs[ref] * k;
      beams[ref] = beams[ref] || [];
      D.levels.forEach(function (lv) {
        var y = lv * k - sec / 2;
        beams[ref].push([x + 0.025, y, z, 0.05, sec, D.BAY * k]);
        beams[ref].push([x + D.DEPTH * k - 0.025, y, z, 0.05, sec, D.BAY * k]);
        decks.push([x + D.DEPTH * k / 2, lv * k + 0.012, z, D.DEPTH * k, 0.02, D.BAY * k - 0.02]);
        for (var s = 0; s < 4; s++) stops.push([x + D.DEPTH * k - 0.09, lv * k + 0.13, (b[1] + 80 + s * 880 + 400) * k, 0.06, 0.24, 0.16]);
      });
    });
    var refTok = { O120: ['lisse-o120', '#b93c0b'], O110: ['lisse-o110', '#f2761b'], J110: ['lisse-j110', '#e3b10a'] };
    Object.keys(beams).forEach(function (r) { inst(beams[r], tm(refTok[r][0], refTok[r][1]), 'lisses-' + r); });
    inst(decks, new T.MeshLambertMaterial({ color: 0x9aa3ad, transparent: true, opacity: 0.45 }), 'plateaux');
    inst(stops, new T.MeshLambertMaterial({ color: 0xb7bcc3 }), 'butees');

    // portiques, protections, poteaux
    inst(D.portiques.map(function (p) { return [(p[0] + p[1]) / 2 * k, D.H_RIVE * k - 0.07, p[2] * k, (p[1] - p[0]) * k + 0.1, 0.12, 0.08]; }), tm('portique', '#0d7a6f'), 'portiques');
    inst(D.prots.map(function (p) { return [(p[0] + p[2] / 2) * k, 0.2, (p[1] + p[3] / 2) * k, p[2] * k, 0.4, p[3] * k]; }), tm('protection', '#c8261d'), 'protections');
    inst(D.columns.map(function (c) { return [c[0] * k, 6, c[1] * k, c[2] * k, 12, c[2] * k]; }), mat('#8d9097'), 'poteaux');

    // palettes : tri par rang aléatoire pour simuler un taux de remplissage
    var slots = D.slots.slice().sort(function (a, b) { return a[3] - b[3]; });
    var base = slots.map(function (s) { return [s[0] * k, s[2] * k + 0.072, s[1] * k, D.PAL_D * k, 0.144, D.PAL_W * k]; });
    var load = slots.map(function (s) { var h = (D.PAL_H - 144 - s[4] * 60) * k; return [s[0] * k, s[2] * k + 0.144 + h / 2, s[1] * k, D.PAL_D * k - 0.04, h, D.PAL_W * k - 0.04]; });
    var mBase = inst(base, tm('palette-bois', '#a07a45'), 'palettes');
    var cm = new T.MeshLambertMaterial({ color: 0xffffff });
    var mLoad = inst(load, cm, 'charges');
    var tones = ['#d9bf91', '#cfb07c', '#e2cca3', '#c9a46c'];
    slots.forEach(function (s, i) { mLoad.setColorAt(i, new T.Color(tones[s[4]])); });
    function setFill(f) { var c = Math.round(slots.length * f); mBase.count = c; mLoad.count = c; draw(); return c; }

    var views = {
      iso: function () { C.position.set(-14, 34, ez + 16); ctl && ctl.target.set(ex / 2, 2, ez / 2); },
      top: function () { C.position.set(ex / 2, 85, ez / 2 + 0.01); ctl && ctl.target.set(ex / 2, 0, ez / 2); },
      allee: function () { var ax = D.aisle[0] * k, az = D.aisle[1] * k; C.position.set(ax, 1.7, az + 36.5); ctl && ctl.target.set(ax, 4.2, az + 6); },
      zoneA: function () { C.position.set(ex + 6, 16, -10); ctl && ctl.target.set(ex / 2, 3, 6); }
    };
    function view(n) { (views[n] || views.iso)(); if (ctl) ctl.update(); else C.lookAt(ex / 2, 2, ez / 2); draw(); }
    function draw() { R.render(S, C); }
    if (ctl) ctl.addEventListener('change', draw);
    var ro = window.ResizeObserver ? new ResizeObserver(function () { var w = el.clientWidth, h = el.clientHeight; if (!w || !h) return; R.setSize(w, h); C.aspect = w / h; C.updateProjectionMatrix(); draw(); }) : null;
    if (ro) ro.observe(el);
    themed();
    setFill(opt.fill == null ? 0.85 : opt.fill);
    view(opt.view || 'iso');
    return { setFill: setFill, view: view, draw: draw, themed: themed, renderer: R, total: slots.length };
  }
  return { mount: mount };
})();
