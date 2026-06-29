"""Update Lena's character profile with rich backstory from the novel."""
import sqlite3, json

DB = r"D:\workspace\narrative-memory-agent\data\nma.db"

LENA = {
    "name": "Lena",
    "aliases": ["Lena"],
    "traits": [
        {"name": "Calm Under Pressure", "category": "core",
         "description": "In the chaos of the Pack kitchen — shouting Betas, burning pots — Lena never raises her voice.", "confidence": 0.90},
        {"name": "Invisible by Design", "category": "core",
         "description": "Stay in the kitchen, stay invisible, stay alive. She drops her shoulders, lowers her chin.", "confidence": 0.90},
        {"name": "Quietly Observant", "category": "core",
         "description": "She notices everything — dampness in the thyme, shaking hands, the exact count of winter wheat.", "confidence": 0.85},
        {"name": "Grief-Bound to Maren", "category": "surface",
         "description": "Her mentor died three months ago. She still reaches for Maren\'s voice in every crisis.", "confidence": 0.80},
        {"name": "Resistant to Authority", "category": "surface",
         "description": "Performs submission perfectly while holding her own judgment in reserve.", "confidence": 0.75},
    ],
    "relations": {"Caelan Ashmark": "The Alpha who saw her", "Maren": "Dead mentor",
                   "Nell": "Young Omega in the kitchen", "Beta Theron": "Pack Beta",
                   "Tess": "Kitchen assistant"},
    "motivation": "To survive. Being seen is the most dangerous thing that has ever happened to her.",
    "arc_stage": "awakening — 22 years of careful invisibility shattered by a single glance.",
    "backstory": "Lena is a 22-year-old Omega in the Ashmark Pack. She has worked in the Pack House kitchen since childhood, trained by Maren. Maren died three months ago in the ice. Lena has never been to the main hall, never spoken to the Alpha, never been seen — until now.",
}

db = sqlite3.connect(DB)
cur = db.execute("SELECT rowid FROM characters WHERE name='Lena'")
if not cur.fetchone():
    print("Lena not found")
else:
    db.execute("""UPDATE characters SET aliases=?, traits=?, relations=?, motivation=?, arc_stage=?, backstory=? WHERE name=?""",
               (json.dumps(LENA["aliases"]), json.dumps(LENA["traits"]), json.dumps(LENA["relations"]),
                LENA["motivation"], LENA["arc_stage"], LENA["backstory"], LENA["name"]))
    db.commit()
    print("Lena profile updated!")

db.close()
