# game/yaml_scenario.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Set

from .scenario import Scenario
from .game_state import GameState
from .world import World, Location
from .entities import Item

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    yaml = None
    _yaml_import_error = e


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    mode: str
    starts: Dict[str, str]
    intro: str


class YamlScenario(Scenario):
    """
    Scenario driven entirely by files in a scenario directory:

      rooms.yaml  - scenario metadata + room graph
      items.yaml  - item definitions + placement

    goals.md / notes.md exist for humans; not loaded by runtime.
    """

    def __init__(self, scenario_dir: str) -> None:
        self.scenario_dir = Path(scenario_dir)
        self._config: Optional[ScenarioConfig] = None

    @property
    def name(self) -> str:
        # name must exist even before load; fall back to folder name
        if self._config is None:
            return self.scenario_dir.name
        return self._config.name

    def initial_setup(self, state: GameState) -> None:
        if yaml is None:  # pragma: no cover
            raise RuntimeError(
                "PyYAML is not installed. Install it with: pip install pyyaml"
            ) from _yaml_import_error

        rooms_path = self.scenario_dir / "rooms.yaml"
        items_path = self.scenario_dir / "items.yaml"

        if not rooms_path.exists():
            raise FileNotFoundError(f"Missing rooms.yaml: {rooms_path}")
        if not items_path.exists():
            raise FileNotFoundError(f"Missing items.yaml: {items_path}")

        rooms_doc = self._load_yaml(rooms_path)
        items_doc = self._load_yaml(items_path)

        config = self._parse_config(rooms_doc)
        world = self._build_world(rooms_doc)
        self._place_items(world, items_doc)

        state.world = world
        self._config = config

        # Start positions
        for pid, player in state.players.items():
            start_room = config.starts.get(pid)
            if start_room is None:
                # if unspecified, fall back to first room id
                first_room_id = next(iter(world.locations.keys()), "")
                start_room = first_room_id
            if start_room not in world.locations:
                raise ValueError(
                    f"Start room '{start_room}' for player '{pid}' does not exist in rooms.yaml"
                )
            player.location_id = start_room
        if config.intro:
            state.add_message(config.intro)

        if config.mode == "meet":
            state.add_message("Find each other before the darkness finds you.")
        else:
            state.add_message(f"Scenario mode: {config.mode}")

    def check_win_condition(self, state: GameState) -> Optional[str]:
        if self._config is None:
            return None

        mode = self._config.mode

        # Default / simplest win condition: both players meet
        if mode == "meet":
            players = list(state.players.values())
            if len(players) < 2:
                return None
            p1, p2 = players[0], players[1]
            if p1.location_id == p2.location_id:
                return "BOTH"
            return None

        # You can add more modes later without touching story files:
        # e.g. "reach:<room_id>", "survive:<turns>", etc.
        if mode.startswith("reach:"):
            target = mode.split(":", 1)[1].strip()
            for p in state.players.values():
                if p.location_id == target:
                    return p.id
            return None

        return None

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)  # type: ignore
        if data is None:
            return {}
        if not isinstance(data, dict):
            raise ValueError(f"YAML root must be a mapping in {path}")
        return data

    def _parse_config(self, rooms_doc: Dict[str, Any]) -> ScenarioConfig:
        scen = rooms_doc.get("scenario", {})
        if scen is None:
            scen = {}
        if not isinstance(scen, dict):
            raise ValueError("rooms.yaml: 'scenario' must be a mapping")

        name = str(scen.get("name", self.scenario_dir.name))
        mode = str(scen.get("mode", "meet"))

        starts_raw = scen.get("starts", {})
        if starts_raw is None:
            starts_raw = {}
        if not isinstance(starts_raw, dict):
            raise ValueError("rooms.yaml: 'scenario.starts' must be a mapping of player_id -> room_id")

        starts: Dict[str, str] = {str(k): str(v) for k, v in starts_raw.items()}

        intro = str(scen.get("intro", "")).rstrip()
        return ScenarioConfig(name=name, mode=mode, starts=starts, intro=intro)

    def _build_world(self, rooms_doc: Dict[str, Any]) -> World:
        rooms_raw = rooms_doc.get("rooms", [])
        if not isinstance(rooms_raw, list):
            raise ValueError("rooms.yaml: 'rooms' must be a list")

        world = World()

        # 1) create locations
        for r in rooms_raw:
            if not isinstance(r, dict):
                raise ValueError("rooms.yaml: each room must be a mapping")
            rid = str(r.get("id", "")).strip()
            if not rid:
                raise ValueError("rooms.yaml: room missing non-empty 'id'")
            loc = Location(
                id=rid.lower(),
                name=str(r.get("name", rid)),
                description=str(r.get("description", "")),
                detail_description=str(r.get("detail_description", "")),
            )
            world.add_location(loc)

        # 2) connect rooms via exits
        connected: Set[frozenset[str]] = set()
        for r in rooms_raw:
            rid = str(r.get("id", "")).strip().lower()
            exits = r.get("exits", {})
            if exits is None:
                exits = {}
            if not isinstance(exits, dict):
                raise ValueError(f"rooms.yaml: room '{rid}' exits must be a mapping")
            for _, dest in exits.items():
                dest_id = str(dest).strip().lower()
                if not dest_id:
                    continue
                if rid not in world.locations:
                    continue
                if dest_id not in world.locations:
                    raise ValueError(f"rooms.yaml: room '{rid}' exit points to missing room id '{dest_id}'")
                edge = frozenset([rid, dest_id])
                if edge in connected:
                    continue
                world.connect(rid, dest_id, bidirectional=True)
                connected.add(edge)

        return world

    def _place_items(self, world: World, items_doc: Dict[str, Any]) -> None:
        items_raw = items_doc.get("items", [])
        if not isinstance(items_raw, list):
            raise ValueError("items.yaml: 'items' must be a list")

        for it in items_raw:
            if not isinstance(it, dict):
                raise ValueError("items.yaml: each item must be a mapping")

            item_id = str(it.get("id", "")).strip().lower()
            if not item_id:
                raise ValueError("items.yaml: item missing non-empty 'id'")

            name = str(it.get("name", item_id))
            desc = str(it.get("description", ""))

            tags_raw = it.get("tags", [])
            if tags_raw is None:
                tags_raw = []
            if not isinstance(tags_raw, list):
                raise ValueError(f"items.yaml: item '{item_id}' tags must be a list")
            tags = [str(t) for t in tags_raw]

            loc_id = str(it.get("location", "")).strip().lower()
            if not loc_id:
                raise ValueError(f"items.yaml: item '{item_id}' missing 'location'")
            if loc_id not in world.locations:
                raise ValueError(f"items.yaml: item '{item_id}' location '{loc_id}' not found in rooms.yaml")

            item = Item(id=item_id, name=name, description=desc, tags=tags)
            world.locations[loc_id].place_item(item)

