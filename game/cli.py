# game/cli.py
from __future__ import annotations
from typing import Dict, Optional
import random
import string
import os

from .entities import Player
from .game_state import GameState
from .engine import GameEngine
from .scenario_modes import FindEachOtherScenario


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def run_cli_game() -> None:
    world_placeholder = None  # type: ignore

    players: Dict[str, Player] = {
        "P1": Player(id="P1", name="Player 1", location_id=""),
        "P2": Player(id="P2", name="Player 2", location_id=""),
    }

    state = GameState(
        world=world_placeholder,
        players=players,
        turn_order=["P1", "P2"],
    )

    scenario = FindEachOtherScenario()
    engine = GameEngine(state, scenario)

    print("=== Welcome to the Cult of Azathoth (Pass & Play) ===")
    print(f"Scenario: {scenario.name}")
    print()

    flush_messages(state, None)

    while state.active:
        current_player = state.current_player()

        print()
        print(f"--- Turn {state.turn_number} ---")
        print(f"It is {current_player.name}'s turn.")
        print("(Pass the keyboard to them.)")
        input("Press Enter when ready...")

        clear_screen()

        engine.describe_surroundings(current_player.id)
        flush_messages(state, current_player.id)

        # Inner loop: stay on this player until a real action consumes the turn
        while state.active:
            print()
            print(f"{current_player.name}, what do you do?")
            print("(Type 'help' for a list of commands.)")
            command = input("> ").strip()

            if command.lower() in ("end", "quit", "exit"):
                state.active = False
                state.add_message("You choose to abandon this place... for now.")
                flush_messages(state, current_player.id)
                break

            turn_consumed = engine.process_command(current_player.id, command)
            flush_messages(state, current_player.id)

            if not state.active:
                break

            if turn_consumed:
                # End-of-turn effects: sanity loss & ambient events
                engine.end_of_turn(current_player.id)
                flush_messages(state, current_player.id)

                if not state.active:
                    break

                break  # end this player's turn; outer loop will advance to next player

        if not state.active:
            break

        state.next_player()

    print()
    print("Game over.")


def flush_messages(state: GameState, player_id: Optional[str]) -> None:
    if not state.messages:
        return

    # Determine sanity for this player's perspective (None means no corruption)
    active_sanity: Optional[int] = None
    if player_id is not None and player_id in state.players:
        active_sanity = state.players[player_id].sanity

    print()
    for msg in state.messages:
        text = msg
        if active_sanity is not None:
            text = degrade_text(text, active_sanity)
        print(text)
        print()
    state.messages.clear()


def degrade_text(message: str, sanity: int) -> str:
    """
    Degrade text based on sanity.
    At full sanity, text is clear.
    As sanity drops toward 0, more letters glitch into random symbols.
    """
    max_sanity = 10
    sanity = max(0, min(sanity, max_sanity))

    # 0 severity at full sanity, 1 at 0 sanity
    severity = (max_sanity - sanity) / max_sanity
    if severity <= 0:
        return message

    # Base probability + extra based on severity
    base_prob = 0.03          # always a tiny bit of weirdness
    max_extra = 0.25          # up to +25% on top when sanity is 0
    p = base_prob + severity * max_extra

    glitch_charset = "░▒▓█▐"

    chars = []
    for ch in message:
        # Only degrade letters; keep spacing and punctuation mostly readable
        if ch.isalpha() and random.random() < p:
            chars.append(random.choice(glitch_charset))
        else:
            chars.append(ch)

    return "".join(chars)

