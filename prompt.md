# Pygame Pokémon-Style Movement Game Prompt

Create a Python game using **Pygame** that behaves like a simple Pokémon-style top-down movement system.

I already have these assets:
- Player spritesheet (3x3 grid, total 9 frames)
- Grass tile (used as floor)
- Bush tile (walkable decoration)
- Tree tile (solid obstacle)

---

## Requirements

### 1. Game Setup
- Create a Pygame window and game loop.
- Use a tile-based map (32x32 or 48x48 tiles).
- Fill the entire map with grass tiles as the base ground.
- Place bushes and trees on top of the grass using a map layout.

---

### 2. Player Movement
- Player moves using WASD or arrow keys.
- Movement should be smooth (not turn-based unless easier to implement).
- Player starts in the center of the map.
- Use the 3x3 sprite sheet for directional walking animations.
- Animate based on movement direction.

---

### 3. Collision Rules
- Grass: walkable
- Bush: walkable (no collision)
- Tree: NOT walkable (solid collision using rectangles or tile-based collision)

---

### 4. Rendering Order (IMPORTANT)
Render in this exact order:
1. Grass (background layer)
2. Player
3. Bush (must render ON TOP of player even though it is walkable)
4. Tree (blocks movement, can render above grass)

---

### 5. Code Structure
Organize code cleanly using classes:
- `Player` class → movement, animation, collision
- `Map` or `TileMap` class → world data and rendering
- Main game loop → update + render

---

### 6. Extra Requirements
- Optional camera that follows the player
- Keep code simple, readable, and modular
- Ensure collision detection is stable and bug-free