"""Reseed all 4 characters with rich English personality tags, varied confidence."""
import sqlite3, json

conn = sqlite3.connect("/data/nma.db")
conn.row_factory = sqlite3.Row

chars = [
    {
        "name": "Elizabeth Bennet",
        "aliases": json.dumps(["Lizzy", "Eliza"]),
        "traits": json.dumps([
            {"name": "Sharp-Witted", "category": "core", "description": "Her tongue cuts faster than most can think.", "confidence": 0.95},
            {"name": "Proud of Her Own Judgment", "category": "core", "description": "Trusts her instincts absolutely — and hates being wrong.", "confidence": 0.90},
            {"name": "Independent", "category": "core", "description": "Refuses to bend her happiness to anyone else's design.", "confidence": 0.90},
            {"name": "Playful", "category": "surface", "description": "Finds amusement in absurdity, even at her own expense.", "confidence": 0.80},
            {"name": "Quick to Judge", "category": "flaw", "description": "Forms strong first impressions and defends them ferociously.", "confidence": 0.65},
            {"name": "Stubborn", "category": "flaw", "description": "Once convinced, no counterargument gets through — for a while.", "confidence": 0.60},
            {"name": "Regretful", "category": "emergent", "description": "Carries the weight of her own mistakes longer than she shows.", "confidence": 0.45},
            {"name": "Fiercely Protective of Sisters", "category": "core", "description": "Jane's happiness is her happiness; Lydia's recklessness her shame.", "confidence": 0.90}
        ], ensure_ascii=False),
        "relations": json.dumps({
            "Jane Bennet": "Beloved elder sister, her moral anchor",
            "Mr. Darcy": "From contempt to love — a journey she never expected",
            "Lydia Bennet": "Foolish younger sister she constantly worries about",
            "Mr. Wickham": "Once charmed, now despised"
        }, ensure_ascii=False),
        "motivation": "To live authentically — on her own terms, by her own judgment.",
        "arc_stage": "awakening",
        "backstory": "Elizabeth Bennet, second of five daughters in the Bennet family of Hertfordshire. Clever, witty, and dangerously certain of her own perceptions. A man of wealth and pride caught her eye for all the wrong reasons — and then proved her entirely wrong.",
        "embedding_centroid": "null",
        "preferred_profile": "null"
    },
    {
        "name": "Fitzwilliam Darcy",
        "aliases": json.dumps(["Mr. Darcy"]),
        "traits": json.dumps([
            {"name": "Proud", "category": "core", "description": "His station is a fortress he was raised to never lower the drawbridge of.", "confidence": 0.95},
            {"name": "Deeply Loyal", "category": "core", "description": "Once he commits — to a person, a duty, a principle — he never wavers.", "confidence": 0.90},
            {"name": "Fundamentally Honourable", "category": "core", "description": "His moral compass is absolute, even when it costs him everything.", "confidence": 0.90},
            {"name": "Reserved to a Fault", "category": "surface", "description": "Silence is his default; strangers mistake it for coldness.", "confidence": 0.85},
            {"name": "Protective of His Circle", "category": "core", "description": "Georgiana's guardian, Pemberley's steward — he carries everyone.", "confidence": 0.80},
            {"name": "Socially Anxious Among Strangers", "category": "flaw", "description": "Large gatherings paralyze his tongue; he retreats into formality.", "confidence": 0.70},
            {"name": "Intolerant of Fools", "category": "flaw", "description": "Suffers stupidity poorly — a flaw he is slowly learning to admit.", "confidence": 0.50},
            {"name": "Secretly Generous", "category": "emergent", "description": "His charity is anonymous, his help invisible. He prefers it that way.", "confidence": 0.30}
        ], ensure_ascii=False),
        "relations": json.dumps({
            "Elizabeth Bennet": "The woman who humbled him — and elevated him",
            "Georgiana Darcy": "Beloved younger sister, his sole family",
            "Charles Bingley": "Closest friend, temperamental opposite",
            "Lady Catherine de Bourgh": "Aunt, a figure of obligation and irritation"
        }, ensure_ascii=False),
        "motivation": "To be worthy of the name he carries — and the woman who saw through him.",
        "arc_stage": "transformation",
        "backstory": "Fitzwilliam Darcy, master of Pemberley, of one of the oldest families in England. Raised to know his worth and never question his station. Then a sharp-tongued woman from Hertfordshire dismantled every assumption he held about himself — and he fell in love with her for it.",
        "embedding_centroid": "null",
        "preferred_profile": "null"
    },
    {
        "name": "Caelan Ashmark",
        "aliases": json.dumps(["Caelan"]),
        "traits": json.dumps([
            {"name": "Order-Driven", "category": "core", "description": "He has never questioned the framework he operates within — it simply is.", "confidence": 0.95},
            {"name": "Brilliant Strategist", "category": "core", "description": "Reads a room's power structure in under thirty seconds. Never opens negotiations.", "confidence": 0.90},
            {"name": "Controlled Demeanour", "category": "core", "description": "Every emotion is buried beneath stillness. His anger is quieter than calm.", "confidence": 0.92},
            {"name": "Chronically Insomniac", "category": "surface", "description": "Sleep abandoned him years ago. He treats it as irrelevant.", "confidence": 0.85},
            {"name": "Blind to Systemic Oppression", "category": "flaw", "description": "Not malice — a cognitive boundary. The invisible infrastructure that benefits him simply escapes notice.", "confidence": 0.75},
            {"name": "Denial About the Bond", "category": "emergent", "description": "The Bond struck an object his worldview cannot explain. His first instinct: reject the data.", "confidence": 0.80},
            {"name": "Reverent Toward His Father", "category": "core", "description": "Admires Edran Ashmark absolutely, unaware of the strings behind the throne.", "confidence": 0.70},
            {"name": "Incurably Curious (Hidden)", "category": "emergent", "description": "A crack in the armour — that Omega interests him more than he will admit to himself.", "confidence": 0.40}
        ], ensure_ascii=False),
        "relations": json.dumps({
            "Mira Goldthorn": "Luna — political marriage, no warmth",
            "Edran Ashmark": "Deceased father, former Alpha, his lodestar",
            "Lena": "Omega kitchen worker, Bond target, unclassifiable variable",
            "Corvan Ashmark": "Beta advisor, younger uncle"
        }, ensure_ascii=False),
        "motivation": "To maintain Ashmark Pack's order and stability — and understand why one Omega shattered it.",
        "arc_stage": "denial",
        "backstory": "Caelan Ashmark, 32, Alpha of Ashmark Pack. At a recent Pack banquet, his Bond — a biological certainty he took for granted — triggered to an Omega kitchen worker. His world has not stopped tilting since.",
        "embedding_centroid": "null",
        "preferred_profile": "[0.7010468300000001, 0.6299503299999998, 0.34059051, 0.7646419200000001, 0.26282609]"
    },
    {
        "name": "Lena",
        "aliases": json.dumps(["Lena"]),
        "traits": json.dumps([
            {"name": "Calm Under Pressure", "category": "core", "description": "Slow is fast. She never raises her voice, even in crisis.", "confidence": 0.95},
            {"name": "Invisible by Design", "category": "core", "description": "22 years of learning to disappear. She wears compliance like camouflage.", "confidence": 0.90},
            {"name": "Quietly Observant", "category": "core", "description": "Notices everything — scents, micro-expressions, shifts in room temperature.", "confidence": 0.90},
            {"name": "Grief-Bound to Maren", "category": "core", "description": "Her mentor died three months ago. The why haunts her more than the loss.", "confidence": 0.85},
            {"name": "Resistant to Authority", "category": "surface", "description": "Performs perfect submission while holding her own silent judgment.", "confidence": 0.80},
            {"name": "Sensitive to Scent", "category": "surface", "description": "Can read a room's emotional state from the air alone.", "confidence": 0.75},
            {"name": "Fearful of Being Seen", "category": "core", "description": "The Alpha looked at her once. Her first instinct was pure terror.", "confidence": 0.85},
            {"name": "Soft at the Core", "category": "emergent", "description": "Despite every defence, she still hopes — a vulnerability she despises.", "confidence": 0.50},
            {"name": "Ravenously Curious", "category": "emergent", "description": "The question 'why' is the most dangerous thing about her.", "confidence": 0.35}
        ], ensure_ascii=False),
        "relations": json.dumps({
            "Caelan Ashmark": "The Alpha who saw her — inexplicable, terrifying",
            "Maren": "Dead mentor, the one who taught her to survive",
            "Nell": "Young Omega in the kitchen she tries to protect",
            "Beta Theron": "Pack Beta, overseer of the kitchen staff"
        }, ensure_ascii=False),
        "motivation": "To survive — and to understand why Maren died for her.",
        "arc_stage": "awakening",
        "backstory": "Lena, 22, Omega in the Ashmark Pack's kitchen. Three months ago her mentor Maren died under unexplained circumstances. She has spent her entire life cultivating invisibility — until an Alpha's gaze landed on her and refused to leave.",
        "embedding_centroid": "null",
        "preferred_profile": "null"
    }
]

# Clear and reseed
for char in chars:
    conn.execute("DELETE FROM characters WHERE name = ?", (char["name"],))
    conn.execute(
        "INSERT INTO characters (name, aliases, traits, relations, motivation, arc_stage, backstory, embedding_centroid, preferred_profile) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (char["name"], char["aliases"], char["traits"], char["relations"],
         char["motivation"], char["arc_stage"], char["backstory"],
         char["embedding_centroid"], char["preferred_profile"])
    )
    print(f"  ✓ Seeded {char['name']}")

conn.commit()
conn.close()
print("Done — all 4 characters reseeded.")
