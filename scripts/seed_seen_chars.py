"""Seed Caelan Ashmark and Lena into the NMA database."""
import sqlite3, json

conn = sqlite3.connect("/data/nma.db")
conn.row_factory = sqlite3.Row

chars = [
    {
        "name": "Caelan Ashmark",
        "aliases": json.dumps(["Caelan"]),
        "traits": json.dumps([
            {"name": "秩序驱动", "category": "core", "description": "他一直在现有框架内做到最好，从未质疑过框架本身。Pack秩序对他来说像空气一样自然。", "confidence": 1.0},
            {"name": "极其聪明", "category": "core", "description": "谈判时从不先开价，能在30秒内判断出房间里的真正权力核心。", "confidence": 1.0},
            {"name": "克制", "category": "core", "description": "情绪从来不在表面，藏在动作和沉默里。他的愤怒比平静更安静。", "confidence": 1.0},
            {"name": "长期失眠", "category": "surface", "description": "长期的安静的失眠。他不觉得这是问题。", "confidence": 0.9},
            {"name": "不屑于压迫也不屑于看见", "category": "core", "description": "他不会主动压迫Omega，但他不会看见他们。不是恶意，是他的认知边界。", "confidence": 1.0},
            {"name": "认知盲区", "category": "core", "description": "他尊敬父亲，不知道他是被控制的。这是他最难触碰的伤。", "confidence": 0.9},
            {"name": "对Bond的否认", "category": "surface", "description": "Bond击中了一个他的世界观无法解释的对象。他的第一反应是：这不对。", "confidence": 0.85}
        ], ensure_ascii=False),
        "relations": json.dumps({
            "Mira Goldthorn": "Luna（政治婚姻），相敬如宾",
            "Edran Ashmark": "已故之父，前Alpha",
            "Lena": "Omega厨房帮工，Bond对象",
            "Corvan Ashmark": "Beta顾问，自己的小叔"
        }, ensure_ascii=False),
        "motivation": "To maintain Ashmark Pack's order and stability.",
        "arc_stage": "denial",
        "backstory": "Caelan Ashmark is the 32-year-old Alpha of Ashmark Pack. At a recent Pack banquet, his Bond triggered to an Omega kitchen worker.",
        "embedding_centroid": "null",
        "preferred_profile": "[0.7010468300000001, 0.6299503299999998, 0.34059051, 0.7646419200000001, 0.26282609]"
    },
    {
        "name": "Lena",
        "aliases": json.dumps(["Lena"]),
        "traits": json.dumps([
            {"name": "Calm Under Pressure", "category": "core", "description": "Slow is fast. In chaos, Lena never raises her voice.", "confidence": 0.95},
            {"name": "Invisible by Design", "category": "core", "description": "22 years of learning to disappear.", "confidence": 0.95},
            {"name": "Quietly Observant", "category": "core", "description": "She notices everything.", "confidence": 0.95},
            {"name": "Grief-Bound to Maren", "category": "core", "description": "Her mentor died three months ago.", "confidence": 0.9},
            {"name": "Resistant to Authority", "category": "surface", "description": "Performs submission perfectly while holding her own judgment.", "confidence": 0.85},
            {"name": "Sensitive to Scent", "category": "surface", "description": "Can read a room from its smell.", "confidence": 0.85},
            {"name": "Fearful of Being Seen", "category": "surface", "description": "The Alpha looked at her once. Her first reaction was terror.", "confidence": 0.9}
        ], ensure_ascii=False),
        "relations": json.dumps({
            "Caelan Ashmark": "The Alpha who saw her",
            "Maren": "Dead mentor",
            "Nell": "Young Omega in the kitchen",
            "Beta Theron": "Pack Beta, oversees kitchen"
        }, ensure_ascii=False),
        "motivation": "To survive — and to understand why Maren died for her.",
        "arc_stage": "awakening",
        "backstory": "Lena is a 22-year-old Omega in the Ashmark Pack. Three months ago her mentor Maren died. She has never been seen — until now.",
        "embedding_centroid": "null",
        "preferred_profile": "null"
    }
]

for char in chars:
    existing = conn.execute("SELECT name FROM characters WHERE name = ?", (char["name"],)).fetchone()
    if existing:
        print(f"  {char['name']} already exists, skipping")
        continue
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
print("Done.")
