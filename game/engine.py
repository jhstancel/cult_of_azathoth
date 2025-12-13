# game/engine.py
from __future__ import annotations
from typing import Optional, Tuple
import random

from .game_state import GameState
from .scenario import Scenario
from .entities import Player, Item
from .world import Location


class GameEngine:
    def __init__(self, state: GameState, scenario: Scenario) -> None:
        self.state = state
        self.scenario = scenario

        self.scenario.initial_setup(self.state)

    def process_command(self, player_id: str, command_str: str) -> bool:
        """
        Returns True if the command consumes the player's turn,
        False if the turn should stay with the same player
        (e.g. help or invalid commands).
        """
        if not self.state.active:
            return False

        command_str = command_str.strip()
        if not command_str:
            self.state.add_message("You hesitate, doing nothing.")
            return False

        verb, arg = self._split_command(command_str)

        consumes_turn = True

        if verb in ("look", "l"):
            self._handle_look(player_id)
        elif verb in ("move", "go", "m"):
            self._handle_move(player_id, arg)
        elif verb in ("search", "s"):
            self._handle_search(player_id)
        elif verb in ("use", "u"):
            self._handle_use(player_id, arg)
        elif verb in ("status", "stats"):
            self._handle_status(player_id)
        elif verb in ("help", "?"):
            self._handle_help(player_id)
            consumes_turn = False
        else:
            self.state.add_message(
                "You mutter something unintelligible. Nothing happens. (Type 'help' for commands.)"
            )
            consumes_turn = False

        return consumes_turn

    def _split_command(self, command_str: str) -> Tuple[str, str]:
        parts = command_str.split(maxsplit=1)
        if len(parts) == 1:
            return parts[0].lower(), ""
        return parts[0].lower(), parts[1].strip()

    def _get_player_and_location(self, player_id: str) -> Tuple[Player, Optional[Location]]:
        player = self.state.players[player_id]
        loc = self.state.world.get_location(player.location_id)
        return player, loc

    def describe_surroundings(self, player_id: str) -> None:
        """
        Basic glance at the current room shown at the start of a turn.
        If the player has inspected (searched) this room before, show detail.
        """
        player, loc = self._get_player_and_location(player_id)
        if loc is None:
            self.state.add_message("You are nowhere. That seems… bad.")
            return

        inspected = loc.id in self.state.inspected_rooms.get(player_id, set())

        if inspected:
            text = (loc.detail_description or "").strip()
            if not text:
                text = (loc.description or "").strip()
        else:
            text = (loc.description or "").strip()

        desc_lines = [f"{player.name}, you are in {loc.name}."]
        if text:
            desc_lines.append(text)

        self.state.add_message("\n".join(desc_lines))

    def _handle_look(self, player_id: str) -> None:
        """
        Detailed inspection of the room. Reveals exits, items, and extra detail.
        """
        player, loc = self._get_player_and_location(player_id)
        if loc is None:
            self.state.add_message("You are nowhere. That seems… bad.")
            return

        detail = (loc.detail_description or "").strip()
        if not detail:
            detail = "You don't notice anything new."

        desc_lines = [
            f"You take a careful look around {loc.name}.",
            detail,
        ]

        if loc.neighbors:
            neighbor_names = []
            for nid in loc.neighbors:
                nloc = self.state.world.get_location(nid)
                if nloc:
                    neighbor_names.append(f"{nloc.name} ({nid})")
                else:
                    neighbor_names.append(nid)
            neighbors_str = ", ".join(neighbor_names)
            desc_lines.append(f"Exits lead to: {neighbors_str}.")

        if loc.items:
            item_list = ", ".join(item.name for item in loc.items)
            desc_lines.append(f"On closer inspection, you notice: {item_list} on the ground.")
        else:
            desc_lines.append("You don't see anything obviously useful, just the unsettling details of the room.")

        player_items = player.inventory
        if player_items:
            inv_list = ", ".join(item.name for item in player_items)
            desc_lines.append(f"Carrying: {inv_list}.")

        self.state.add_message("\n".join(desc_lines))
 def _handle_move(self, player_id: str, target: str) -> None:
        player, loc = self._get_player_and_location(player_id)
        if loc is None:
            self.state.add_message("You cannot move from here.")
            return

        if not target:
            self.state.add_message("Move where?")
            return

        target_lower = target.lower()

        # Try by id
        destination_id: Optional[str] = None
        if target_lower in loc.neighbors:
            destination_id = target_lower
        else:
            # Try by location name
            for nid in loc.neighbors:
                nloc = self.state.world.get_location(nid)
                if nloc and nloc.name.lower() == target_lower:
                    destination_id = nloc.id
                    break

        if not destination_id:
            self.state.add_message("You fumble in the dark, but there is no clear path that way.")
            return

        player.location_id = destination_id
        new_loc = self.state.world.get_location(destination_id)
        if new_loc:
            self.state.add_message(f"You move into {new_loc.name}.")
            self.describe_surroundings(player_id)
        else:
            self.state.add_message("You step into an undefined void. Odd.")
    def _handle_search(self, player_id: str) -> None:
        player, loc = self._get_player_and_location(player_id)
        if loc is None:
            self.state.add_message("There is nothing here to search.")
            return

        if player_id not in self.state.inspected_rooms:
            self.state.inspected_rooms[player_id] = set()
        self.state.inspected_rooms[player_id].add(loc.id)

        if not loc.items:
            self.state.add_message("You search the area but find nothing useful.")
            return

        found_names = ", ".join(item.name for item in loc.items)
        self.state.add_message(f"You search carefully and find: {found_names}.")
        self.state.add_message("You pick them up.")

        player.inventory.extend(loc.items)
        loc.items.clear()

    def _handle_use(self, player_id: str, target: str) -> None:
        player = self.state.players[player_id]

        if not player.inventory:
            self.state.add_message("You have nothing to use.")
            return

        if not target:
            self.state.add_message("Use what? (Hint: use <item id or name>)")
            return

        target_lower = target.lower()
        item: Optional[Item] = None

        # Try by id, then by name substring
        for it in player.inventory:
            if it.id.lower() == target_lower or target_lower in it.name.lower():
                item = it
                break

        if not item:
            self.state.add_message("You fumble through your things but can't find that.")
            return

        max_sanity = 10

        # Very simple item effects for now
        if "clarity" in item.tags:
            player.sanity = max_sanity
            self.state.add_message("You drink the clear draught. The whispers fall silent.")
            self.state.add_message("Your mind snaps back into focus. (Sanity fully restored)")
            player.inventory.remove(item)
        elif "potion" in item.tags:
            player.health += 3
            player.sanity = min(max_sanity, player.sanity + 2)
            self.state.add_message("You drink the strange potion. Warmth spreads through your body.")
            self.state.add_message("You feel a little safer. (+3 health, +2 sanity)")
            player.inventory.remove(item)
        elif "light" in item.tags:
            player.sanity = min(max_sanity, player.sanity + 1)
            self.state.add_message("You raise the lantern. The darkness shrinks back a little.")
            self.state.add_message("Your mind steadies. (+1 sanity)")
        else:
            self.state.add_message("You fiddle with it, but nothing obvious happens.")

    def _handle_status(self, player_id: str) -> None:
        player = self.state.players[player_id]
        msg = (
            f"{player.name}'s status:\n"
            f"  Health: {player.health}\n"
            f"  Sanity: {player.sanity}\n"
            f"  Location: {player.location_id}\n"
        )
        self.state.add_message(msg)

    def _handle_help(self, player_id: str) -> None:
        msg = (
            "Commands:\n"
            "  look / l                     - Look around\n"
            "  move <room name or id>       - Move to an adjacent location\n"
            "  search / s                   - Search the area for items\n"
            "  use <item>                   - Use an item in your inventory\n"
            "  status                       - View your status\n"
            "  help                         - Show this help\n"
            "  end / quit                   - End the game\n"
        )
        self.state.add_message(msg)

    def _resolve_ambient_danger(self, player_id: str) -> None:
        """
        Simple horror pressure:
        - 20%: creepy noise (flavor).
        - 15%: sanity chip.
        - 10%: health chip.
        """
        player = self.state.players[player_id]
        roll = random.random()

        if roll < 0.2:
            self.state.add_message("Something moves just out of sight. The air feels heavier.")
        elif roll < 0.35:
            player.sanity -= 1
            self.state.add_message("A whisper curls into your ear in a voice you almost recognize. (-1 sanity)")
        elif roll < 0.45:
            player.health -= 1
            self.state.add_message("A sudden, invisible weight presses on your chest. It hurts to breathe. (-1 health)")

    def end_of_turn(self, player_id: str) -> None:
        """
        Apply end-of-turn effects: ambient danger, then death/win checks.
        Called only when a turn-consuming action has happened.
        """
        if not self.state.active:
            return

        self._resolve_ambient_danger(player_id)

        # Check for death
        for p in self.state.players.values():
            if p.health <= 0:
                self.state.active = False
                self.state.winner_id = None
                self.state.add_message("The darkness closes in. No one escapes.")
                return

        # Check win condition after ambient effects
        if self.state.active:
            winner_id = self.scenario.check_win_condition(self.state)
            if winner_id is not None:
                self._handle_win(winner_id)

    def _handle_win(self, winner_id: str) -> None:
        self.state.active = False
        self.state.winner_id = winner_id

        if winner_id == "BOTH":
            self.state.add_message("You find each other in the darkness. For now, you are safe.")
        else:
            self.state.add_message(f"Player {winner_id} has won.")

