"""Dump Lena, Caelan, and other Seen characters from local DB."""
import sqlite3, json

conn = sqlite3.connect('/home/ubuntu/forge/narrative-memory-agent/data/nma.db')
conn.row_factory = sqlite3.Row

for name in ['Caelan Ashmark', 'Lena', 'Maren', 'Nell', 'Beta Theron']:
    row = conn.execute('SELECT * FROM characters WHERE name = ?', (name,)).fetchone()
    if not row:
        print(f'XXX {name}: NOT FOUND')
        continue
    d = dict(row)
    print(f'=== {name} ===')
    for col in ['aliases','traits','relations','motivation','arc_stage','backstory','embedding_centroid','preferred_profile']:
        val = d.get(col)
        if val and col in ('aliases','traits','relations'):
            parsed = json.loads(val)
            print(f'{col}: {json.dumps(parsed, ensure_ascii=False)}')
        else:
            print(f'{col}: {repr(val)}')
    print()

conn.close()
