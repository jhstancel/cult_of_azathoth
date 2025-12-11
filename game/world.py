# game/world.py
from dataclasses import dataclass, field
from typing import Dict, Set, Optional, List

from .entities import Item


@dataclass
class Location:
    id: str
    name: str
    description: str
    detail_description: str = ""
    neighbors: Set[str] = field(default_factory=set)
    items: List[Item] = field(default_factory=list)

    def add_neighbor(self, neighbor_id: str) -> None:
        self.neighbors.add(neighbor_id)

    def place_item(self, item: Item) -> None:
        self.items.append(item)


class World:
    def __init__(self) -> None:
        self.locations: Dict[str, Location] = {}

    def add_location(self, location: Location) -> None:
        self.locations[location.id] = location

    def connect(self, id_a: str, id_b: str, bidirectional: bool = True) -> None:
        a = self.locations[id_a]
        b = self.locations[id_b]
        a.add_neighbor(b.id)
        if bidirectional:
            b.add_neighbor(a.id)

    def get_location(self, location_id: str) -> Optional[Location]:
        return self.locations.get(location_id)

