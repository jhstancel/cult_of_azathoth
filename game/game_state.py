# game/game_state.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .world import World
from .entities import Player


@dataclass
class GameState:
    world: World
    players: Dict[str, Player]
    turn_order: List[str]
    current_turn_index: int = 0
    turn_number: int = 1
    active: bool = True
    winner_id: Optional[str] = None
    messages: List[str] = field(default_factory=list)

    def current_player(self) -> Player:
        return self.players[self.turn_order[self.current_turn_index]]

    def next_player(self) -> Player:
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
        if self.current_turn_index == 0:
            self.turn_number += 1
        return self.current_player()

    def add_message(self, message: str) -> None:
        self.messages.append(message)

