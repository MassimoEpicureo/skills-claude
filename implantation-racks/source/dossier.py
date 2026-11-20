import base64, os, subprocess, json
from build import *

FD = os.path.join(SCR, "npm/node_modules/@fontsource")
def ff(fam, path, w):
    b = base64.b64encode(open(os.path.join(FD, path), "rb").read()).decode()
    return f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b}) format('woff2')}}"
FONTFACES = "".join([
    ff("IBM Plex Sans", "ibm-plex-sans/files/ibm-plex-sans-latin-400-normal.woff2", 400),
    ff("IBM Plex Sans", "ibm-plex-sans/files/ibm-plex-sans-latin-600-normal.woff2", 600),
    ff("IBM Plex Sans", "ibm-plex-sans/files/ibm-plex-sans-latin-700-normal.woff2", 700),
    ff("IBM Plex Mono", "ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2", 400),
    ff("IBM Plex Mono", "ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2", 500),
])

# --- rendus 3D pour le dossier ---
shots = {}
tmp = os.path.join(SCR, "r3d.html")
for v in ("iso", "allee", "zoneA"):
    open(tmp, "w").write(page3d(True, preserve=True, controls=False, fill=0.88, view=v))
    out = os.path.join(SCR, f"r3d-{v}.png")
    subprocess.run(["node", os.path.join(HERE, "shot.js"), "file://" + tmp, out, "1600", "1000"], check=True)
    shots[v] = "data:image/png;base64," + base64.b64encode(open(out, "rb").read()).decode()
    import shutil; shutil.copy(out, os.path.join(OUT, f"rendu-3d-{v}.png"))

alloc_ok = all(True for _ in [0])
TODAY = "20/11/2026"

def page(title, num, body, kicker=""):
    return f"""<section class="pg"><header><div><span class="k">{kicker}</span><h2>{title}</h2></div><div class="pn">Implantation racks · {num:02d}</div></header><div class="bd">{body}</div></section>"""

kpis = [("Racks doubles", st["racks"]), ("Alvéoles 3 600", st["bays"]), ("Emplacements palettes", n(st["slots"])),
        ("Échelles", st["frames"]), ("Lisses", st["beams"]), ("Portiques d'allée", st["portiques"])]
kpi_html = "".join(f'<div class="kpi"><b>{v}</b><span>{l}</span></div>' for l, v in kpis)

spec = [
    ("Échelles de rive / portique", "H 10 005 mm (plan) · P 1 100 · fût 80"),
    ("Échelles intermédiaires", "H 8 500 mm (plan) · P 1 100 · fût 80"),
    ("Niveaux", "4 niveaux de lisses + sol : 2 044 / 4 044 / 6 044 / 8 044"),
    ("Lisses", "3 600 mm · 4 PAL/niveau · 3 références du stock client"),
    ("Cheminée", "entretoises 250 mm (racks doubles 2 450)"),
    ("Charge", "400 kg/palette · 1 600 kg/niveau · 6 400 kg/alvéole sur lisses"),
    ("Palette", "800 × 1 200 · H 1 750 gerbage inclus (hypothèse)"),
    ("Chariot", "Retract · allées 3 000 / 3 314 / 3 315 · allée murale 5 631"),
    ("Équipements", "plateaux fils, butées podium N1–N4, goupilles, sabots, protections, goujons"),
    ("Portiques", "toutes les 2 alvéoles entre racks du périmètre, échelles H 10 005"),
]
spec_html = '<table class="tb">' + "".join(f"<tr><td class='muted'>{a}</td><td>{b}</td></tr>" for a, b in spec) + "</table>"

vig = [
    ("Poteaux P1 / P2 dans B-R3 face Ouest", "Relevés à l'échelle sur le plan (±300 mm) : ils tombent au milieu de la profondeur, entre les deux lisses. Les lisses restent posées, mais 15 emplacements palettes sont perdus (3 par niveau, sol inclus) ainsi que 12 plateaux et 12 butées. <b>Relevé géomètre obligatoire avant commande.</b>"),
    ("Poteaux P3 / P4 dans l'allée transversale", "À environ 1 m des racks de la zone B, dans l'axe de B-R3 et de A-R6 : vérifier la giration du retract et prévoir une protection de poteau."),
    ("Compatibilité C-LOG / ECOLOG", "Les lisses jaunes C-LOG doivent avoir des crochets compatibles avec la perforation des échelles retenues. À valider avec le fabricant avant toute pose."),
    ("Portée des lisses", "1 600 kg par paire sur 3 600 mm : à vérifier dans les tables de charge de la section la plus faible (110×50), flèche ≤ L/200."),
    ("Retract et portiques", "Hauteur de levée nécessaire ≥ 8,2 m. Le mât déployé doit passer sous la traverse de portique (sous-face ≈ 9 885 mm)."),
    ("Hauteur des palettes", "Non renseignée au cahier des charges : hypothèse de 1 750 mm (pas de 2 000 − lisse 120 − jeu de 130). Palette haute en N4 : 9 794 mm, à comparer à la hauteur sous sprinklers."),
    ("Écarts de cotes", "Calcul avec fût de 80 mm : zone A 11 120 (plan 11 123), zone B 36 880 (plan 36 886). L'élévation indique 81 mm : à confirmer."),
    ("Hypothèses de quantités", "Entretoises : 3 par paire, 4 sur les paires de 10 005. Goujons des protections de bout d'allée : 8 par pièce. Plateaux fils : 4 par niveau. À aligner sur la notice du fabricant."),
    ("Réglementation", "Plaques de charge par rack et inspection annuelle selon NF EN 15635. Plateaux 880 × 1 100 : sans objet, aucun passage pont ni porte coupe-feu dans les alignements."),
]
vig_html = '<ol class="vig">' + "".join(f"<li><b>{a}</b><p>{b}</p></li>" for a, b in vig) + "</ol>"

choice = f"""
<div class="cols">
<div>
<h3>Le constat</h3>
<p>Le plan demande <b>122 alvéoles × 8 lisses = 976 lisses</b>, soit exactement le stock. Mais 346 (Orange 120) et 334 (Jaune 110) ne sont pas des multiples de 8 : <b>sans ajustement, une alvéole aurait obligatoirement des lisses de références différentes.</b></p>
<h3>La solution retenue</h3>
<p><b>Commander 2 lisses 3600×110×50 C-LOG jaune.</b> Les 3 références se répartissent alors <b>par face d'allée entière</b>. Chaque allée est homogène : un cariste ou un visiteur ne voit qu'une seule section et une seule couleur. Il reste 2 lisses Orange 120 en pièces de rechange.</p>
<h3>Alternative sans achat</h3>
<p>Créer un <b>passage pont</b> au milieu de B-R4, côtés Ouest et Est (alvéole 6), en supprimant le niveau N1. Cela économise 4 lisses jaunes et ne nécessite aucune commande. En contrepartie, on perd 16 emplacements palettes et il faut ajouter 8 plateaux fils 880 × 1 100.</p>
</div>
<div>{table_alloc(m)}
<p class="muted small">Règle appliquée : une face de rack orientée vers une allée = une seule référence de lisse. Les deux faces d'un rack double donnent sur des allées différentes et peuvent donc porter deux références sans mélange visible.</p></div>
</div>"""

css = f"""{FONTFACES}{ROOT_VARS.split('@media')[0]}{STYLE_ALL}
@page{{size:A4 landscape;margin:0}}
*{{box-sizing:border-box}} body{{margin:0;background:#888;font:13px/1.5 var(--font-sans);color:var(--ink)}}
.pg{{width:297mm;height:210mm;background:var(--paper);padding:11mm 13mm 9mm;display:flex;flex-direction:column;page-break-after:always;overflow:hidden;position:relative}}
.pg header{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1.5px solid var(--ink);padding-bottom:3mm;margin-bottom:5mm}}
.pg h2{{margin:0;font-size:22px;font-weight:700;letter-spacing:-.01em}} .k{{font:500 10px var(--font-mono);color:var(--ink-muted);text-transform:uppercase;letter-spacing:.08em}}
.pn{{font:400 10px var(--font-mono);color:var(--ink-muted)}}
.bd{{flex:1;min-height:0;display:flex;flex-direction:column;gap:4mm}}
.bd>svg,.fit svg{{width:100%;height:100%;min-height:0}}
.fit{{flex:1;min-height:0;display:flex}}
h3{{font-size:13px;margin:0 0 4px;font-weight:700}} p{{margin:0 0 10px}} .small{{font-size:11px}}
.cols{{display:grid;grid-template-columns:1fr 1.25fr;gap:9mm}}
.kpis{{display:grid;grid-template-columns:repeat(6,1fr);gap:0;border-top:1.5px solid var(--ink)}}
.kpi{{padding:8px 10px 0 0}} .kpi b{{display:block;font:600 26px var(--font-mono);letter-spacing:-.02em}} .kpi span{{font-size:11px;color:var(--ink-muted)}}
.cover{{padding:0;display:grid;grid-template-columns:118mm 1fr}}
.cover .l{{padding:16mm 12mm 12mm 14mm;display:flex;flex-direction:column;justify-content:space-between;background:var(--surface)}}
.cover h1{{font-size:38px;line-height:1.02;margin:0 0 10px;letter-spacing:-.02em}}
.cover .r{{background:var(--paper) url({shots['iso']}) center/cover no-repeat}}
.bars{{display:flex;height:9px;margin:0 0 18px}} .bars i{{flex:1}}
.meta{{font:400 11px/1.7 var(--font-mono);color:var(--ink-muted)}}
.img2{{display:grid;grid-template-columns:1fr 1fr;gap:5mm;flex:1;min-height:0}} .img2 figure{{margin:0;display:flex;flex-direction:column;min-height:0}}
.img2 img{{width:100%;flex:1;min-height:0;object-fit:cover;border:1px solid var(--line)}} figcaption{{font-size:11px;color:var(--ink-muted);padding-top:4px}}
.el{{flex:1;min-height:0;display:flex;flex-direction:column}} .el svg{{flex:1;min-height:0;width:100%}} .el h3{{margin-top:2mm}}
.vig{{columns:2;column-gap:10mm;margin:0;padding-left:18px;font-size:12px}} .vig li{{break-inside:avoid;margin-bottom:8px}} .vig p{{margin:2px 0 0;color:var(--ink)}}
.vig li::marker{{font-family:var(--font-mono);color:var(--signal);font-weight:600}}
.planpg .bd{{flex-direction:row;gap:7mm}} .planpg .side{{width:62mm;font-size:11.5px}}
"""
plan_side = f"""<div class="side"><h3>Lecture du plan</h3>
<p>Chaque alvéole porte sa <b>longueur de lisse</b> et sa <b>référence</b> (« 3600 · O110 »). Les traits de couleur matérialisent les lisses, les barres bleues les échelles (bleu foncé : H 10 005).</p>
<p>Portiques <span style="color:var(--portique);font-weight:600">tiretés</span> toutes les 2 alvéoles, au-dessus des allées intérieures uniquement. Les allées voisines des racks hors périmètre et l'allée murale n'en reçoivent pas.</p>
<p><span class="sig">P1–P4</span> : poteaux du bâtiment à relever.</p>
<h3>Zones</h3><p>A : 7 racks doubles × 3 alvéoles.<br>B : 4 racks doubles × 10 alvéoles.<br>Allée transversale : 4 540.</p>
<h3>Références</h3><p><span class="chip c-O120"></span>O120 Orange 120<br><span class="chip c-O110"></span>O110 Orange 110<br><span class="chip c-J110"></span>J110 Jaune 110</p></div>"""

html = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Dossier implantation racks</title><style>{css}</style></head><body>
<section class="pg cover"><div class="l"><div><div class="bars"><i class="c-O120"></i><i class="c-O110"></i><i class="c-J110"></i><i style="background:var(--echelle)"></i></div>
<div class="k">Proposition d'implantation · bureau d'études</div><h1>Rayonnages à palettes<br>retract · 2 440 emplacements</h1>
<p class="muted">Plan 2D coté, répartition des lisses sans mélange de section ni de couleur, simulation 3D en charge et inventaire complet du matériel.</p></div>
<div class="meta">Client : à compléter<br>Site : à compléter<br>Date : {TODAY} · Indice A<br>Statut : avant-projet, à valider après relevé</div></div><div class="r"></div></section>
{page("Synthèse du projet", 2, f'<div class="kpis">{kpi_html}</div><div class="cols"><div><h3>Cahier des charges appliqué</h3>{spec_html}</div><div><h3>Ce qu’il faut retenir</h3><p><b>Le stock de lisses couvre 100 % du besoin à 2 lisses près.</b> Avec 2 lisses jaunes C-LOG supplémentaires, chaque allée est équipée d’une seule référence, conformément à l’exigence du client.</p><p>Capacité : <b>{n(st["slots"])} emplacements théoriques</b> (sol + 4 niveaux × 4 palettes × 122 alvéoles), soit {n(st["slots_ok"])} si les poteaux P1/P2 sont confirmés dans le rack B-R3. Charge maximale stockée : {n(st["slots"]*PAL_KG/1000)} t.</p><p>36 portiques d’allée relient les racks au-dessus des allées intérieures. Ils utilisent 36 échelles hautes (H 10 005) placées toutes les deux alvéoles.</p><p class="sig">Point bloquant avant commande : relevé des poteaux du bâtiment (voir page 9).</p></div></div>', "01 · Résumé")}
<section class="pg planpg"><header><div><span class="k">02 · Implantation</span><h2>Plan 2D coté</h2></div><div class="pn">Implantation racks · 03</div></header><div class="bd"><div class="fit">{svg_plan(m, legend=False)}</div>{plan_side}</div></section>
{page("Répartition des lisses", 4, choice, "03 · Exigence client")}
{page("Élévations et simulation de charge", 5, f'<div class="el"><h3>Zone A · face A-R4 Ouest · 3 alvéoles · lisses O110</h3>{svg_elevation(m, "A4W", 0.92)}</div><div class="el"><h3>Zone B · face B-R2 Ouest · 10 alvéoles · lisses O120</h3>{svg_elevation(m, "B2W", 0.92)}</div>', "04 · Vue en projection")}
{page("Vue 3D de l'entrepôt chargé", 6, f'<div class="img2"><figure><img src="{shots["allee"]}"><figcaption>Dans l’allée B-R3 / B-R4 (3 315 mm) : lisses O120 à gauche, J110 à droite, portiques en tête.</figcaption></figure><figure><img src="{shots["zoneA"]}"><figcaption>Zone A depuis le nord-est : passage du jaune (A-R5 à A-R7) à l’orange 110. Simulation à 88 % de remplissage.</figcaption></figure></div>', "05 · Simulation")}
{page("Mesures au sol (traçage)", 7, f'<p class="small muted">Origine X = nu intérieur du mur ouest. Origine Y = about nord de la zone A (côté des échelles de rive). Entraxe des échelles : 3 680 (lisse de 3 600 + fût de 80). Toutes les cotes sont en mm.</p>{table_trace(m)}', "06 · Chantier")}
{page("Inventaire complet du matériel", 8, table_inventory(m), "07 · Quantitatif")}
{page("Points de vigilance et hypothèses", 9, vig_html, "08 · À valider")}
</body></html>"""
open(os.path.join(OUT, "dossier.html"), "w").write(html)
print("dossier ok", len(html) // 1024, "KB")
