"""Modèle de l'implantation : géométrie, répartition des lisses, inventaire.
Toutes les cotes en mm. Origine X = nu intérieur du mur ouest, Y = about nord zone A."""
import json, random

POST, BAY, DEPTH, FLUE = 80, 3600, 1100, 250
PITCH = BAY + POST              # 3680 entraxe d'échelles
RW = 2 * DEPTH + FLUE           # 2450 rack double
LEVELS = [2044, 4044, 6044, 8044]
H_RIVE, H_INT = 10005, 8500
PAL_W, PAL_D, PAL_H = 800, 1200, 1750   # palette 800x1200, hauteur gerbage inclus (hypothèse)
PAL_KG = 400

REFS = {
    "O120": dict(label="LISSE 3600×120×50 ECOLOG ORANGE", short="Orange 120", sec=120, stock=346, token="lisse-o120"),
    "O110": dict(label="LISSE 3600×110×50 ECOLOG ORANGE", short="Orange 110", sec=110, stock=296, token="lisse-o110"),
    "J110": dict(label="LISSE 3600×110×50 C-LOG JAUNE",   short="Jaune 110",  sec=110, stock=334, token="lisse-j110"),
}

RACK_X = [5631]
for gap in [3000, 3000, 3315, 3314, 3000, 3000]:
    RACK_X.append(RACK_X[-1] + RW + gap)
AISLE_AFTER = [3000, 3000, 3315, 3314, 3000, 3000, 3000]   # largeur d'allée à l'est de chaque rack

ZONES = [
    dict(id="A", y0=0,     bays=3,  racks=7, plan_len=11123),
    dict(id="B", y0=0,     bays=10, racks=4, plan_len=36886),
]
for z in ZONES:
    z["len"] = z["bays"] * BAY + (z["bays"] + 1) * POST
ZONES[1]["y0"] = ZONES[0]["len"] + 4540
CROSS = (ZONES[0]["len"], ZONES[1]["y0"])

# Répartition : 1 face d'allée = 1 référence (section + couleur)
ALLOC = {
    "A": {"1W": "O120", "1E": "O110", "2W": "O110", "2E": "O110", "3W": "O110", "3E": "O110",
          "4W": "O110", "4E": "O110", "5W": "O110", "5E": "J110", "6W": "J110", "6E": "J110",
          "7W": "J110", "7E": "O110"},
    "B": {"1W": "O110", "1E": "O120", "2W": "O120", "2E": "O120", "3W": "O120",
          "3E": "J110", "4W": "J110", "4E": "J110"},
}
PORT_LINES = {"A": [0, 2, 3], "B": [0, 2, 4, 6, 8, 10]}

# Poteaux du bâtiment relevés à l'échelle sur le plan fourni (±300 mm)
COLUMNS = [
    dict(id="P1", x=RACK_X[2] + 448, y=ZONES[1]["y0"] + 15845, size=450, note="dans R3 face Ouest, zone B, alvéole 5"),
    dict(id="P2", x=RACK_X[2] + 448, y=ZONES[1]["y0"] + 32524, size=450, note="dans R3 face Ouest, zone B, alvéole 9"),
    dict(id="P3", x=RACK_X[2] + 448, y=CROSS[0] + 3570, size=450, note="allée transversale, axe R3"),
    dict(id="P4", x=RACK_X[5] + 576, y=CROSS[0] + 3570, size=450, note="allée transversale, axe R6"),
]


def build():
    rows, frames, beams, bays, portiques, prots, pairs = [], [], [], [], [], [], []
    for z in ZONES:
        zid, y0, nb = z["id"], z["y0"], z["bays"]
        nr = z["racks"]
        for k in range(1, nr + 1):
            X = RACK_X[k - 1]
            for side in "WE":
                rid = f"{zid}{k}{side}"
                ref = ALLOC[zid][f"{k}{side}"]
                rx = X if side == "W" else X + DEPTH + FLUE
                faces_inner = (side == "E" and k < nr) or (side == "W" and k > 1)
                row = dict(id=rid, zone=zid, rack=k, side=side, ref=ref, x=rx, y0=y0, bays=nb,
                           len=z["len"], aisle_x=(rx if side == "W" else rx + DEPTH))
                rows.append(row)
                for i in range(nb + 1):
                    end = i in (0, nb)
                    port = faces_inner and i in PORT_LINES[zid]
                    h = H_RIVE if (end or port) else H_INT
                    frames.append(dict(row=rid, i=i, x=rx, y=y0 + i * PITCH, h=h, rive=end,
                                       port=port and not end, zone=zid))
                for b in range(nb):
                    by = y0 + POST + b * PITCH
                    bays.append(dict(row=rid, b=b, x=rx, y=by, ref=ref))
                    for lv in LEVELS:
                        for face in (0, 1):
                            beams.append(dict(row=rid, ref=ref, x=rx + (0 if face == 0 else DEPTH - 50),
                                              y=by, z=lv, sec=REFS[ref]["sec"]))
            # paires d'échelles (entretoises)
            for i in range(nb + 1):
                hW = next(f["h"] for f in frames if f["row"] == f"{zid}{k}W" and f["i"] == i)
                hE = next(f["h"] for f in frames if f["row"] == f"{zid}{k}E" and f["i"] == i)
                pairs.append(dict(zone=zid, rack=k, i=i, n=4 if min(hW, hE) >= H_RIVE else 3))
            # protections bout d'allée (2 par rack double)
            prots.append(dict(x=X - 60, y=y0 - 260, w=RW + 120, d=160, zone=zid, rack=k, end="N"))
            prots.append(dict(x=X - 60, y=y0 + z["len"] + 100, w=RW + 120, d=160, zone=zid, rack=k, end="S"))
        # portiques entre racks du périmètre
        for k in range(1, nr):
            x1 = RACK_X[k - 1] + RW
            x2 = RACK_X[k]
            for i in PORT_LINES[zid]:
                portiques.append(dict(zone=zid, aisle=f"{k}-{k+1}", x1=x1, x2=x2, L=x2 - x1,
                                      y=y0 + i * PITCH + POST / 2, line=i))

    # emplacements palettes
    slots = []
    for bay in bays:
        for li, lv in enumerate([0] + LEVELS):
            for s in range(4):
                py = bay["y"] + 80 + s * (PAL_W + 80)
                blocked = None
                for c in COLUMNS:
                    if bay["x"] - 1 <= c["x"] <= bay["x"] + DEPTH and py - c["size"] / 2 < c["y"] < py + PAL_W + c["size"] / 2:
                        blocked = c["id"]
                slots.append(dict(row=bay["row"], b=bay["b"], lv=li, z=lv, x=bay["x"] + DEPTH / 2,
                                  y=py + PAL_W / 2, s=s, blocked=blocked))
    rnd = random.Random(7)
    for s in slots:
        s["r"] = round(rnd.random(), 4)
        s["tone"] = rnd.randint(0, 3)
    return dict(rows=rows, frames=frames, beams=beams, bays=bays, portiques=portiques,
                prots=prots, pairs=pairs, slots=slots)


def inventory(m):
    nf = len(m["frames"])
    tall = sum(1 for f in m["frames"] if f["h"] == H_RIVE)
    rive = sum(1 for f in m["frames"] if f["rive"])
    port = sum(1 for f in m["frames"] if f["port"])
    use = {r: 0 for r in REFS}
    for b in m["beams"]:
        use[b["ref"]] += 1
    nbeams = len(m["beams"])
    ent = sum(p["n"] for p in m["pairs"])
    trav = {}
    for p in m["portiques"]:
        trav[p["L"]] = trav.get(p["L"], 0) + 1
    beam_slots = [s for s in m["slots"] if s["lv"] > 0]
    blocked_beam = sum(1 for s in beam_slots if s["blocked"])
    nprot = len(m["prots"])
    G_PROT = 8
    lines = [
        ("Structure", "Échelle de rive / portique", f"H {H_RIVE:,} × P {DEPTH:,} mm · fût {POST} mm".replace(",", " "), tall,
         f"{rive} rives + {port} échelles de portique"),
        ("Structure", "Échelle intermédiaire", f"H {H_INT:,} × P {DEPTH:,} mm · fût {POST} mm".replace(",", " "), nf - tall,
         f"{nf} échelles au total − {tall} hautes"),
        ("Structure", "Entretoise de cheminée", "L 250 mm", ent,
         f"{len(m['pairs'])} paires d'échelles × 3 (× 4 sur les paires de 10 005 mm)"),
    ]
    for L in sorted(trav):
        lines.append(("Structure", "Traverse de portique d'allée", f"L {L:,} mm (largeur d'allée)".replace(",", " "), trav[L],
                      "1 par ligne de portique, toutes les 2 alvéoles + extrémités"))
    for r, d in REFS.items():
        q = use[r]
        delta = d["stock"] - q
        note = f"stock {d['stock']} → " + ("reliquat " + str(delta) if delta > 0 else ("à commander " + str(-delta) if delta < 0 else "stock soldé"))
        lines.append(("Lisses", d["label"], f"section {d['sec']}×50 · 4 PAL / niveau", q, note))
    lines += [
        ("Lisses", "Goupille de sécurité", "2 par lisse", nbeams * 2, f"{nbeams} lisses × 2"),
        ("Équipement", "Plateau fil", f"P {DEPTH} mm · 4 par niveau", len(beam_slots),
         f"{len(m['bays'])} alvéoles × 4 niveaux × 4 (−{blocked_beam} si poteaux P1/P2 confirmés)"),
        ("Équipement", "Plateau fil 880 × 1100", "passage pont / porte coupe-feu", 0, "aucun passage pont ni porte CF dans les alignements"),
        ("Équipement", "Butée podium", "1 par emplacement sur lisses · 4 niveaux", len(beam_slots),
         f"1 par palette sur niveaux 1 à 4 (−{blocked_beam} si poteaux confirmés)"),
        ("Sécurité", "Sabot de protection de pied", "côté allée", nf, "1 par échelle, montant côté allée"),
        ("Sécurité", "Protection de bout d'allée", f"pour rack double {RW} mm", nprot, f"{nprot // 2} racks doubles × 2 extrémités"),
        ("Ancrage", "Goujon d'ancrage", "échelles + sabots + protections", nf * 4 + nf * 4 + nprot * G_PROT,
         f"{nf}×4 échelles + {nf}×4 sabots + {nprot}×{G_PROT} protections"),
    ]
    return lines


def stats(m):
    slots = m["slots"]
    return dict(
        bays=len(m["bays"]), frames=len(m["frames"]), beams=len(m["beams"]),
        slots=len(slots), slots_ok=sum(1 for s in slots if not s["blocked"]),
        beam_slots=sum(1 for s in slots if s["lv"] > 0),
        racks=sum(z["racks"] for z in ZONES), rows=len(m["rows"]),
        portiques=len(m["portiques"]),
    )


if __name__ == "__main__":
    m = build()
    print(json.dumps(stats(m), indent=1))
    for l in inventory(m):
        print(l)
