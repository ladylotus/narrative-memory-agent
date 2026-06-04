"""Test ingestion pipeline end-to-end with a Caelvorn excerpt.

Run:  python backend/scripts/test_ingestion.py
       (from ~/forge/narrative-memory-agent/)
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.ingestion import IngestionService


async def main():
    # Read a sample chapter excerpt
    excerpt_path = Path.home() / "Caelvorn Series" / "Book1 Seen" / "Seen1-5.md"
    text = excerpt_path.read_text(encoding="utf-8")

    # Use just the first ~2000 chars for a quick test
    sample = text[:2500]

    svc = IngestionService()
    print("🔍 Running ingestion on Caelvorn Ch.1 excerpt...")
    result = await svc.process_text(sample, title="Seen Ch.1 (test excerpt)")

    print(f"\n✅ Ingestion complete!")
    print(f"  Chunks processed:  {result['chunks_processed']}")
    print(f"  Events extracted:  {result['events_extracted']}")
    print(f"  Characters found:  {result['characters_found']}")
    print(f"  New characters:    {result['new_characters']}")

    # Verify events stored in EpisodicMemory
    from app.memory.episodic import EpisodicMemory
    epi = EpisodicMemory()
    if result['characters_found']:
        for char in result['characters_found'][:3]:
            events = epi.get_events(protagonist=char, limit=3)
            print(f"\n  Events for {char}: {len(events)} stored")

    # Verify characters in DB
    from app.database import list_characters, get_character
    all_chars = list_characters()
    print(f"\n  Total characters in DB: {len(all_chars)}")
    for c in all_chars:
        if c in result['characters_found']:
            profile = get_character(c)
            if profile:
                traits = profile.get("traits", [])
                print(f"    {c}: {len(traits)} traits")


if __name__ == "__main__":
    asyncio.run(main())
