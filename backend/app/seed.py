"""Seed the database with demo characters — Elizabeth Bennet & Fitzwilliam Darcy.

Pride and Prejudice (Jane Austen, 1813) for the Qwen Cloud Global AI Hackathon.
Familiar to a global audience; rich character arcs ideal for OOC detection
and narrative memory demos. Also seeds demo episodic events so the memory
system has data to retrieve on first use.
"""

from __future__ import annotations

from app.database import get_character, upsert_character
from app.memory.episodic import EpisodicMemory
from app.models.event import NarrativeEvent


ELIZABETH_BENNET = {
    "name": "Elizabeth Bennet",
    "aliases": ["Elizabeth", "Lizzy", "Eliza"],
    "traits": [
        {
            "name": "Sharp-Witted",
            "category": "core",
            "description": "Quick to judge character and fond of laughing at folly. Her intellect is her defining feature — she reads people fast and trusts her reading absolutely.",
            "confidence": 0.95,
        },
        {
            "name": "Proud of Her Own Judgment",
            "category": "core",
            "description": "Confident in her ability to read people — which makes her blind to her own blind spots. She formed an unfavourable impression of Darcy at the first ball and has been confirming it ever since.",
            "confidence": 0.90,
        },
        {
            "name": "Loyal to Family",
            "category": "surface",
            "description": "Despite being frequently embarrassed by her mother and younger sisters, she defends them fiercely when outsiders attack. She would not trade them.",
            "confidence": 0.85,
        },
        {
            "name": "Independent",
            "category": "core",
            "description": "Refused Mr. Collins's hand, refused Darcy's first proposal, and would refuse any marriage that does not offer genuine affection and respect. She will not sell herself for security.",
            "confidence": 0.90,
        },
        {
            "name": "Warm Once Trust Is Earned",
            "category": "surface",
            "description": "Cold and playful with strangers; warm, open, and deeply affectionate with those she respects. Jane has her full heart; her father is her intellectual companion.",
            "confidence": 0.85,
        },
    ],
    "relations": {
        "Jane Bennet": "Beloved elder sister, confidante, the kindest person she knows",
        "Fitzwilliam Darcy": "Proud and disagreeable gentleman — or so she believes. Her feelings are… changing.",
        "George Wickham": "Charming officer whose story she believed without question; now she is less certain",
        "Mr. Collins": "Pompous cousin who proposed to her; she refused him firmly",
        "Lydia Bennet": "Wild youngest sister, source of perpetual anxiety",
    },
    "motivation": "To marry for genuine affection and mutual respect, not convenience or financial security. She would rather be an old maid than sell her happiness.",
    "arc_stage": "prejudice — confident in her poor first impression of Darcy, utterly convinced of Wickham's virtue. Her judgment has not yet been tested.",
    "backstory": (
        "Elizabeth Bennet is the second of five daughters of the Bennet family of Longbourn, Hertfordshire. "
        "She is 20 years old, the favourite child of her intelligent but indolent father, who nurtured her quick mind and love of reading. "
        "Her mother's single obsession is to marry off all five daughters before Mr. Bennet's estate passes to Mr. Collins by entail. "
        "At a local ball, she met Fitzwilliam Darcy — a wealthy, reserved gentleman from Derbyshire who was seen dancing only twice and refused to be introduced to anyone new. "
        "She overheard him say she was 'tolerable but not handsome enough to tempt me.' She has never forgotten it. "
        "More recently, she met Mr. Wickham, a charming militia officer who told her a devastating story of how Darcy cheated him out of his inheritance. "
        "She believed every word. At this moment, she is staying at the Hunsford parsonage with her friend Charlotte Collins — and Darcy is visiting his aunt, Lady Catherine de Bourgh, nearby."
    ),
    "embedding_centroid": None,
    "preferred_profile": None,
}

FITZWILLIAM_DARCY = {
    "name": "Fitzwilliam Darcy",
    "aliases": ["Darcy", "Mr. Darcy"],
    "traits": [
        {
            "name": "Proud",
            "category": "core",
            "description": "Highly conscious of his station, uncomfortable with strangers. What others perceive as arrogance is partly genuine reserve — but also real pride in his name, his estate, and his standards.",
            "confidence": 0.95,
        },
        {
            "name": "Deeply Loyal",
            "category": "core",
            "description": "To his sister Georgiana, to his friend Bingley, to Pemberley itself. Those under his protection have his full devotion — even at great personal cost.",
            "confidence": 0.90,
        },
        {
            "name": "Reserved to a Fault",
            "category": "surface",
            "description": "Cannot make small talk. Hates entering a room of strangers. His silence is almost universally mistaken for disdain — and he does little to correct the impression.",
            "confidence": 0.85,
        },
        {
            "name": "Fundamentally Honourable",
            "category": "core",
            "description": "When he understands what is right, he does it — even when it costs him personally. He paid for Wickham's commission, endured Lady Catherine's fury, and approached Bingley about Jane entirely because Elizabeth had opened his eyes to his own failings.",
            "confidence": 0.90,
        },
        {
            "name": "Capable of Transformation",
            "category": "core",
            "description": "His love for Elizabeth forced him to examine his own character for the first time. He is not static — he reads her rebuke and genuinely changes. This capacity for self-examination is his deepest trait.",
            "confidence": 0.85,
        },
    ],
    "relations": {
        "Elizabeth Bennet": "The woman who makes him question everything he thought he knew about himself. He proposed and was refused — devastatingly.",
        "Georgiana Darcy": "Beloved younger sister, he is fiercely protective of her after Wickham's near-elopement",
        "Charles Bingley": "His best friend — easygoing, warm, everything Darcy is not. He trusts Bingley's heart more than Bingley's judgment.",
        "Lady Catherine de Bourgh": "His aunt, domineering, expects him to marry her daughter Anne",
        "George Wickham": "Childhood companion turned lifelong enemy. Wickham tried to elope with Georgiana for her fortune.",
    },
    "motivation": "To be worthy of Elizabeth's respect — even if she never returns his affection. He is learning that his wealth and name are not enough to earn a woman of real worth.",
    "arc_stage": "rejection — has just been refused by Elizabeth. His proposal was arrogant and ill-delivered; her refusal shattered his self-image. He is beginning to see himself through her eyes.",
    "backstory": (
        "Fitzwilliam Darcy is the master of Pemberley, one of the finest estates in Derbyshire. He is 28 years old. "
        "Raised by a loving father who taught him generosity of means but left him socially isolated, Darcy grew up believing that his rank and wealth made him superior — a belief no one challenged until Elizabeth Bennet. "
        "His close friend Charles Bingley leased Netherfield Park in Hertfordshire, and Darcy accompanied him. At a local assembly, he refused to dance with anyone outside his party and was overheard disparaging Elizabeth Bennet. "
        "Since then, he has found himself increasingly drawn to her — her fine eyes, her quick wit, her utter indifference to his fortune. "
        "He separated Bingley from Jane Bennet because he believed Jane indifferent. He hid the truth about Wickham's character. "
        "Days ago at Hunsford, he proposed to Elizabeth — not romantically, but as if conferring an honour. She refused him with devastating clarity: his pride, his cruelty to Wickham, his interference with Jane and Bingley. "
        "He left Hunsford in shock. For the first time in his life, he is looking at himself honestly."
    ),
    "embedding_centroid": None,
    "preferred_profile": None,
}


# ── Seed events ──────────────────────────────────────────

_EVENTS_ELIZABETH = [
    {
        "id": "eliza_meryton_ball",
        "chapter": 1,
        "summary": (
            "At the Meryton assembly, Elizabeth overheard Mr. Darcy tell Bingley "
            "that she is 'tolerable, but not handsome enough to tempt me.' "
            "She was standing within hearing distance. She told her friends the story "
            "with great spirit — but it stung."
        ),
        "importance": 0.75,
        "zwaan_dims": {
            "time": "evening",
            "space": "Meryton assembly rooms",
            "protagonist": "Elizabeth",
            "causality": "social introduction",
            "intent": "observe",
        },
    },
    {
        "id": "eliza_netherfield_jane",
        "chapter": 2,
        "summary": (
            "Jane fell ill while dining at Netherfield. Elizabeth walked three miles "
            "through muddy fields to care for her, arriving with her petticoats six inches deep in mud. "
            "Darcy watched her with an expression she could not read — part disapproval, part something else."
        ),
        "importance": 0.70,
        "zwaan_dims": {
            "time": "morning",
            "space": "Netherfield Park",
            "protagonist": "Elizabeth",
            "causality": "sibling concern",
            "intent": "caregiving",
        },
    },
    {
        "id": "eliza_collins_proposal",
        "chapter": 3,
        "summary": (
            "Mr. Collins proposed to Elizabeth. She refused him clearly and firmly, "
            "though her mother is furious and insists she accept. "
            "Elizabeth stood her ground — she will not marry a man she cannot respect, "
            "even to save her family from financial ruin."
        ),
        "importance": 0.80,
        "zwaan_dims": {
            "time": "afternoon",
            "space": "Longbourn",
            "protagonist": "Elizabeth",
            "causality": "social obligation",
            "intent": "refuse",
        },
    },
    {
        "id": "eliza_wickham_story",
        "chapter": 3,
        "summary": (
            "At a party in Meryton, Mr. Wickham told Elizabeth a devastating story: "
            "Darcy's father had promised him a valuable living, but Darcy denied it out of jealousy. "
            "Elizabeth believed Wickham entirely. This confirmed every bad opinion she had formed of Darcy."
        ),
        "importance": 0.85,
        "zwaan_dims": {
            "time": "evening",
            "space": "Meryton",
            "protagonist": "Elizabeth",
            "causality": "conversation",
            "intent": "trust",
        },
    },
    {
        "id": "eliza_hunsford_proposal",
        "chapter": 5,
        "summary": (
            "Darcy proposed to Elizabeth at Hunsford Parsonage. His proposal was arrogant — "
            "he spoke of his struggle against his inferior connections, his certainty of her acceptance. "
            "She refused him with devastating clarity: his pride, his cruelty to Wickham, "
            "his interference with Jane and Bingley. She told him he was the last man in the world "
            "she could ever be prevailed upon to marry. He left in shock."
        ),
        "importance": 0.95,
        "zwaan_dims": {
            "time": "morning",
            "space": "Hunsford Parsonage",
            "protagonist": "Elizabeth",
            "causality": "proposal",
            "intent": "refuse",
        },
    },
    {
        "id": "eliza_darcy_letter",
        "chapter": 5,
        "summary": (
            "The morning after the proposal, Darcy handed Elizabeth a letter. "
            "In it, he admitted separating Bingley from Jane — but defended it based on "
            "what he believed was Jane's indifference. He also revealed the truth about Wickham: "
            "Wickham attempted to elope with Darcy's fifteen-year-old sister Georgiana for her fortune. "
            "Elizabeth read the letter multiple times, her opinion of Darcy beginning to shift."
        ),
        "importance": 0.90,
        "zwaan_dims": {
            "time": "morning",
            "space": "Hunsford",
            "protagonist": "Elizabeth",
            "causality": "letter",
            "intent": "reflect",
        },
    },
]

_EVENTS_DARCY = [
    {
        "id": "darcy_meryton_ball",
        "chapter": 1,
        "summary": (
            "At the Meryton assembly, Darcy danced only with Bingley's sisters and refused "
            "to be introduced to anyone new. When Bingley urged him to dance with Elizabeth Bennet, "
            "Darcy replied that she was 'tolerable, but not handsome enough to tempt me.' "
            "Miss Bennet overheard him. He did not think much of it at the time."
        ),
        "importance": 0.75,
        "zwaan_dims": {
            "time": "evening",
            "space": "Meryton assembly rooms",
            "protagonist": "Darcy",
            "causality": "social introduction",
            "intent": "reject",
        },
    },
    {
        "id": "darcy_netherfield_observation",
        "chapter": 2,
        "summary": (
            "While Elizabeth stayed at Netherfield nursing Jane, Darcy found himself "
            "watching her constantly. Her fine eyes, her easy laugh, her utter indifference to his opinion — "
            "she was unlike any woman he had met. He began to be attracted against his better judgment."
        ),
        "importance": 0.70,
        "zwaan_dims": {
            "time": "evening",
            "space": "Netherfield Park",
            "protagonist": "Darcy",
            "causality": "proximity",
            "intent": "observe",
        },
    },
    {
        "id": "darcy_separates_bingley",
        "chapter": 3,
        "summary": (
            "Darcy persuaded Bingley that Jane Bennet was indifferent to him, "
            "convincing him to leave Netherfield for London. Darcy genuinely believed "
            "Jane did not love Bingley — her composure was too calm for a woman in love. "
            "He thought he was protecting his friend from an unsuitable attachment."
        ),
        "importance": 0.75,
        "zwaan_dims": {
            "time": "autumn",
            "space": "Netherfield",
            "protagonist": "Darcy",
            "causality": "friendship",
            "intent": "protect",
        },
    },
    {
        "id": "darcy_hunsford_proposal",
        "chapter": 5,
        "summary": (
            "Darcy proposed to Elizabeth at Hunsford. He told her of his love despite "
            "her inferior connections — expecting acceptance. She refused him furiously: "
            "accusing him of pride, of cruelty to Wickham, of destroying Jane's happiness. "
            "She said he was 'the last man in the world she could ever be prevailed upon to marry.' "
            "He left devastated — but her accusations forced him to see himself clearly for the first time."
        ),
        "importance": 0.95,
        "zwaan_dims": {
            "time": "morning",
            "space": "Hunsford Parsonage",
            "protagonist": "Darcy",
            "causality": "proposal",
            "intent": "confess",
        },
    },
    {
        "id": "darcy_writes_letter",
        "chapter": 5,
        "summary": (
            "After the rejection, Darcy wrote Elizabeth a long letter in answer to her accusations. "
            "He admitted separating Bingley from Jane, detailing his honest belief in Jane's indifference. "
            "He revealed Wickham's true character — the attempted elopement with Georgiana. "
            "Writing the letter forced him to articulate things to himself that he had never admitted."
        ),
        "importance": 0.85,
        "zwaan_dims": {
            "time": "morning",
            "space": "Hunsford",
            "protagonist": "Darcy",
            "causality": "rejection",
            "intent": "explain",
        },
    },
    {
        "id": "darcy_pemberley_meeting",
        "chapter": 6,
        "summary": (
            "Weeks after Hunsford, Darcy encountered Elizabeth unexpectedly at his own estate, Pemberley. "
            "He was mortified at his appearance — just returned from fishing — but found "
            "her manner towards him surprisingly softened. He invited her and her aunt and uncle to dine, "
            "determined to show her he had changed."
        ),
        "importance": 0.80,
        "zwaan_dims": {
            "time": "afternoon",
            "space": "Pemberley",
            "protagonist": "Darcy",
            "causality": "chance encounter",
            "intent": "reconnect",
        },
    },
]


def _make_event(char_name: str, data: dict) -> NarrativeEvent:
    """Build a NarrativeEvent from a dict for the given character."""
    return NarrativeEvent(
        id=data["id"],
        chapter=data["chapter"],
        position=f"{data['chapter']}.0",
        protagonist=char_name,
        summary=data["summary"],
        importance=data["importance"],
        related_entities=[zwaan.get("space", "")] if (zwaan := data.get("zwaan_dims", {})) else [],
        zwaan_dims=data.get("zwaan_dims", {}),
        embedding=None,
    )


def seed_demo_character() -> None:
    """Seed Elizabeth and Darcy (if not already in DB) + demo events."""
    episodic = EpisodicMemory()
    seeded_any = False

    for char in [ELIZABETH_BENNET, FITZWILLIAM_DARCY]:
        existing = get_character(char["name"])
        if existing is not None:
            print(f"  ✓ {char['name']} already exists, skipping")
        else:
            upsert_character(char)
            print(f"  ✓ Seeded {char['name']}")
            seeded_any = True

    # Seed demo events (idempotent — skips if already present)
    for char_name, event_list in [
        ("Elizabeth Bennet", _EVENTS_ELIZABETH),
        ("Fitzwilliam Darcy", _EVENTS_DARCY),
    ]:
        for data in event_list:
            existing = episodic.get_event(data["id"])
            if existing is not None:
                continue
            ev = _make_event(char_name, data)
            episodic.add_event(ev)
            print(f"  ✓ Seeded event '{data['id']}' (for {char_name})")

    if not seeded_any:
        print("  ✓ All demo data already present")
