"""
Script to find and translate Chinese content in character traits/descriptions
in the NMA database. Run inside the backend container or on the host with
access to the SQLite database file.

Usage (inside Docker):
  docker exec -it nma-backend python /scripts/translate_chinese_traits.py

Usage (on host with volume access):
  python scripts/translate_chinese_traits.py --db-path /path/to/nma.db
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

# Chinese character range
CHINESE_RE = re.compile(r'[\u4e00-\u9fff]+')

# ── Translation map for known Chinese trait patterns ──────
# These are the common trait names from the Caelvorn novel ingestion
TRANSLATIONS = {
    # Trait/Pattern names
    "秩序驱动": "Order-Driven",
    "规则导向": "Rule-Oriented",
    "执行者": "Executor",
    "战略思维": "Strategic Thinker",
    "分析型": "Analytical",
    "直觉主导": "Intuition-Led",
    "情感克制": "Emotionally Restrained",
    "内省": "Introspective",
    "行动派": "Action-Oriented",
    "保护者": "Protector",
    "观察者": "Observer",
    "决策果断": "Decisive",
   
    # Common description fragments
    "倾向于": "Tends to be ",
    "在压力下": "Under pressure, ",
    "面对冲突": "When facing conflict, ",
    "表现出": "Exhibits ",
    "有强烈的": "Has a strong sense of ",
    "偏好": "Prefers ",
    "擅长": "Skilled at ",
   
    # Arc stages
    "初期": "Early Stage",
    "发展中": "Developing",
    "成熟": "Mature",
    "蜕变": "Transformation",
    "觉醒": "Awakening",
   
    # Motivation / Backstory fragments
    "寻找": "Searching for ",
    "保护": "Protecting ",
    "证明": "Proving ",
    "理解": "Understanding ",
    "掌控": "Taking control of ",
    "秩序": "Order",
    "混沌": "Chaos",
    "力量": "Power",
    "真相": "Truth",
    "自由": "Freedom",
   
    # Relationship descriptions
    "盟友": "Ally",
    "对手": "Rival",
    "导师": "Mentor",
    "追随者": "Follower",
    "敌人": "Enemy",
    "伙伴": "Partner",
    "陌生": "Stranger",
}


def has_chinese(text: str) -> bool:
    """Check if text contains Chinese characters."""
    return bool(CHINESE_RE.search(text))


def translate_text(text: str) -> str:
    """Translate Chinese text to English using the lookup table + pattern matching."""
    result = text
    for cn, en in sorted(TRANSLATIONS.items(), key=lambda x: -len(x[0])):
        result = result.replace(cn, en)
    # If there are still Chinese characters, mark them for manual review
    remaining = CHINESE_RE.findall(result)
    if remaining:
        print(f"  ⚠️  Untranslated Chinese found: {remaining}")
        print(f"     Original: {text[:100]}")
        print(f"     Partial:  {result[:100]}")
    return result


def traverse_and_translate(obj, path=""):
    """Recursively traverse a dict/list and translate Chinese strings."""
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            new_path = f"{path}.{key}"
            if isinstance(value, str) and has_chinese(value):
                translated = translate_text(value)
                if translated != value:
                    obj[key] = translated
                    print(f"  ✓ [{new_path}]: translated")
            elif isinstance(value, (dict, list)):
                traverse_and_translate(value, new_path)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]"
            if isinstance(item, str) and has_chinese(item):
                translated = translate_text(item)
                if translated != item:
                    obj[i] = translated
                    print(f"  ✓ [{new_path}]: translated")
            elif isinstance(item, (dict, list)):
                traverse_and_translate(item, new_path)


def main():
    # Determine DB path
    if "--db-path" in sys.argv:
        idx = sys.argv.index("--db-path")
        db_path = Path(sys.argv[idx + 1])
    else:
        # Default: inside Docker container
        db_path = Path("/app/data/nma.db")

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        sys.exit(1)

    print(f"📁 Database: {db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Get all characters
    rows = conn.execute("SELECT name, traits, relations, motivation, arc_stage, backstory FROM characters").fetchall()

    if not rows:
        print("No characters found in database.")
        return

    modified_any = False

    for row in rows:
        name = row["name"]
        print(f"\n━━━ Checking: {name} ━━━")

        has_cn = any(
            row[k] and isinstance(row[k], str) and has_chinese(row[k])
            for k in ("traits", "relations", "motivation", "arc_stage", "backstory")
        )

        if not has_cn:
            print("  ✓ All English, skipping")
            continue

        print(f"  Found Chinese content, translating...")

        # Build update dict
        update = {}
        for field in ("traits", "relations", "motivation", "arc_stage", "backstory"):
            raw = row[field]
            if not raw:
                continue
            try:
                parsed = json.loads(raw) if isinstance(raw, str) else raw
            except (json.JSONDecodeError, TypeError):
                parsed = raw

            if isinstance(parsed, str) and has_chinese(parsed):
                translated = translate_text(parsed)
                if translated != parsed:
                    update[field] = json.dumps(translated, ensure_ascii=False)
                    modified_any = True
            elif isinstance(parsed, (dict, list)):
                traverse_and_translate(parsed)
                update[field] = json.dumps(parsed, ensure_ascii=False)
                modified_any = True

        if update:
            update["name"] = name
            conn.execute(
                """UPDATE characters SET
                    traits = ?, relations = ?, motivation = ?,
                    arc_stage = ?, backstory = ?, updated_at = datetime('now')
                WHERE name = ?""",
                (
                    update.get("traits", row["traits"]),
                    update.get("relations", row["relations"]),
                    update.get("motivation", row["motivation"]),
                    update.get("arc_stage", row["arc_stage"]),
                    update.get("backstory", row["backstory"]),
                    name,
                ),
            )
            conn.commit()
            print(f"  ✅ Updated {name}")

    # Also check events table
    print(f"\n━━━ Checking events table ━━━")
    ev_rows = conn.execute("SELECT id, protagonist, summary FROM events").fetchall()
    for ev in ev_rows:
        if has_chinese(ev["summary"]):
            translated = translate_text(ev["summary"])
            if translated != ev["summary"]:
                conn.execute(
                    "UPDATE events SET summary = ? WHERE id = ?",
                    (translated, ev["id"]),
                )
                conn.commit()
                print(f"  ✅ Translated event '{ev['id']}' ({ev['protagonist']})")

    if not modified_any:
        print("\nNo characters needed translation.")
    else:
        print("\n✅ Translation complete.")

    conn.close()


if __name__ == "__main__":
    main()
