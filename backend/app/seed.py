"""Seed the database with demo characters — Elizabeth Bennet & Fitzwilliam Darcy.

Pride and Prejudice (Jane Austen, 1813) for the Qwen Cloud Global AI Hackathon.
Familiar to a global audience; rich character arcs ideal for OOC detection
and narrative memory demos.
"""

from __future__ import annotations

from app.database import get_character, upsert_character


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


def seed_demo_character() -> None:
    """Seed Elizabeth and Darcy if not already in the database."""
    for char in [ELIZABETH_BENNET, FITZWILLIAM_DARCY]:
        existing = get_character(char["name"])
        if existing is not None:
            print(f"  ✓ {char['name']} already exists, skipping")
            continue
        upsert_character(char)
        print(f"  ✓ Seeded {char['name']}")
