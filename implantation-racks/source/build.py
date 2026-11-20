import json, os, sys, base64, datetime
from model import *
from render import *

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.dirname(HERE)
OUT = "/home/user/skills-claude/implantation-racks"
DS = os.path.join(SCR, "ds")
NPM = os.path.join(SCR, "npm/node_modules/three")
os.makedirs(OUT, exist_ok=True)

m = build()
st = stats(m)
D3 = json.dumps(data3d(m), separators=(",", ":"))
ENGINE = open(os.path.join(HERE, "engine3d.js")).read()
THREE = open(os.path.join(NPM, "build/three.min.js")).read()
ORBIT = open(os.path.join(NPM, "examples/js/controls/OrbitControls.js")).read()
GFONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">'
ROOT_VARS = f":root{{{css_vars('light')};{FONTS_CSS}}}@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{{css_vars('dark')}}}}}:root[data-theme=dark]{{{css_vars('dark')}}}"

DOC_CSS = """
.tb{width:100%;border-collapse:collapse;font:12px/1.45 var(--font-sans);color:var(--ink)}
.tb th{text-align:left;font-weight:600;color:var(--ink-muted);border-bottom:1.5px solid var(--ink);padding:6px 8px;font-size:11px;text-transform:uppercase;letter-spacing:.04em}
.tb td{border-bottom:1px solid var(--line);padding:6px 8px;vertical-align:top}
.tb .num{text-align:right;font-family:var(--font-mono);white-space:nowrap}
.tb .mono{font-family:var(--font-mono);font-size:11px}
.tb .warn,.sig{color:var(--signal);font-weight:600}
.muted{color:var(--ink-muted)}
.chip{display:inline-block;width:14px;height:10px;margin-right:8px;vertical-align:baseline}
.c-O120{background:var(--lisse-o120)}.c-O110{background:var(--lisse-o110)}.c-J110{background:var(--lisse-j110)}
"""
STYLE_ALL = SVG_CSS + DOC_CSS

# ---------- 3D standalone (hors ligne) ----------
def page3d(inline_three=True, preserve=False, controls=True, fill=0.85, view="iso", size=None):
    libs = (f"<script>{THREE}</script><script>{ORBIT}</script>" if inline_three else
            '<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js"></script>'
            '<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/controls/OrbitControls.js"></script>')
    sz = f"width:{size[0]}px;height:{size[1]}px" if size else "position:fixed;inset:0"
    ui = """
<div class="ui">
 <div class="ttl">Implantation racks · vue 3D</div>
 <div class="row"><button data-v="iso">Perspective</button><button data-v="allee">Dans l'allée</button><button data-v="zoneA">Zone A</button><button data-v="top">Dessus</button></div>
 <label>Simulation de remplissage <b id="pct">85 %</b><input id="fill" type="range" min="0" max="100" value="85"></label>
 <div class="lg"><span><i class="c-O120"></i>O120 Orange 120</span><span><i class="c-O110"></i>O110 Orange 110</span><span><i class="c-J110"></i>J110 Jaune 110</span><span><i style="background:var(--portique)"></i>Portiques</span></div>
 <div class="hint">Glisser : tourner · Molette : zoom · Clic droit : déplacer</div>
</div>""" if controls else ""
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vue 3D implantation</title>{GFONT}<style>{ROOT_VARS}
html,body{{margin:0;background:var(--paper);color:var(--ink);font:13px var(--font-sans)}}
#v{{{sz}}}
.ui{{position:fixed;left:16px;top:16px;max-width:340px;background:var(--surface);border:1px solid var(--line);padding:14px 16px;display:grid;gap:10px}}
.ttl{{font-weight:700;font-size:15px}} .row{{display:flex;flex-wrap:wrap;gap:6px}}
button{{font:inherit;background:var(--paper);color:var(--ink);border:1px solid var(--line);padding:6px 10px;cursor:pointer}}
button:hover{{border-color:var(--ink)}} label{{display:grid;gap:4px}} input{{width:100%}}
.lg{{display:flex;flex-wrap:wrap;gap:6px 12px;font-size:12px}} .lg i{{display:inline-block;width:12px;height:12px;margin-right:6px;vertical-align:-1px}}
.c-O120{{background:var(--lisse-o120)}}.c-O110{{background:var(--lisse-o110)}}.c-J110{{background:var(--lisse-j110)}}
.hint{{color:var(--ink-muted);font-size:12px}}
@media (max-width:600px){{.ui{{left:8px;right:8px;top:auto;bottom:8px;max-width:none}}}}
</style></head><body><div id="v"></div>{ui}
{libs}<script>window.RACK_DATA={D3};</script><script>{ENGINE}</script>
<script>
var api=Rack3D.mount(document.getElementById('v'),RACK_DATA,{{preserve:{str(preserve).lower()},fill:{fill},view:'{view}'}});
window.api=api;
document.querySelectorAll('[data-v]').forEach(function(b){{b.onclick=function(){{api.view(b.dataset.v)}}}});
var f=document.getElementById('fill');if(f)f.oninput=function(){{document.getElementById('pct').textContent=f.value+' %';api.setFill(f.value/100)}};
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',function(){{api.themed()}});
</script></body></html>"""

open(os.path.join(OUT, "vue-3d.html"), "w").write(page3d(True))
svg_std = svg_plan(m, legend=True, standalone=True)
open(os.path.join(OUT, "plan-2d.svg"), "w").write(svg_std)
for rid in ("A4W", "B2W"):
    open(os.path.join(OUT, f"elevation-{rid}.svg"), "w").write(svg_elevation(m, rid, 0.9, standalone=True))
with open(os.path.join(OUT, "inventaire.csv"), "w") as f:
    f.write("Famille;Désignation;Caractéristiques;Quantité;Base de calcul\n")
    for r in inventory(m):
        f.write(";".join(str(x) for x in r) + "\n")
json.dump(dict(stats=st), open(os.path.join(HERE, "stats.json"), "w"))
print(st)
