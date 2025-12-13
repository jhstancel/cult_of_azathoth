scenario:
  name: "Manor"
  mode: "meet"   # meet | reach:<room_id>
  intro: |
    You wake up on a cold stone floor. The air stinks of mildew.
    Something is watching from the dark corner you can't quite see.
  starts:
    P1: "foyer"
    P2: "library"

# rooms.yaml is the ONLY runtime story file for rooms + topology.
# goals.md / notes.md are for humans, not parsed by the engine.

rooms:
  - id: "foyer"
    name: "Foyer"
    description: |
      A cold, dim foyer with a single flickering candle.
    detail_description: |
      Peeling wallpaper curls from the walls. The air tastes old.
    exits:
      north: "hall"

  - id: "hall"
    name: "Long Hallway"
    description: |
      A narrow hallway. The walls seem closer than they should be.
    detail_description: |
      Uneven floorboards creak underfoot. Shadows stretch when you blink.
    exits:
      south: "foyer"
      east: "library"
      down: "cellar"

  - id: "library"
    name: "Library"
    description: |
      Dusty shelves tower above. You hear faint whispering.
    detail_description: |
      Dozens of cracked leather spines stare down at you like unblinking eyes.
    exits:
      west: "hall"

  - id: "cellar"
    name: "Cellar"
    description: |
      Damp stone underfoot. Something drips in the dark.
    detail_description: |
      Thick wooden beams hold up a low ceiling. The corners feel occupied.
    exits:
      up: "hall"

