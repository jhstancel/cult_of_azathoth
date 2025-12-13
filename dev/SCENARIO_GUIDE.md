AFTER:

# Scenario Development Guide

All non-code design work for the game lives under `dev/`.

Each scenario gets its own folder:

- `dev/scenario_<name>/`
  - `rooms/rooms.yaml`   – Room definitions, connections, and basic text.
  - `items/items.yaml`   – Items available in this scenario.
  - `goals.md`           – Win/loss conditions, special rules.
  - `notes.md`           – Freeform design notes, ideas, dialogue, etc.

Example structure:

```text
dev/
  scenario_village/
    rooms/
      rooms.yaml
    items/
      items.yaml
    goals.md
    notes.md

Creating a New Scenario

From the project root, run:

make scenario village


This will create:

dev/scenario_village/
  rooms/rooms.yaml
  items/items.yaml
  goals.md
  notes.md


You can also specify a name explicitly:

make scenario name=castle

What Goes Where
rooms/rooms.yaml

Describe all rooms and how they connect. Example:

rooms:
  - id: gate
    name: Village Gate
    description: "A crooked wooden gate barely keeps the forest out."
    detail_description: "Lanterns sway on rusted hooks. Old wanted posters peel from the fence."
    neighbors: ["square"]

  - id: square
    name: Village Square
    description: "An empty square with a dry fountain."
    detail_description: "Stalls stand abandoned. A statue in the center has had its face chiselled away."
    neighbors: ["gate", "tavern"]

items/items.yaml

Define items available in this scenario:

items:
  - id: lantern
    name: Dented Lantern
    description: "A metal lantern that still holds a little oil."
    tags: ["light"]

  - id: village_potion
    name: Bitter Tonic
    description: "Brewed in someone’s cellar. Smells like herbs and smoke."
    tags: ["potion"]

goals.md

Explain the objective and special rules in plain language:

# Goals – Village Scenario

- Two players start at opposite edges of the village.
- The goal is to meet in the same room without either player reaching 0 health.
- Night advances every full round:
  - More ambient danger.
  - Certain rooms become unsafe.

Special rules:
- Lanterns lower sanity loss in outdoor rooms.
- The tavern is temporarily a safe zone (reduced ambient danger).

notes.md

Scratchpad for narrative beats, pacing ideas, NPCs, etc. This is for you, not the engine.

Hooking a Scenario into Code

Right now, scenarios are still hard-coded in game/scenario_modes.py. Over time:

You’ll parse rooms.yaml and items.yaml.

You’ll construct the World and items from data.

You’ll use goals.md as human-readable spec while implementing logic.

For now, treat these files as design docs that keep your scenarios consistent and modular.


