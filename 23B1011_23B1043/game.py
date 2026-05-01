# # """
# # game.py — Turntile CGT Game Logic (pure, no rendering)
# # =======================================================
# # Rulesets:
# #   A: Impartial — either player places a domino in any orientation
# #   B: Partizan — place in your orientation, then optionally rotate
# #      the opponent's most recently placed tile (any tile on board)
# #   C: Partizan — place in your orientation, then optionally rotate
# #      any tile already on the board except the one just placed

# # Rotation rule (all rulesets that have rotation):
# #   Pick one end-cell of a domino as the pivot.
# #   The other cell moves to any of the 3 neighbours of the pivot
# #   that isn't the current position of that other cell.
# #   This gives up to 6 candidate positions per domino.
# #   A candidate is valid if both cells are active board cells
# #   and neither cell is occupied by a DIFFERENT domino.
# # """

# # from dataclasses import dataclass, field
# # from typing import Optional
# # import copy


# # # ─────────────────────────────────────────────────────────
# # # Data types
# # # ─────────────────────────────────────────────────────────

# # Cell = tuple[int, int]   # (row, col)

# # @dataclass
# # class Domino:
# #     id: int
# #     player: str          # 'H' or 'V'
# #     cells: tuple[Cell, Cell]   # always sorted: top-left first

# #     def orientation(self) -> str:
# #         r0, c0 = self.cells[0]
# #         r1, c1 = self.cells[1]
# #         return 'V' if r1 > r0 else 'H'


# # @dataclass
# # class GameState:
# #     ruleset: str                    # 'A', 'B', 'C'
# #     board_cells: frozenset[Cell]    # all active cells
# #     rows: int
# #     cols: int
# #     name_h: str
# #     name_v: str

# #     dominoes: list[Domino] = field(default_factory=list)
# #     occupied: dict[Cell, int] = field(default_factory=dict)  # cell -> domino.id
# #     current_player: str = 'H'
# #     phase: str = 'place'            # 'place' or 'rotate'
# #     last_placed_id: Optional[int] = None
# #     move_count: int = 0
# #     log: list[str] = field(default_factory=list)
# #     over: bool = False
# #     winner: Optional[str] = None
# #     _next_id: int = 0

# #     def domino_by_id(self, did: int) -> Optional[Domino]:
# #         for d in self.dominoes:
# #             if d.id == did:
# #                 return d
# #         return None

# #     def is_active(self, r: int, c: int) -> bool:
# #         return (r, c) in self.board_cells

# #     def is_free(self, r: int, c: int) -> bool:
# #         return (r, c) in self.board_cells and (r, c) not in self.occupied


# # # ─────────────────────────────────────────────────────────
# # # Board construction helpers
# # # ─────────────────────────────────────────────────────────

# # def make_grid_board(rows: int, cols: int) -> frozenset[Cell]:
# #     return frozenset((r, c) for r in range(rows) for c in range(cols))


# # def make_custom_board(cells: set[Cell]) -> frozenset[Cell]:
# #     return frozenset(cells)


# # # ─────────────────────────────────────────────────────────
# # # Move generation
# # # ─────────────────────────────────────────────────────────

# # def _sorted_pair(a: Cell, b: Cell) -> tuple[Cell, Cell]:
# #     return (a, b) if (a[0], a[1]) <= (b[0], b[1]) else (b, a)


# # def h_placements(G: GameState) -> list[tuple[Cell, Cell]]:
# #     """All valid horizontal domino placements (left-cell, right-cell)."""
# #     result = []
# #     for r, c in G.board_cells:
# #         if G.is_free(r, c) and G.is_free(r, c + 1):
# #             result.append(_sorted_pair((r, c), (r, c + 1)))
# #     return result


# # def v_placements(G: GameState) -> list[tuple[Cell, Cell]]:
# #     """All valid vertical domino placements (top-cell, bottom-cell)."""
# #     result = []
# #     for r, c in G.board_cells:
# #         if G.is_free(r, c) and G.is_free(r + 1, c):
# #             result.append(_sorted_pair((r, c), (r + 1, c)))
# #     return result


# # def valid_placements(G: GameState, player: Optional[str] = None) -> list[tuple[Cell, Cell]]:
# #     """
# #     Returns all valid placement moves for the given player.
# #     Ruleset A: both orientations.
# #     Rulesets B/C: H → horizontal only, V → vertical only.
# #     """
# #     p = player or G.current_player
# #     if G.ruleset == 'A':
# #         return h_placements(G) + v_placements(G)
# #     elif p == 'H':
# #         return h_placements(G)
# #     else:
# #         return v_placements(G)


# # def _neighbours(r: int, c: int) -> list[Cell]:
# #     return [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]


# # def rotation_candidates(G: GameState, domino: Domino) -> list[dict]:
# #     """
# #     Returns all valid rotation outcomes for a domino.

# #     For each of the 2 end-cells as pivot, the other cell can move to
# #     any of 3 neighbours of the pivot (excluding its current position).
# #     = up to 6 candidates total.

# #     Each result: {
# #         'pivot': Cell,
# #         'new_other': Cell,
# #         'cells': tuple[Cell,Cell]  — sorted pair the domino would occupy
# #     }

# #     A candidate is valid if:
# #       - both cells are active board cells
# #       - any cell not currently part of THIS domino is unoccupied
# #     """
# #     own = set(domino.cells)
# #     cell_a, cell_b = domino.cells[0], domino.cells[1]
# #     results = []
# #     seen = set()

# #     for pivot, other in [(cell_a, cell_b), (cell_b, cell_a)]:
# #         for n in _neighbours(*pivot):
# #             if n == other:
# #                 continue                      # already there
# #             pr, pc = pivot
# #             nr, nc = n

# #             # Both cells must be active
# #             if (pr, pc) not in G.board_cells:
# #                 continue
# #             if (nr, nc) not in G.board_cells:
# #                 continue

# #             # The new cell must be free OR already part of this domino
# #             if (nr, nc) in G.occupied and (nr, nc) not in own:
# #                 continue

# #             pair = _sorted_pair(pivot, n)
# #             if pair in seen:
# #                 continue
# #             seen.add(pair)

# #             results.append({
# #                 'pivot': pivot,
# #                 'new_other': n,
# #                 'cells': pair,
# #             })

# #     return results


# # def rotatable_domino_ids(G: GameState) -> list[int]:
# #     """
# #     Returns IDs of dominoes eligible for rotation this phase.

# #     Ruleset B: any domino placed so far (either player).
# #     Ruleset C: every domino EXCEPT the one just placed this turn.
# #     """
# #     if G.phase != 'rotate':
# #         return []

# #     opp = 'V' if G.current_player == 'H' else 'H'

# #     if G.ruleset == 'B':
# #         # Any domino placed so far (either player)
# #         return [
# #             d.id for d in G.dominoes
# #             if rotation_candidates(G, d)
# #         ]

# #     if G.ruleset == 'C':
# #         # Any domino except the just-placed one
# #         return [
# #             d.id for d in G.dominoes
# #             if d.id != G.last_placed_id and rotation_candidates(G, d)
# #         ]

# #     return []


# # # ─────────────────────────────────────────────────────────
# # # Mutation
# # # ─────────────────────────────────────────────────────────

# # def place_domino(G: GameState, cell_a: Cell, cell_b: Cell) -> dict:
# #     """
# #     Place a domino occupying cell_a and cell_b for the current player.
# #     Returns {'ok': True} or {'ok': False, 'error': str}.
# #     """
# #     if G.over:
# #         return {'ok': False, 'error': 'Game is over.'}
# #     if G.phase != 'place':
# #         return {'ok': False, 'error': 'Not in place phase.'}

# #     pair = _sorted_pair(cell_a, cell_b)

# #     # Validate: pair must be in valid_placements
# #     if pair not in valid_placements(G):
# #         return {'ok': False, 'error': f'Invalid placement: {pair}'}

# #     # Create domino
# #     did = G._next_id
# #     G._next_id += 1
# #     d = Domino(id=did, player=G.current_player, cells=pair)
# #     G.dominoes.append(d)
# #     G.last_placed_id = did
# #     for cell in pair:
# #         G.occupied[cell] = did

# #     name = G.name_h if G.current_player == 'H' else G.name_v
# #     orient = 'H' if pair[0][0] == pair[1][0] else 'V'
# #     G.log.append(f"{name} placed {orient} domino at {pair[0]}+{pair[1]}")

# #     # Advance phase
# #     if G.ruleset == 'A':
# #         _end_turn(G)
# #     else:
# #         G.phase = 'rotate'
# #         # If no rotatable pieces exist, skip rotation automatically
# #         if not rotatable_domino_ids(G):
# #             G.log.append("(no rotation possible — skipped)")
# #             _end_turn(G)

# #     return {'ok': True}


# # def rotate_domino(G: GameState, domino_id: int, new_cells: tuple[Cell, Cell]) -> dict:
# #     """
# #     Rotate the domino with given id to occupy new_cells.
# #     new_cells must be one of the results from rotation_candidates().
# #     Returns {'ok': True} or {'ok': False, 'error': str}.
# #     """
# #     if G.phase != 'rotate':
# #         return {'ok': False, 'error': 'Not in rotate phase.'}

# #     if domino_id not in rotatable_domino_ids(G):
# #         return {'ok': False, 'error': 'Domino not eligible for rotation.'}

# #     domino = G.domino_by_id(domino_id)
# #     if domino is None:
# #         return {'ok': False, 'error': 'Domino not found.'}

# #     candidates = rotation_candidates(G, domino)
# #     target = _sorted_pair(*new_cells)
# #     valid_targets = [c['cells'] for c in candidates]

# #     if target not in valid_targets:
# #         return {'ok': False, 'error': f'Invalid rotation target {target}. Valid: {valid_targets}'}

# #     # Remove old occupancy
# #     for cell in domino.cells:
# #         del G.occupied[cell]

# #     # Apply new position
# #     domino.cells = target
# #     for cell in target:
# #         G.occupied[cell] = domino_id

# #     name = G.name_h if G.current_player == 'H' else G.name_v
# #     orient = 'H' if target[0][0] == target[1][0] else 'V'
# #     G.log.append(f"{name} rotated domino #{domino_id} → {orient} at {target[0]}+{target[1]}")

# #     _end_turn(G)
# #     return {'ok': True}


# # def skip_rotation(G: GameState) -> dict:
# #     """Skip the rotation phase."""
# #     if G.phase != 'rotate':
# #         return {'ok': False, 'error': 'Not in rotate phase.'}
# #     name = G.name_h if G.current_player == 'H' else G.name_v
# #     G.log.append(f"{name} skipped rotation.")
# #     _end_turn(G)
# #     return {'ok': True}


# # def _end_turn(G: GameState):
# #     G.move_count += 1
# #     G.current_player = 'V' if G.current_player == 'H' else 'H'
# #     G.phase = 'place'
# #     G.last_placed_id = None

# #     # Check if next player has any moves
# #     if not valid_placements(G):
# #         loser = G.current_player
# #         G.winner = 'V' if loser == 'H' else 'H'
# #         G.over = True
# #         winner_name = G.name_h if G.winner == 'H' else G.name_v
# #         loser_name = G.name_h if loser == 'H' else G.name_v
# #         G.log.append(f"🏆 {winner_name} wins! ({loser_name} has no moves.)")


# # # ─────────────────────────────────────────────────────────
# # # Factory
# # # ─────────────────────────────────────────────────────────

# # def new_game(ruleset: str, board_cells: frozenset[Cell],
# #              rows: int, cols: int,
# #              name_h: str = 'Player H', name_v: str = 'Player V') -> GameState:
# #     return GameState(
# #         ruleset=ruleset,
# #         board_cells=board_cells,
# #         rows=rows,
# #         cols=cols,
# #         name_h=name_h,
# #         name_v=name_v,
# #     )

# """
# game.py — Turntile CGT Game Logic (pure, no rendering)
# =======================================================
# Rulesets:
#   A: Impartial — either player places a domino in any orientation
#   B: Partizan — place in your orientation, then optionally rotate
#      the opponent's most recently placed tile (any tile on board)
#   C: Partizan — place in your orientation, then optionally rotate
#      any tile already on the board except the one just placed
#   D: Partizan — place in your orientation, then optionally rotate
#      only the tile you just placed

# Rotation rule (all rulesets that have rotation):
#   Pick one end-cell of a domino as the pivot.
#   The other cell moves to any of the 3 neighbours of the pivot
#   that isn't the current position of that other cell.
#   This gives up to 6 candidate positions per domino.
#   A candidate is valid if both cells are active board cells
#   and neither cell is occupied by a DIFFERENT domino.
# """

# from dataclasses import dataclass, field
# from typing import Optional
# import copy


# # ─────────────────────────────────────────────────────────
# # Data types
# # ─────────────────────────────────────────────────────────

# Cell = tuple[int, int]   # (row, col)

# @dataclass
# class Domino:
#     id: int
#     player: str          # 'H' or 'V'
#     cells: tuple[Cell, Cell]   # always sorted: top-left first

#     def orientation(self) -> str:
#         r0, c0 = self.cells[0]
#         r1, c1 = self.cells[1]
#         return 'V' if r1 > r0 else 'H'


# @dataclass
# class GameState:
#     ruleset: str                    # 'A', 'B', 'C', 'D'
#     board_cells: frozenset[Cell]    # all active cells
#     rows: int
#     cols: int
#     name_h: str
#     name_v: str

#     dominoes: list[Domino] = field(default_factory=list)
#     occupied: dict[Cell, int] = field(default_factory=dict)  # cell -> domino.id
#     current_player: str = 'H'
#     phase: str = 'place'            # 'place' or 'rotate'
#     last_placed_id: Optional[int] = None
#     move_count: int = 0
#     log: list[str] = field(default_factory=list)
#     over: bool = False
#     winner: Optional[str] = None
#     _next_id: int = 0

#     def domino_by_id(self, did: int) -> Optional[Domino]:
#         for d in self.dominoes:
#             if d.id == did:
#                 return d
#         return None

#     def is_active(self, r: int, c: int) -> bool:
#         return (r, c) in self.board_cells

#     def is_free(self, r: int, c: int) -> bool:
#         return (r, c) in self.board_cells and (r, c) not in self.occupied


# # ─────────────────────────────────────────────────────────
# # Board construction helpers
# # ─────────────────────────────────────────────────────────

# def make_grid_board(rows: int, cols: int) -> frozenset[Cell]:
#     return frozenset((r, c) for r in range(rows) for c in range(cols))


# def make_custom_board(cells: set[Cell]) -> frozenset[Cell]:
#     return frozenset(cells)


# # ─────────────────────────────────────────────────────────
# # Move generation
# # ─────────────────────────────────────────────────────────

# def _sorted_pair(a: Cell, b: Cell) -> tuple[Cell, Cell]:
#     return (a, b) if (a[0], a[1]) <= (b[0], b[1]) else (b, a)


# def h_placements(G: GameState) -> list[tuple[Cell, Cell]]:
#     """All valid horizontal domino placements (left-cell, right-cell)."""
#     result = []
#     for r, c in G.board_cells:
#         if G.is_free(r, c) and G.is_free(r, c + 1):
#             result.append(_sorted_pair((r, c), (r, c + 1)))
#     return result


# def v_placements(G: GameState) -> list[tuple[Cell, Cell]]:
#     """All valid vertical domino placements (top-cell, bottom-cell)."""
#     result = []
#     for r, c in G.board_cells:
#         if G.is_free(r, c) and G.is_free(r + 1, c):
#             result.append(_sorted_pair((r, c), (r + 1, c)))
#     return result


# def valid_placements(G: GameState, player: Optional[str] = None) -> list[tuple[Cell, Cell]]:
#     """
#     Returns all valid placement moves for the given player.
#     Ruleset A: both orientations.
#     Rulesets B/C/D: H → horizontal only, V → vertical only.
#     """
#     p = player or G.current_player
#     if G.ruleset == 'A':
#         return h_placements(G) + v_placements(G)
#     elif p == 'H':
#         return h_placements(G)
#     else:
#         return v_placements(G)


# def _neighbours(r: int, c: int) -> list[Cell]:
#     return [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]


# def rotation_candidates(G: GameState, domino: Domino) -> list[dict]:
#     """
#     Returns all valid rotation outcomes for a domino.

#     For each of the 2 end-cells as pivot, the other cell can move to
#     any of 3 neighbours of the pivot (excluding its current position).
#     = up to 6 candidates total.

#     Each result: {
#         'pivot': Cell,
#         'new_other': Cell,
#         'cells': tuple[Cell,Cell]  — sorted pair the domino would occupy
#     }

#     A candidate is valid if:
#       - both cells are active board cells
#       - any cell not currently part of THIS domino is unoccupied
#     """
#     own = set(domino.cells)
#     cell_a, cell_b = domino.cells[0], domino.cells[1]
#     results = []
#     seen = set()

#     for pivot, other in [(cell_a, cell_b), (cell_b, cell_a)]:
#         for n in _neighbours(*pivot):
#             if n == other:
#                 continue                      # already there
#             pr, pc = pivot
#             nr, nc = n

#             # Both cells must be active
#             if (pr, pc) not in G.board_cells:
#                 continue
#             if (nr, nc) not in G.board_cells:
#                 continue

#             # The new cell must be free OR already part of this domino
#             if (nr, nc) in G.occupied and (nr, nc) not in own:
#                 continue

#             pair = _sorted_pair(pivot, n)
#             if pair in seen:
#                 continue
#             seen.add(pair)

#             results.append({
#                 'pivot': pivot,
#                 'new_other': n,
#                 'cells': pair,
#             })

#     return results


# def rotatable_domino_ids(G: GameState) -> list[int]:
#     """
#     Returns IDs of dominoes eligible for rotation this phase.

#     Ruleset B: any domino placed so far (either player).
#     Ruleset C: every domino EXCEPT the one just placed this turn.
#     Ruleset D: only the domino just placed this turn.
#     """
#     if G.phase != 'rotate':
#         return []

#     if G.ruleset == 'B':
#         # Any domino placed so far (either player)
#         return [
#             d.id for d in G.dominoes
#             if rotation_candidates(G, d)
#         ]

#     if G.ruleset == 'C':
#         # Any domino except the just-placed one
#         return [
#             d.id for d in G.dominoes
#             if d.id != G.last_placed_id and rotation_candidates(G, d)
#         ]

#     if G.ruleset == 'D':
#         # Only the domino just placed this turn
#         if G.last_placed_id is None:
#             return []
#         d = G.domino_by_id(G.last_placed_id)
#         if d and rotation_candidates(G, d):
#             return [G.last_placed_id]
#         return []

#     return []


# # ─────────────────────────────────────────────────────────
# # Mutation
# # ─────────────────────────────────────────────────────────

# def place_domino(G: GameState, cell_a: Cell, cell_b: Cell) -> dict:
#     """
#     Place a domino occupying cell_a and cell_b for the current player.
#     Returns {'ok': True} or {'ok': False, 'error': str}.
#     """
#     if G.over:
#         return {'ok': False, 'error': 'Game is over.'}
#     if G.phase != 'place':
#         return {'ok': False, 'error': 'Not in place phase.'}

#     pair = _sorted_pair(cell_a, cell_b)

#     # Validate: pair must be in valid_placements
#     if pair not in valid_placements(G):
#         return {'ok': False, 'error': f'Invalid placement: {pair}'}

#     # Create domino
#     did = G._next_id
#     G._next_id += 1
#     d = Domino(id=did, player=G.current_player, cells=pair)
#     G.dominoes.append(d)
#     G.last_placed_id = did
#     for cell in pair:
#         G.occupied[cell] = did

#     name = G.name_h if G.current_player == 'H' else G.name_v
#     orient = 'H' if pair[0][0] == pair[1][0] else 'V'
#     G.log.append(f"{name} placed {orient} domino at {pair[0]}+{pair[1]}")

#     # Advance phase
#     if G.ruleset == 'A':
#         _end_turn(G)
#     else:
#         G.phase = 'rotate'
#         # If no rotatable pieces exist, skip rotation automatically
#         if not rotatable_domino_ids(G):
#             G.log.append("(no rotation possible — skipped)")
#             _end_turn(G)

#     return {'ok': True}


# def rotate_domino(G: GameState, domino_id: int, new_cells: tuple[Cell, Cell]) -> dict:
#     """
#     Rotate the domino with given id to occupy new_cells.
#     new_cells must be one of the results from rotation_candidates().
#     Returns {'ok': True} or {'ok': False, 'error': str}.
#     """
#     if G.phase != 'rotate':
#         return {'ok': False, 'error': 'Not in rotate phase.'}

#     if domino_id not in rotatable_domino_ids(G):
#         return {'ok': False, 'error': 'Domino not eligible for rotation.'}

#     domino = G.domino_by_id(domino_id)
#     if domino is None:
#         return {'ok': False, 'error': 'Domino not found.'}

#     candidates = rotation_candidates(G, domino)
#     target = _sorted_pair(*new_cells)
#     valid_targets = [c['cells'] for c in candidates]

#     if target not in valid_targets:
#         return {'ok': False, 'error': f'Invalid rotation target {target}. Valid: {valid_targets}'}

#     # Remove old occupancy
#     for cell in domino.cells:
#         del G.occupied[cell]

#     # Apply new position
#     domino.cells = target
#     for cell in target:
#         G.occupied[cell] = domino_id

#     name = G.name_h if G.current_player == 'H' else G.name_v
#     orient = 'H' if target[0][0] == target[1][0] else 'V'
#     G.log.append(f"{name} rotated domino #{domino_id} → {orient} at {target[0]}+{target[1]}")

#     _end_turn(G)
#     return {'ok': True}


# def skip_rotation(G: GameState) -> dict:
#     """Skip the rotation phase."""
#     if G.phase != 'rotate':
#         return {'ok': False, 'error': 'Not in rotate phase.'}
#     name = G.name_h if G.current_player == 'H' else G.name_v
#     G.log.append(f"{name} skipped rotation.")
#     _end_turn(G)
#     return {'ok': True}


# def _end_turn(G: GameState):
#     G.move_count += 1
#     G.current_player = 'V' if G.current_player == 'H' else 'H'
#     G.phase = 'place'
#     G.last_placed_id = None

#     # Check if next player has any moves
#     if not valid_placements(G):
#         loser = G.current_player
#         G.winner = 'V' if loser == 'H' else 'H'
#         G.over = True
#         winner_name = G.name_h if G.winner == 'H' else G.name_v
#         loser_name = G.name_h if loser == 'H' else G.name_v
#         G.log.append(f"🥳 {winner_name} wins! ({loser_name} has no moves.)")

# def new_game(ruleset: str, board_cells: frozenset[Cell],
#              rows: int, cols: int,
#              name_h: str = 'Player H', name_v: str = 'Player V') -> GameState:
#     return GameState(
#         ruleset=ruleset,
#         board_cells=board_cells,
#         rows=rows,
#         cols=cols,
#         name_h=name_h,
#         name_v=name_v,
#     )

"""
game.py — Turntile CGT Game Logic (pure, no rendering)
=======================================================
Ruleset D (Partizan):
  Place in your orientation (H↔, V↕), then optionally rotate
  only the tile you just placed.

Rotation rule:
  Pick one end-cell of the just-placed domino as the pivot.
  The other cell moves to any of the 3 neighbours of the pivot
  that isn't the current position of that other cell.
  This gives up to 6 candidate positions.
  A candidate is valid if both cells are active board cells
  and neither cell is occupied by a DIFFERENT domino.
"""

from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────
# Data types
# ─────────────────────────────────────────────────────────

Cell = tuple[int, int]   # (row, col)

@dataclass
class Domino:
    id: int
    player: str          # 'H' or 'V'
    cells: tuple[Cell, Cell]   # always sorted: top-left first

    def orientation(self) -> str:
        r0, c0 = self.cells[0]
        r1, c1 = self.cells[1]
        return 'V' if r1 > r0 else 'H'


@dataclass
class GameState:
    board_cells: frozenset[Cell]
    rows: int
    cols: int
    name_h: str
    name_v: str

    dominoes: list[Domino] = field(default_factory=list)
    occupied: dict[Cell, int] = field(default_factory=dict)  # cell -> domino.id
    current_player: str = 'H'
    phase: str = 'place'            # 'place' or 'rotate'
    last_placed_id: Optional[int] = None
    move_count: int = 0
    log: list[str] = field(default_factory=list)
    over: bool = False
    winner: Optional[str] = None
    _next_id: int = 0

    def domino_by_id(self, did: int) -> Optional[Domino]:
        for d in self.dominoes:
            if d.id == did:
                return d
        return None

    def is_active(self, r: int, c: int) -> bool:
        return (r, c) in self.board_cells

    def is_free(self, r: int, c: int) -> bool:
        return (r, c) in self.board_cells and (r, c) not in self.occupied


# ─────────────────────────────────────────────────────────
# Board construction helpers
# ─────────────────────────────────────────────────────────

def make_grid_board(rows: int, cols: int) -> frozenset[Cell]:
    return frozenset((r, c) for r in range(rows) for c in range(cols))


def make_custom_board(cells: set[Cell]) -> frozenset[Cell]:
    return frozenset(cells)


# ─────────────────────────────────────────────────────────
# Move generation
# ─────────────────────────────────────────────────────────

def _sorted_pair(a: Cell, b: Cell) -> tuple[Cell, Cell]:
    return (a, b) if (a[0], a[1]) <= (b[0], b[1]) else (b, a)


def h_placements(G: GameState) -> list[tuple[Cell, Cell]]:
    result = []
    for r, c in G.board_cells:
        if G.is_free(r, c) and G.is_free(r, c + 1):
            result.append(_sorted_pair((r, c), (r, c + 1)))
    return result


def v_placements(G: GameState) -> list[tuple[Cell, Cell]]:
    result = []
    for r, c in G.board_cells:
        if G.is_free(r, c) and G.is_free(r + 1, c):
            result.append(_sorted_pair((r, c), (r + 1, c)))
    return result


def valid_placements(G: GameState, player: Optional[str] = None) -> list[tuple[Cell, Cell]]:
    """H → horizontal only, V → vertical only."""
    p = player or G.current_player
    return h_placements(G) if p == 'H' else v_placements(G)


def _neighbours(r: int, c: int) -> list[Cell]:
    return [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]


def rotation_candidates(G: GameState, domino: Domino) -> list[dict]:
    """
    Returns all valid rotation outcomes for a domino.
    Each result: {'pivot': Cell, 'new_other': Cell, 'cells': tuple[Cell,Cell]}
    """
    own = set(domino.cells)
    cell_a, cell_b = domino.cells[0], domino.cells[1]
    results = []
    seen = set()

    for pivot, other in [(cell_a, cell_b), (cell_b, cell_a)]:
        for n in _neighbours(*pivot):
            if n == other:
                continue
            pr, pc = pivot
            nr, nc = n

            if (pr, pc) not in G.board_cells:
                continue
            if (nr, nc) not in G.board_cells:
                continue
            if (nr, nc) in G.occupied and (nr, nc) not in own:
                continue

            pair = _sorted_pair(pivot, n)
            if pair in seen:
                continue
            seen.add(pair)

            results.append({'pivot': pivot, 'new_other': n, 'cells': pair})

    return results


def rotatable_domino_ids(G: GameState) -> list[int]:
    """Returns the id of the just-placed domino if it can be rotated, else []."""
    if G.phase != 'rotate' or G.last_placed_id is None:
        return []
    d = G.domino_by_id(G.last_placed_id)
    if d and rotation_candidates(G, d):
        return [G.last_placed_id]
    return []


# ─────────────────────────────────────────────────────────
# Mutation
# ─────────────────────────────────────────────────────────

def place_domino(G: GameState, cell_a: Cell, cell_b: Cell) -> dict:
    if G.over:
        return {'ok': False, 'error': 'Game is over.'}
    if G.phase != 'place':
        return {'ok': False, 'error': 'Not in place phase.'}

    pair = _sorted_pair(cell_a, cell_b)
    if pair not in valid_placements(G):
        return {'ok': False, 'error': f'Invalid placement: {pair}'}

    did = G._next_id
    G._next_id += 1
    d = Domino(id=did, player=G.current_player, cells=pair)
    G.dominoes.append(d)
    G.last_placed_id = did
    for cell in pair:
        G.occupied[cell] = did

    name = G.name_h if G.current_player == 'H' else G.name_v
    orient = 'H' if pair[0][0] == pair[1][0] else 'V'
    G.log.append(f"{name} placed {orient} domino at {pair[0]}+{pair[1]}")

    G.phase = 'rotate'
    if not rotatable_domino_ids(G):
        G.log.append("(no rotation possible — skipped)")
        _end_turn(G)

    return {'ok': True}


def rotate_domino(G: GameState, domino_id: int, new_cells: tuple[Cell, Cell]) -> dict:
    if G.phase != 'rotate':
        return {'ok': False, 'error': 'Not in rotate phase.'}
    if domino_id not in rotatable_domino_ids(G):
        return {'ok': False, 'error': 'Domino not eligible for rotation.'}

    domino = G.domino_by_id(domino_id)
    if domino is None:
        return {'ok': False, 'error': 'Domino not found.'}

    candidates = rotation_candidates(G, domino)
    target = _sorted_pair(*new_cells)
    valid_targets = [c['cells'] for c in candidates]
    if target not in valid_targets:
        return {'ok': False, 'error': f'Invalid rotation target {target}. Valid: {valid_targets}'}

    for cell in domino.cells:
        del G.occupied[cell]
    domino.cells = target
    for cell in target:
        G.occupied[cell] = domino_id

    name = G.name_h if G.current_player == 'H' else G.name_v
    orient = 'H' if target[0][0] == target[1][0] else 'V'
    G.log.append(f"{name} rotated domino #{domino_id} → {orient} at {target[0]}+{target[1]}")

    _end_turn(G)
    return {'ok': True}


def skip_rotation(G: GameState) -> dict:
    if G.phase != 'rotate':
        return {'ok': False, 'error': 'Not in rotate phase.'}
    name = G.name_h if G.current_player == 'H' else G.name_v
    G.log.append(f"{name} skipped rotation.")
    _end_turn(G)
    return {'ok': True}


def _end_turn(G: GameState):
    G.move_count += 1
    G.current_player = 'V' if G.current_player == 'H' else 'H'
    G.phase = 'place'
    G.last_placed_id = None

    if not valid_placements(G):
        loser = G.current_player
        G.winner = 'V' if loser == 'H' else 'H'
        G.over = True
        winner_name = G.name_h if G.winner == 'H' else G.name_v
        loser_name = G.name_h if loser == 'H' else G.name_v
        G.log.append(f"🏆 {winner_name} wins! ({loser_name} has no moves.)")


# ─────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────

def new_game(board_cells: frozenset[Cell], rows: int, cols: int,
             name_h: str = 'Player H', name_v: str = 'Player V') -> GameState:
    return GameState(
        board_cells=board_cells,
        rows=rows,
        cols=cols,
        name_h=name_h,
        name_v=name_v,
    )