"""
Use the backend's Qwen API to translate Chinese character data to English.
Run inside the backend container.
"""
import json
import sqlite3
import os
import re
from openai import OpenAI

CHINESE_RE = re.compile(r'[\u4e00-\u9fff]{2,}')

DB_PATH = "/app/data/nma.db"
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen3.6-flash"


def has_chinese(text):
    return bool(CHINESE_RE.search(text))


def translate_text(text, max_retries=2):
    """Translate Chinese text to English using Qwen."""
    if not text or not has_chinese(text):
        return text
    
    prompt = (
        "Translate the following Chinese text to natural English. "
        "This is character profile data for a fiction novel (werewolf/omegaverse pack dynamics). "
        "Keep proper nouns (character names, place names like 'Ashmark Pack', 'Alpha', 'Omega', "
        "'Pack', 'Luna', 'Bond') unchanged. Keep the tone in-character and literary. "
        "Return ONLY the translation, no explanations.\n\n"
        f"{text}"
    )
    
    for attempt in range(max_retries):
        try:
            client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
            resp = client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000,
            )
            translated = resp.choices[0].message.content.strip()
            return translated
        except Exception as e:
            print(f"  ⚠️  API error (attempt {attempt+1}): {e}", flush=True)
    
    return text  # fallback: return original if all retries fail


def main():
    if not QWEN_API_KEY or QWEN_API_KEY == "":
        print("❌ QWEN_API_KEY not set")
        return
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute(
        "SELECT name, traits, relations, motivation, arc_stage, backstory FROM characters"
    ).fetchall()
    
    for row in rows:
        name = row["name"]
        print(f"\n━━━ {name} ━━━", flush=True)
        
        updates = {}
        
        # Translate traits (JSON array of objects)
        raw_traits = row["traits"]
        if raw_traits:
            traits = json.loads(raw_traits) if isinstance(raw_traits, str) else raw_traits
            modified = False
            for trait in traits:
                for field in ("name", "description"):
                    val = trait.get(field, "")
                    if has_chinese(val):
                        translated = translate_text(val)
                        if translated != val:
                            trait[field] = translated
                            modified = True
                            print(f"  ✓ Trait '{val[:30]}...' → '{translated[:30]}...'")
            if modified:
                updates["traits"] = json.dumps(traits, ensure_ascii=False)
        
        # Translate relations (JSON object)
        raw_rels = row["relations"]
        if raw_rels:
            rels = json.loads(raw_rels) if isinstance(raw_rels, str) else raw_rels
            modified = False
            for key, val in rels.items():
                if has_chinese(val):
                    translated = translate_text(val)
                    if translated != val:
                        rels[key] = translated
                        modified = True
                        print(f"  ✓ Relation '{key}': translated")
            if modified:
                updates["relations"] = json.dumps(rels, ensure_ascii=False)
        
        # Translate text fields
        for field in ("motivation", "arc_stage", "backstory"):
            val = row[field]
            if val and has_chinese(val):
                translated = translate_text(val)
                if translated != val:
                    updates[field] = translated
                    print(f"  ✓ {field}: translated")
        
        if updates:
            updates["name"] = name
            conn.execute(
                """UPDATE characters SET
                    traits = ?, relations = ?, motivation = ?,
                    arc_stage = ?, backstory = ?, updated_at = datetime('now')
                WHERE name = ?""",
                (
                    updates.get("traits", row["traits"]),
                    updates.get("relations", row["relations"]),
                    updates.get("motivation", row["motivation"]),
                    updates.get("arc_stage", row["arc_stage"]),
                    updates.get("backstory", row["backstory"]),
                    name,
                ),
            )
            conn.commit()
            print(f"  ✅ {name} fully translated and updated")
        else:
            print(f"  ✓ No Chinese content found for {name}")
    
    conn.close()
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
