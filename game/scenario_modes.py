# game/scenario_modes.py
from __future__ import annotations
from typing import Optional

from .scenario import Scenario
from .game_state import GameState
from .world import World, Location
from .entities import Player, Item


class FindEachOtherScenario(Scenario):
    name = "Find Each Other"

    def initial_setup(self, state: GameState) -> None:
        world = World()

        foyer = Location(
            id="foyer",
            name="Foyer",
            description="A cold, dim foyer with a single flickering candle.",
            detail_description="Peeling wallpaper curls from the walls and a large portrait with scratched-out faces hangs crooked above the door."
        )
        hall = Location(
            id="hall",
            name="Long Hallway",
            description="A narrow hallway. The walls seem closer than they should be.",
            detail_description="Uneven floorboards creak underfoot. Faded runner rugs lead past doorways, and the ceiling seems to sag in the middle."
        )
        library = Location(
            id="library",
            name="Library",
            description="Dusty shelves tower above. You hear faint whispering.",
            detail_description="Dozens of cracked leather spines stare down at you. A ladder leans uselessly against a shelf, and loose pages litter the floor like fallen leaves."
        )
        cellar = Location(
            id="cellar",
            name="Cellar",
            description="Damp stone underfoot. Something drips in the dark.",
            detail_description="Thick wooden beams hold up a low ceiling. Rusted hooks hang from chains, and old barrels sweat moisture in the chill."
        )

        world.add_location(foyer)
        world.add_location(hall)
        world.add_location(library)
        world.add_location(cellar)

        world.connect("foyer", "hall")
        world.connect("hall", "library")
        world.connect("hall", "cellar")

        # Items
        faint_lantern = Item(
            id="lantern",
            name="Faint Lantern",
            description="A small lantern that pushes the darkness back just a little.",
            tags=["light"]
        )
        strange_potion = Item(
            id="potion",
            name="Strange Potion",
            description="A cloudy liquid in a cracked vial. It smells metallic.",
            tags=["potion"]
        )
        clarity_potion = Item(
            id="clarity",
            name="Clarity Draught",
            description="A clear, bitter liquid that somehow smells like cold air.",
            tags=["potion", "clarity"]
        )

        foyer.place_item(faint_lantern)
        library.place_item(strange_potion)
        cellar.place_item(clarity_potion)

        state.world = world

        p1 = state.players["P1"]
        p2 = state.players["P2"]

        p1.location_id = "foyer"
        p2.location_id = "library"

        state.add_message("You awaken in different parts of a strange place.")
        state.add_message("Find each other before the darkness finds you.")

    def check_win_condition(self, state: GameState) -> Optional[str]:
        players = list(state.players.values())
        if len(players) < 2:
            return None

        p1, p2 = players[0], players[1]
        if p1.location_id == p2.location_id:
            return "BOTH"

        return None

