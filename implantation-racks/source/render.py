"""Rendus : SVG plan 2D, élévations, tables HTML, données 3D."""
import json
from model import *

TOKENS = [
    # name, light, dark, usage
    ("paper", "#f6f5f1", "#141619", "Fond de page et de planche."),
    ("surface", "#ffffff", "#1d2025", "Cartes, tableaux, cartouche."),
    ("ink", "#1b1f24", "#eceef1", "Texte principal, traits de cotation forts, mur."),
    ("ink-muted", "#59616c", "#a5adb8", "Texte secondaire, chaînes de cotes (≥4.5:1 sur paper)."),
    ("line", "#cfd2d7", "#3a3f47", "Filets de tableau, contours de rack."),
    ("aisle-floor", "#e9e6de", "#22252a", "Sol des allées de circulation sur le plan."),
    ("lisse-o120", "#b93c0b", "#f0702e", "Lisse 3600×120×50 ECOLOG orange : trait de lisse, pastille. La plus foncée des trois."),
    ("lisse-o120-tint", "#b93c0b2e", "#f0702e33", "Fond des faces de rack équipées en Orange 120."),
    ("lisse-o110", "#f2761b", "#fdba74", "Lisse 3600×110×50 ECOLOG orange : intermédiaire en clarté, toujours doublé du code O110."),
    ("lisse-o110-tint", "#f2761b2b", "#fdba7430", "Fond des faces de rack équipées en Orange 110."),
    ("lisse-j110", "#e3b10a", "#fde047", "Lisse 3600×110×50 C-LOG jaune : la plus claire, toujours doublé du code J110."),
    ("lisse-j110-tint", "#e3b10a33", "#fde04726", "Fond des faces de rack équipées en Jaune 110."),
    ("echelle", "#2f5fd0", "#6d9cff", "Échelle intermédiaire H 8 500 (plan, élévation, 3D)."),
    ("echelle-haute", "#173a8c", "#b4ccff", "Échelle de rive / portique H 10 005."),
    ("portique", "#0d7a6f", "#34d3bf", "Traverse de portique d'allée (trait tireté sur le plan)."),
    ("palette-bois", "#a07a45", "#b98f55", "Plancher de palette (élévation, 3D)."),
    ("palette-carton", "#d9bf91", "#c7a876", "Charge palettisée (élévation, 3D)."),
    ("poteau", "#3d434c", "#9aa2ad", "Poteau béton du bâtiment."),
    ("protection", "#c8261d", "#ff6b5e", "Protections de bout d'allée et sabots."),
    ("signal", "#b42318", "#ff8a7a", "Point de vigilance, conflit à lever."),
]

def css_vars(theme):
    i = 1 if theme == "light" else 2
    return ";".join(f"--{t[0]}:{t[i]}" for t in TOKENS)

FONTS_CSS = "--font-sans:'IBM Plex Sans',system-ui,sans-serif;--font-mono:'IBM Plex Mono',ui-monospace,monospace"

SVG_CSS = """
.pl-bg{fill:var(--paper)}
.pl-wall{stroke:var(--ink);stroke-width:220}
.pl-aisle{fill:var(--aisle-floor)}
.pl-row-O120{fill:var(--lisse-o120-tint)} .pl-row-O110{fill:var(--lisse-o110-tint)} .pl-row-J110{fill:var(--lisse-j110-tint)}
.pl-rowo{fill:none;stroke:var(--line);stroke-width:24}
.pl-beam-O120{stroke:var(--lisse-o120);stroke-width:90} .pl-beam-O110{stroke:var(--lisse-o110);stroke-width:90} .pl-beam-J110{stroke:var(--lisse-j110);stroke-width:90}
.f-O120{fill:var(--lisse-o120)} .f-O110{fill:var(--lisse-o110)} .f-J110{fill:var(--lisse-j110)}
.pl-up{fill:var(--echelle)} .pl-up-h{fill:var(--echelle-haute)}
.pl-port{stroke:var(--portique);stroke-width:90;stroke-dasharray:260 160}
.pl-col{fill:var(--poteau)} .pl-colr{fill:none;stroke:var(--signal);stroke-width:60}
.pl-prot{fill:var(--protection)}
.pl-ghost{fill:none;stroke:var(--line);stroke-width:30;stroke-dasharray:200 160}
.pl-dim{stroke:var(--ink-muted);stroke-width:22;fill:none}
.pl-t{fill:var(--ink);font-family:var(--font-mono)} .pl-tm{fill:var(--ink-muted);font-family:var(--font-mono)}
.pl-ts{fill:var(--ink);font-family:var(--font-sans);font-weight:600}
.pl-sig{fill:var(--signal);font-family:var(--font-sans);font-weight:600}
.el-pal-b{fill:var(--palette-bois)} .el-pal{fill:var(--palette-carton);stroke:var(--palette-bois);stroke-width:14}
.el-floor{stroke:var(--ink);stroke-width:60}
.el-port{fill:var(--portique)}
"""

def n(v):
    return f"{int(round(v)):,}".replace(",", " ")

def dim_h(x1, x2, y, label, size=520, cls="pl-tm"):
    t = 220
    return (f'<path class="pl-dim" d="M{x1} {y}H{x2}M{x1} {y-t}V{y+t}M{x2} {y-t}V{y+t}"/>'
            f'<text class="{cls}" x="{(x1+x2)/2}" y="{y-180}" font-size="{size}" text-anchor="middle">{label}</text>')

def dim_v(y1, y2, x, label, size=520):
    t = 220
    cy = (y1 + y2) / 2
    return (f'<path class="pl-dim" d="M{x} {y1}V{y2}M{x-t} {y1}H{x+t}M{x-t} {y2}H{x+t}"/>'
            f'<text class="pl-tm" x="{x-200}" y="{cy}" font-size="{size}" text-anchor="middle" transform="rotate(-90 {x-200} {cy})">{label}</text>')


def svg_plan(m, legend=True, standalone=False):
    xmax = RACK_X[6] + RW + 3000 + 1100
    ytot = ZONES[1]["y0"] + ZONES[1]["len"]
    vx, vy = -3600, -4300
    vw = xmax + 4600
    vh = ytot + 5600 + (6200 if legend else 0)
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {vw} {vh}" role="img" aria-label="Plan 2D d\'implantation">')
    if standalone:
        o.append(f"<style>svg{{{css_vars('light')};{FONTS_CSS}}}{SVG_CSS}</style>")
    o.append(f'<rect class="pl-bg" x="{vx}" y="{vy}" width="{vw}" height="{vh}"/>')
    # allées (sol)
    for z in ZONES:
        o.append(f'<rect class="pl-aisle" x="0" y="{z["y0"]}" width="{xmax}" height="{z["len"]}"/>')
    o.append(f'<rect class="pl-aisle" x="0" y="{CROSS[0]}" width="{xmax}" height="{CROSS[1]-CROSS[0]}"/>')
    # mur ouest + porte
    door_y = CROSS[0] + 1700
    o.append(f'<path class="pl-wall" d="M0 -1800V{door_y}M0 {door_y+1200}V{ytot+1800}"/>')
    o.append(f'<path class="pl-dim" d="M0 {door_y}L1200 {door_y}A1200 1200 0 0 1 0 {door_y+1200}"/>')
    o.append(f'<text class="pl-tm" x="300" y="{door_y-250}" font-size="420">Porte</text>')
    # emprises hors périmètre (racks cyan du plan d'origine)
    gx = RACK_X[6] + RW + 3000
    o.append(f'<rect class="pl-ghost" x="{gx}" y="0" width="{RW}" height="{ZONES[0]["len"]}"/>')
    for k in range(4, 8):
        x = RACK_X[k] if k < 7 else gx
        o.append(f'<rect class="pl-ghost" x="{x}" y="{ZONES[1]["y0"]}" width="{RW}" height="{ZONES[1]["len"]}"/>')
    o.append(f'<text class="pl-tm" x="{(RACK_X[4]+gx+RW)/2}" y="{ZONES[1]["y0"]+ZONES[1]["len"]/2}" font-size="700" text-anchor="middle">Hors périmètre</text>')
    # faces de rack
    for r in m["rows"]:
        x, y0, L, ref = r["x"], r["y0"], r["len"], r["ref"]
        o.append(f'<rect class="pl-row-{ref}" x="{x}" y="{y0}" width="{DEPTH}" height="{L}"/>')
        o.append(f'<rect class="pl-rowo" x="{x}" y="{y0}" width="{DEPTH}" height="{L}"/>')
        o.append(f'<path class="pl-beam-{ref}" d="M{x+45} {y0}V{y0+L}M{x+DEPTH-45} {y0}V{y0+L}"/>')
    for b in m["bays"]:
        cx, cy = b["x"] + DEPTH / 2, b["y"] + BAY / 2
        o.append(f'<text class="pl-t" x="{cx}" y="{cy}" font-size="360" text-anchor="middle" dominant-baseline="central" transform="rotate(-90 {cx} {cy})">{BAY} · {b["ref"]}</text>')
    for f in m["frames"]:
        cls = "pl-up-h" if f["h"] == H_RIVE else "pl-up"
        o.append(f'<rect class="{cls}" x="{f["x"]}" y="{f["y"]}" width="{DEPTH}" height="{POST}"/>')
    for p in m["portiques"]:
        o.append(f'<path class="pl-port" d="M{p["x1"]} {p["y"]}H{p["x2"]}"/>')
    for p in m["prots"]:
        o.append(f'<rect class="pl-prot" x="{p["x"]}" y="{p["y"]}" width="{p["w"]}" height="{p["d"]}"/>')
    for c in COLUMNS:
        s = c["size"]
        o.append(f'<rect class="pl-col" x="{c["x"]-s/2}" y="{c["y"]-s/2}" width="{s}" height="{s}"/>')
        o.append(f'<circle class="pl-colr" cx="{c["x"]}" cy="{c["y"]}" r="700"/>')
        o.append(f'<text class="pl-sig" x="{c["x"]-850}" y="{c["y"]+160}" font-size="460" text-anchor="end">{c["id"]}</text>')
    # repères de racks
    for z in ZONES:
        for k in range(1, z["racks"] + 1):
            X = RACK_X[k - 1]
            ty = z["y0"] - 700 if z["id"] == "A" else z["y0"] - 700
            o.append(f'<text class="pl-ts" x="{X+RW/2}" y="{ty}" font-size="520" text-anchor="middle">{z["id"]}-R{k}</text>')
    # libellés d'allées
    for z in ZONES:
        cy = z["y0"] + z["len"] / 2
        ax = [(0, RACK_X[0])] + [(RACK_X[k] + RW, RACK_X[k] + RW + AISLE_AFTER[k]) for k in range(z["racks"])]
        for (a1, a2) in ax:
            cx = (a1 + a2) / 2
            o.append(f'<text class="pl-tm" x="{cx}" y="{cy}" font-size="440" text-anchor="middle" dominant-baseline="central" transform="rotate(-90 {cx} {cy})">ALLÉE {n(a2-a1)}</text>')
    o.append(f'<text class="pl-tm" x="{RACK_X[3]}" y="{(CROSS[0]+CROSS[1])/2 - 300}" font-size="480" text-anchor="middle">ALLÉE TRANSVERSALE {n(CROSS[1]-CROSS[0])}</text>')
    # cotes horizontales
    ydim = -2700
    xs = [0]
    for k in range(7):
        xs += [RACK_X[k], RACK_X[k] + RW]
    xs.append(RACK_X[6] + RW + 3000)
    for a, b in zip(xs, xs[1:]):
        o.append(dim_h(a, b, ydim, n(b - a), 480))
    o.append(dim_h(0, xs[-1], ydim - 1100, f"{n(xs[-1])} (mur → face rack hors périmètre)", 480))
    # cotes verticales
    xd = -1900
    o.append(dim_v(0, ZONES[0]["len"], xd, f"Zone A · {n(ZONES[0]['len'])}"))
    o.append(dim_v(CROSS[0], CROSS[1], xd, n(CROSS[1] - CROSS[0])))
    o.append(dim_v(ZONES[1]["y0"], ytot, xd, f"Zone B · {n(ZONES[1]['len'])}"))
    # détail d'entraxe à droite
    xr = xmax - 500
    z = ZONES[0]
    o.append(dim_v(z["y0"] + POST, z["y0"] + POST + BAY, xr, "lisse 3 600", 400))
    if legend:
        o.append(legend_svg(m, 0, ytot + 1900, xmax))
    o.append("</svg>")
    return "".join(o)


def legend_svg(m, x, y, w):
    from collections import Counter
    use = Counter(b["ref"] for b in m["beams"])
    g = [f'<g transform="translate({x} {y})">']
    g.append(f'<text class="pl-ts" x="0" y="0" font-size="560">Légende · règle client : 1 face d\'allée = 1 référence de lisse (section + couleur), aucune mixité</text>')
    col = 0
    for i, (r, d) in enumerate(REFS.items()):
        gx = i * 13500
        g.append(f'<rect class="f-{r}" x="{gx}" y="700" width="1400" height="700"/>')
        g.append(f'<text class="pl-t" x="{gx+1700}" y="1250" font-size="480">{r} · {d["short"]} — {use[r]} lisses</text>')
    items = [("pl-up-h", "Échelle H 10 005 (rive / portique)"), ("pl-up", "Échelle H 8 500"),
             ("pl-prot", "Protection bout d'allée"), ("pl-col", "Poteau bâtiment (à relever)")]
    for i, (c, t) in enumerate(items):
        gx = i * 11800
        g.append(f'<rect class="{c}" x="{gx}" y="2200" width="1400" height="500"/>')
        g.append(f'<text class="pl-t" x="{gx+1700}" y="2600" font-size="440">{t}</text>')
    g.append(f'<path class="pl-port" d="M0 3500H1400"/><text class="pl-t" x="1700" y="3650" font-size="440">Portique d\'allée (traverse en tête d\'échelle, toutes les 2 alvéoles)</text>')
    g.append(f'<text class="pl-tm" x="0" y="4700" font-size="440">Cotes en mm · origine X = mur ouest, Y = about nord zone A · « 3600 · O110 » = longueur de lisse et référence de l\'alvéole</text>')
    g.append("</g>")
    return "".join(g)


def svg_elevation(m, row_id, fill=1.0, standalone=False):
    row = next(r for r in m["rows"] if r["id"] == row_id)
    frames = [f for f in m["frames"] if f["row"] == row_id]
    slots = [s for s in m["slots"] if s["row"] == row_id]
    L = row["len"]
    vx, vy, vw, vh = -3200, -11400, L + 4600, 13200
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {vw} {vh}" role="img" aria-label="Élévation {row_id}">']
    if standalone:
        o.append(f"<style>svg{{{css_vars('light')};{FONTS_CSS}}}{SVG_CSS}</style>")
    o.append(f'<rect class="pl-bg" x="{vx}" y="{vy}" width="{vw}" height="{vh}"/>')
    ref = row["ref"]
    for s in slots:
        if s["blocked"] or s["r"] > fill:
            continue
        sx = s["y"] - row["y0"] - PAL_W / 2
        z = s["z"]
        o.append(f'<rect class="el-pal-b" x="{sx}" y="{-(z+144)}" width="{PAL_W}" height="144"/>')
        hh = PAL_H - 144 - (s["tone"] * 60)
        o.append(f'<rect class="el-pal" x="{sx+15}" y="{-(z+144+hh)}" width="{PAL_W-30}" height="{hh}"/>')
    for s in slots:
        if s["blocked"] and s["lv"] == 0:
            sx = s["y"] - row["y0"] - PAL_W / 2
            o.append(f'<text class="pl-sig" x="{sx+PAL_W/2}" y="-900" font-size="380" text-anchor="middle">{s["blocked"]}</text>')
    for lv in LEVELS:
        sec = REFS[ref]["sec"]
        o.append(f'<rect class="f-{ref}" x="0" y="{-lv}" width="{L}" height="{sec}"/>')
    for f in frames:
        x = f["y"] - row["y0"]
        cls = "pl-up-h" if f["h"] == H_RIVE else "pl-up"
        o.append(f'<rect class="{cls}" x="{x}" y="{-f["h"]}" width="{POST}" height="{f["h"]}"/>')
        if f["port"] or (f["rive"] and any(p["zone"] == row["zone"] for p in m["portiques"]) and _row_faces_inner(row)):
            o.append(f'<rect class="el-port" x="{x-200}" y="{-f["h"]-20}" width="{POST+400}" height="140"/>')
    o.append(f'<path class="el-floor" d="M-1200 0H{L+1200}"/>')
    # cotes niveaux
    prev = 0
    for lv in LEVELS:
        o.append(dim_v(-lv, -prev, -900, n(lv - prev), 380))
        prev = lv
    o.append(dim_v(-H_RIVE, 0, -2300, f"H rive {n(H_RIVE)}", 400))
    fi = next(f for f in frames if f["h"] == H_INT) if any(f["h"] == H_INT for f in frames) else None
    if fi:
        x = fi["y"] - row["y0"] + POST + 300
        o.append(dim_v(-H_INT, 0, x + 300, f"H {n(H_INT)}", 360))
    for b in range(row["bays"]):
        x1 = POST + b * PITCH
        o.append(dim_h(x1, x1 + BAY, 900, f"{BAY} · {ref}", 360, "pl-t"))
    for i, lv in enumerate(LEVELS, 1):
        o.append(f'<text class="pl-tm" x="{L+350}" y="{-lv-500}" font-size="380">N{i}</text>')
    o.append(f'<text class="pl-tm" x="{L+350}" y="-500" font-size="380">N0</text>')
    o.append("</svg>")
    return "".join(o)


def _row_faces_inner(row):
    z = next(z for z in ZONES if z["id"] == row["zone"])
    return (row["side"] == "E" and row["rack"] < z["racks"]) or (row["side"] == "W" and row["rack"] > 1)


def table_inventory(m):
    rows = inventory(m)
    h = ['<table class="tb"><thead><tr><th>Famille</th><th>Désignation</th><th>Caractéristiques</th><th class="num">Qté</th><th>Base de calcul</th></tr></thead><tbody>']
    for fam, des, car, q, note in rows:
        tag = ""
        for r in REFS:
            if des == REFS[r]["label"]:
                tag = f'<span class="chip c-{r}"></span>'
        warn = ' class="warn"' if "commander" in note else ""
        h.append(f'<tr><td>{fam}</td><td>{tag}{des}</td><td>{car}</td><td class="num"><b>{n(q)}</b></td><td{warn}>{note}</td></tr>')
    h.append("</tbody></table>")
    return "".join(h)


def table_alloc(m):
    from collections import defaultdict
    by = defaultdict(list)
    for r in m["rows"]:
        by[r["ref"]].append(r)
    h = ['<table class="tb"><thead><tr><th>Référence</th><th>Faces de rack équipées</th><th class="num">Alvéoles</th><th class="num">Lisses</th><th class="num">Stock</th><th>Écart</th></tr></thead><tbody>']
    for r, d in REFS.items():
        rs = by[r]
        alv = sum(x["bays"] for x in rs)
        faces = ", ".join(f'{x["zone"]}-R{x["rack"]}{"O" if x["side"]=="W" else "E"}' for x in rs)
        q = alv * 8
        e = d["stock"] - q
        et = f"reliquat {e}" if e > 0 else (f'<b class="sig">à commander {-e}</b>' if e < 0 else "soldé")
        h.append(f'<tr><td><span class="chip c-{r}"></span>{r} · {d["short"]}</td><td>{faces}</td><td class="num">{alv}</td><td class="num"><b>{q}</b></td><td class="num">{d["stock"]}</td><td>{et}</td></tr>')
    h.append("</tbody></table>")
    return "".join(h)


def table_trace(m):
    h = ['<table class="tb"><thead><tr><th>Rack</th><th class="num">X face Ouest</th><th class="num">X dos Ouest</th><th class="num">X dos Est</th><th class="num">X face Est</th><th class="num">Allée à l\'Est</th><th>Lisses O / E</th></tr></thead><tbody>']
    for k in range(7):
        X = RACK_X[k]
        refs = " / ".join(sorted({f'{ALLOC[z][f"{k+1}W"]}·{ALLOC[z][f"{k+1}E"]}' for z in ("A", "B") if f"{k+1}W" in ALLOC[z]}))
        h.append(f'<tr><td>R{k+1}</td><td class="num">{n(X)}</td><td class="num">{n(X+DEPTH)}</td><td class="num">{n(X+DEPTH+FLUE)}</td><td class="num">{n(X+RW)}</td><td class="num">{n(AISLE_AFTER[k])}</td><td>{refs}</td></tr>')
    h.append("</tbody></table>")
    h.append('<table class="tb"><thead><tr><th>Zone</th><th>Y des lignes d\'échelles (début du fût de 80 mm)</th><th class="num">Longueur</th></tr></thead><tbody>')
    for z in ZONES:
        ys = ", ".join(n(z["y0"] + i * PITCH) for i in range(z["bays"] + 1))
        h.append(f'<tr><td>{z["id"]} · {z["bays"]} alvéoles</td><td class="mono">{ys}</td><td class="num">{n(z["len"])} <span class="muted">(plan {n(z["plan_len"])})</span></td></tr>')
    h.append("</tbody></table>")
    return "".join(h)


def data3d(m):
    return dict(
        POST=POST, BAY=BAY, DEPTH=DEPTH, FLUE=FLUE, PAL_W=PAL_W, PAL_D=PAL_D, PAL_H=PAL_H,
        levels=LEVELS, H_RIVE=H_RIVE,
        refs={r: d["sec"] for r, d in REFS.items()},
        frames=[[f["x"], f["y"], f["h"]] for f in m["frames"]],
        bays=[[b["x"], b["y"], b["ref"]] for b in m["bays"]],
        slots=[[s["x"], s["y"], s["z"], s["r"], s["tone"]] for s in m["slots"] if not s["blocked"]],
        portiques=[[p["x1"], p["x2"], p["y"]] for p in m["portiques"]],
        prots=[[p["x"], p["y"], p["w"], p["d"]] for p in m["prots"]],
        columns=[[c["x"], c["y"], c["size"]] for c in COLUMNS],
        ext=[RACK_X[6] + RW + 3000, ZONES[1]["y0"] + ZONES[1]["len"]],
        aisle=[RACK_X[2] + RW + 3315 / 2, ZONES[1]["y0"]],
    )
