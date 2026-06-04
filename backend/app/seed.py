"""Seed the database with a demo character — Caelan Ashmark from Caelvorn Series."""

from __future__ import annotations

from app.database import get_character, upsert_character


CAELAN = {
    "name": "Caelan Ashmark",
    "aliases": ["Caelan"],
    "traits": [
        {
            "name": "秩序驱动",
            "category": "core",
            "description": "他一直在现有框架内做到最好，从未质疑过框架本身。Pack秩序对他来说像空气一样自然。",
            "confidence": 0.95,
        },
        {
            "name": "极其聪明",
            "category": "core",
            "description": "谈判时从不先开价，能在30秒内判断出房间里的真正权力核心。但他的智识一直被用来在现有框架内做到最好，而不是质疑框架。",
            "confidence": 0.90,
        },
        {
            "name": "克制",
            "category": "core",
            "description": "情绪从来不在表面，藏在动作和沉默里。他的愤怒比平静更安静。从不解释自己的决定。",
            "confidence": 0.85,
        },
        {
            "name": "长期失眠",
            "category": "surface",
            "description": "长期的安静的失眠。他不觉得这是问题——Alpha不需要示弱。他在夜里保持清醒，处理文件，或者什么都不做地站在窗边。",
            "confidence": 0.80,
        },
        {
            "name": "不屑于压迫也不屑于看见",
            "category": "core",
            "description": "他不会主动压迫Omega，但他不会看见他们。不是恶意，是他的视野里从来没有被训练出那个焦距。",
            "confidence": 0.85,
        },
        {
            "name": "极少犯错",
            "category": "surface",
            "description": "他的决定通常是对的——一个经常犯错的人知道自己可能是错的；一个极少犯错的人，第一次错了会不知道该怎么办。",
            "confidence": 0.75,
        },
    ],
    "relations": {
        "Mira Goldthorn": "Luna（政治婚姻），相敬如宾，无感情也无恶意",
        "Edran Ashmark": "已故之父，前Alpha，用信息差控制了自己一辈子",
        "Lena": "Omega厨房帮工，Bond对象（尚未完全接受）",
        "Corvan Ashmark": "Beta顾问，自己的小叔，知道所有秘密",
    },
    "motivation": "维持Ashmark Pack的秩序和稳定。他接受的教育就是做一个好的Alpha——统治、决策、保护。他从未想过要别的。",
    "arc_stage": "initial — 刚在宴会上第一次感应到Bond，处于否认阶段",
    "backstory": (
        "Caelan Ashmark是Ashmark Pack的现任Alpha，32岁。"
        "父亲Edran Ashmark在他约22岁时急病去世，留下一个表面稳固但暗流涌动的Pack。"
        "他与Mira Goldthorn维持着一场体面的政治婚姻——相敬如宾，但没有感情。"
        "他统治Pack的方式是规则驱动的：极少动用强制力，因为极少有人敢试探他的边界。"
        "他长期失眠，但从不承认。他在三点钟的夜里独自清醒，处理文件，或者站在窗边。"
        "在最近一次高规格Pack宴会上，他的Bond突然感应到了一个人——"
        "一个他不应该感应到的、不在他视野里的人。他当晚没有睡着。"
    ),
    "embedding_centroid": None,
    "preferred_profile": None,
}


def seed_demo_character() -> None:
    """Seed Caelan if not already in the database."""
    existing = get_character("Caelan Ashmark")
    if existing is not None:
        return  # already seeded
    upsert_character(CAELAN)
    print("  ✓ Seeded Caelan Ashmark")
