# game/cli.py
from __future__ import annotations

from typing import Dict, Optional
import argparse
import os
import random

from .entities import Player
from .game_state import GameState
from .engine import GameEngine
from .yaml_scenario import YamlScenario


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def run_cli_game() -> None:
    args = _parse_args()

    scenario_dir = args.scenario_dir
    if scenario_dir is None:
        scenario_dir = f"dev/scenario_{args.scenario}"

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

    scenario = YamlScenario(scenario_dir)
    engine = GameEngine(state, scenario)

    print("=== Welcome to the Cult of Azathoth (Pass & Play) ===")
    print(f"Scenario: {scenario.name}")
    print(f"Scenario dir: {scenario_dir}")
    print()
    print_controls()

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
                engine.end_of_turn(current_player.id)
                flush_messages(state, current_player.id)

                if not state.active:
                    break

                break

        if not state.active:
            break

        state.next_player()

    print()
    print("Game over.")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--scenario", default=os.environ.get("SCENARIO", "manor"))
    p.add_argument("--scenario-dir", default=os.environ.get("SCENARIO_DIR"))
    return p.parse_args()


def flush_messages(state: GameState, player_id: Optional[str]) -> None:
    if not state.messages:
        return

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
    max_sanity = 10
    sanity = max(0, min(sanity, max_sanity))

    severity = (max_sanity - sanity) / max_sanity
    if severity <= 0:
        return message

    base_prob = 0.03
    max_extra = 0.25
    p = base_prob + severity * max_extra

    glitch_charset = "░▒▓█▐"

    chars = []
    for ch in message:
        if ch.isalpha() and random.random() < p:
            chars.append(random.choice(glitch_charset))
        else:
            chars.append(ch)

    return "".join(chars)
def print_controls() -> None:
    print("Controls:")
    print("  look / l                     - Look around")
    print("  move <room name or id>       - Move to an adjacent location")
    print("  search / s                   - Search the area for items")
    print("  use <item>                   - Use an item in your inventory")
    print("  status                       - View your status")
    print("  help                         - Show this help")
    print("  end / quit                   - End the game")
    print()

