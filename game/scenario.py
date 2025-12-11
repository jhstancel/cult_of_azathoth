# game/scenario.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_state import GameState


class Scenario(ABC):
    name: str

    @abstractmethod
    def initial_setup(self, state: "GameState") -> None:
        ...

    @abstractmethod
    def check_win_condition(self, state: "GameState") -> Optional[str]:
        """
        Returns winner_id if someone has won, otherwise None.
        """
        ...

