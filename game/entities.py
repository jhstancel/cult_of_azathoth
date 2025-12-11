# game/entities.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Item:
    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)


@dataclass
class Player:
    id: str
    name: str
    location_id: str
    health: int = 10
    sanity: int = 10
    inventory: List[Item] = field(default_factory=list)

