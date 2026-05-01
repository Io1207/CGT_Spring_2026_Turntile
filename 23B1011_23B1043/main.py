# # """
# # main.py — Turntile CGT Game (Pygame UI)
# # ========================================
# # Run: python main.py

# # Interaction model:
# #   PLACE phase:
# #     - Hover over an empty cell to preview domino placement
# #     - Left-click to confirm placement
# #     - In rulesets B/C, after placing you enter ROTATE phase

# #   ROTATE phase:
# #     - All rotatable dominoes are outlined in gold
# #     - Click a rotatable domino to SELECT it (it turns bright gold)
# #     - All 6 (up to) valid rotation target positions are shown as dashed outlines
# #     - Click one of those target outlines to confirm rotation
# #     - Click the selected domino again to deselect
# #     - Press SPACE or click "Skip" to skip rotation

# #   Setup screen:
# #     - Choose ruleset A / B / C
# #     - Choose board: grid (2m x 2n) or one of several preset shapes
# #     - Enter player names
# #     - Click Start
# # """

# # import pygame
# # import sys
# # from game import (
# #     GameState, Domino, Cell,
# #     new_game, make_grid_board, make_custom_board,
# #     valid_placements, rotation_candidates, rotatable_domino_ids,
# #     place_domino, rotate_domino, skip_rotation,
# #     h_placements, v_placements,
# # )

# # # ─────────────────────────────────────────────────────────
# # # Constants
# # # ─────────────────────────────────────────────────────────

# # W, H_WIN = 1100, 720
# # CELL = 56          # cell size in pixels
# # GAP = 3            # gap between cells
# # SIDEBAR = 280      # right sidebar width

# # # Colours
# # BG          = (14,  14,  16)
# # SURFACE     = (22,  22,  28)
# # SURFACE2    = (30,  30,  38)
# # BORDER      = (42,  42,  54)
# # BORDER2     = (58,  58,  74)
# # TEXT        = (232, 232, 240)
# # TEXT2       = (144, 144, 168)
# # TEXT3       = (96,  96,  120)
# # ACCENT      = (201, 169, 110)
# # ACCENT2     = (13, 111,  62)

# # H_COL       = (232, 115,  74)
# # H_DIM       = ( 61,  34,  24)
# # H_MID       = (12,  53,  32)
# # V_COL       = ( 91, 141, 238)
# # V_DIM       = ( 26,  38,  64)
# # V_MID       = ( 142,  64, 128)

# # EMPTY_CELL  = (28,  28,  36)
# # HOVER_H     = ( 80,  40,  20)
# # HOVER_V     = ( 20,  40,  80)
# # ROTATABLE   = (100,  85,  40)
# # SELECTED    = (201, 169, 110)
# # TARGET_COL  = ( 80,  70,  30)
# # GREEN       = ( 76, 175, 130)
# # RED         = (200,  80,  80)

# # FPS = 60


# # # ─────────────────────────────────────────────────────────
# # # Pygame helpers
# # # ─────────────────────────────────────────────────────────

# # def cell_rect(board_origin: tuple[int,int], r: int, c: int) -> pygame.Rect:
# #     ox, oy = board_origin
# #     x = ox + c * (CELL + GAP)
# #     y = oy + r * (CELL + GAP)
# #     return pygame.Rect(x, y, CELL, CELL)


# # def pixel_to_cell(board_origin: tuple[int,int], px: int, py: int,
# #                   rows: int, cols: int) -> tuple[int,int] | None:
# #     ox, oy = board_origin
# #     col = (px - ox) // (CELL + GAP)
# #     row = (py - oy) // (CELL + GAP)
# #     # Check it's actually inside the cell (not in the gap)
# #     if 0 <= row < rows and 0 <= col < cols:
# #         rx = ox + col * (CELL + GAP)
# #         ry = oy + row * (CELL + GAP)
# #         if rx <= px < rx + CELL and ry <= py < ry + CELL:
# #             return (row, col)
# #     return None


# # def draw_rounded_rect(surf, color, rect, radius=6, width=0):
# #     pygame.draw.rect(surf, color, rect, width, border_radius=radius)


# # def draw_dashed_rect(surf, color, rect, width=2, dash=6, gap=4, radius=5):
# #     """Draw a dashed rounded rectangle outline."""
# #     x, y, w, h = rect
# #     # Draw dashes along each edge
# #     def dashes_h(x0, x1, y0):
# #         pos = x0
# #         draw = True
# #         while pos < x1:
# #             end = min(pos + (dash if draw else gap), x1)
# #             if draw:
# #                 pygame.draw.line(surf, color, (pos, y0), (end, y0), width)
# #             pos = end
# #             draw = not draw

# #     def dashes_v(y0, y1, x0):
# #         pos = y0
# #         draw = True
# #         while pos < y1:
# #             end = min(pos + (dash if draw else gap), y1)
# #             if draw:
# #                 pygame.draw.line(surf, color, (x0, pos), (x0, end), width)
# #             pos = end
# #             draw = not draw

# #     pad = radius
# #     dashes_h(x + pad, x + w - pad, y)
# #     dashes_h(x + pad, x + w - pad, y + h - 1)
# #     dashes_v(y + pad, y + h - pad, x)
# #     dashes_v(y + pad, y + h - pad, x + w - 1)


# # def draw_text(surf, text, font, color, x, y, anchor='topleft'):
# #     surf2 = font.render(text, True, color)
# #     r = surf2.get_rect(**{anchor: (x, y)})
# #     surf.blit(surf2, r)
# #     return r


# # def make_fonts():
# #     pygame.font.init()
# #     return {
# #         'title':  pygame.font.SysFont('Georgia', 28, bold=True),
# #         'head':   pygame.font.SysFont('Courier New', 13, bold=True),
# #         'body':   pygame.font.SysFont('Arial', 13),
# #         'small':  pygame.font.SysFont('Courier New', 11),
# #         'mono':   pygame.font.SysFont('Courier New', 12),
# #         'big':    pygame.font.SysFont('Georgia', 40, bold=True),
# #         'btn':    pygame.font.SysFont('Arial', 14, bold=True),
# #         'label':  pygame.font.SysFont('Arial', 11),
# #     }


# # # ─────────────────────────────────────────────────────────
# # # Board layout calculation
# # # ─────────────────────────────────────────────────────────

# # def board_origin(rows: int, cols: int) -> tuple[int,int]:
# #     """Centre the board in the left portion of the window."""
# #     board_w = cols * CELL + (cols - 1) * GAP
# #     board_h = rows * CELL + (rows - 1) * GAP
# #     avail_w = W - SIDEBAR
# #     ox = (avail_w - board_w) // 2
# #     oy = (H_WIN - board_h) // 2
# #     return max(20, ox), max(60, oy)


# # # ─────────────────────────────────────────────────────────
# # # SETUP SCREEN
# # # ─────────────────────────────────────────────────────────

# # PRESET_BOARDS = {
# #     '4×4 Grid':      (4, 4, None),
# #     '4×6 Grid':      (4, 6, None),
# #     '6×6 Grid':      (6, 6, None),
# #     '6×8 Grid':      (6, 8, None),
# #     'T-shape (6×6)': (6, 6, lambda: {(r,c) for r in range(6) for c in range(6)
# #                                      if r==0 or c in (2,3)}),
# #     'L-shape (6×6)': (6, 6, lambda: {(r,c) for r in range(6) for c in range(6)
# #                                      if c==0 or r==5}),
# #     'Plus (7×7)':    (7, 7, lambda: {(r,c) for r in range(7) for c in range(7)
# #                                      if r==3 or c==3}),
# #     'Staircase':     (6, 6, lambda: {(r,c) for r in range(6) for c in range(r,6)}),
# #     'Hollow (6×6)':  (6, 6, lambda: {(r,c) for r in range(6) for c in range(6)
# #                                      if r in (0,5) or c in (0,5)}),
# #     'Two Rooms':     (4, 8, lambda: {(r,c) for r in range(4) for c in range(8)
# #                                      if c != 3 and c != 4}),
# # }


# # class Button:
# #     def __init__(self, rect, text, font, active=False):
# #         self.rect = pygame.Rect(rect)
# #         self.text = text
# #         self.font = font
# #         self.active = active
# #         self.hovered = False

# #     def draw(self, surf):
# #         if self.active:
# #             col = ACCENT
# #             tcol = (20, 15, 5)
# #         elif self.hovered:
# #             col = SURFACE2
# #             tcol = TEXT
# #         else:
# #             col = SURFACE
# #             tcol = TEXT2
# #         draw_rounded_rect(surf, col, self.rect, 7)
# #         draw_rounded_rect(surf, BORDER2 if not self.active else ACCENT2,
# #                           self.rect, 7, 2)
# #         cx, cy = self.rect.center
# #         draw_text(surf, self.text, self.font, tcol, cx, cy, 'center')

# #     def update(self, mx, my):
# #         self.hovered = self.rect.collidepoint(mx, my)

# #     def hit(self, pos):
# #         return self.rect.collidepoint(pos)


# # class TextInput:
# #     def __init__(self, rect, font, placeholder=''):
# #         self.rect = pygame.Rect(rect)
# #         self.font = font
# #         self.text = placeholder
# #         self.active = False
# #         self.placeholder = placeholder

# #     def draw(self, surf):
# #         border_col = ACCENT2 if self.active else BORDER
# #         draw_rounded_rect(surf, SURFACE2, self.rect, 6)
# #         draw_rounded_rect(surf, border_col, self.rect, 6, 2)
# #         col = TEXT if self.text != self.placeholder else TEXT3
# #         tx = self.rect.x + 10
# #         ty = self.rect.centery
# #         draw_text(surf, self.text, self.font, col, tx, ty, 'midleft')
# #         if self.active:
# #             tw = self.font.size(self.text)[0]
# #             cx = tx + tw + 2
# #             pygame.draw.line(surf, ACCENT, (cx, ty - 9), (cx, ty + 9), 2)

# #     def handle_event(self, event):
# #         if event.type == pygame.MOUSEBUTTONDOWN:
# #             self.active = self.rect.collidepoint(event.pos)
# #             if self.active and self.text == self.placeholder:
# #                 self.text = ''
# #         elif event.type == pygame.KEYDOWN and self.active:
# #             if event.key == pygame.K_BACKSPACE:
# #                 self.text = self.text[:-1]
# #             elif event.key not in (pygame.K_RETURN, pygame.K_TAB):
# #                 if len(self.text) < 20:
# #                     self.text += event.unicode


# # class SetupScreen:
# #     def __init__(self, fonts):
# #         self.F = fonts
# #         self.selected_ruleset = 'A'
# #         self.selected_board = '6×6 Grid'
# #         self.ruleset_btns = []
# #         self.board_btns = []
# #         self.start_btn = None
# #         self.name_h = TextInput((80, 530, 200, 34), fonts['body'], 'Player H')
# #         self.name_v = TextInput((310, 530, 200, 34), fonts['body'], 'Player V')
# #         self._build_buttons()

# #     def _build_buttons(self):
# #         rulesets = [
# #             ('B', 'Ruleset B — Opponent Rotation (Partizan)'),
# #             ('C', 'Ruleset C — Own-History Rotation (Partizan)'),
# #         ]
# #         self.ruleset_btns = []
# #         for i, (key, label) in enumerate(rulesets):
# #             r = pygame.Rect(80, 140 + i * 54, 450, 44)
# #             b = Button(r, label, self.F['body'], active=(key == self.selected_ruleset))
# #             b._key = key
# #             self.ruleset_btns.append(b)

# #         self.board_btns = []
# #         keys = list(PRESET_BOARDS.keys())
# #         for i, key in enumerate(keys):
# #             col = i % 3
# #             row = i // 3
# #             r = pygame.Rect(570 + col * 178, 140 + row * 54, 168, 44)
# #             b = Button(r, key, self.F['label'], active=(key == self.selected_board))
# #             b._key = key
# #             self.board_btns.append(b)

# #         self.start_btn = Button(pygame.Rect(W//2 - 120, 630, 240, 48),
# #                                 'Start Match →', self.F['btn'])

# #     def draw(self, surf):
# #         surf.fill(BG)
# #         # Title
# #         draw_text(surf, 'TURNTILE', self.F['big'], TEXT, W//2, 45, 'center')
# #         draw_text(surf, 'IE619 · Combinatorial Game Theory',
# #                   self.F['head'], TEXT3, W//2, 82, 'center')

# #         # Section labels
# #         draw_text(surf, '01 — RULESET', self.F['head'], TEXT3, 80, 118)
# #         draw_text(surf, '02 — BOARD SHAPE', self.F['head'], TEXT3, 570, 118)
# #         draw_text(surf, '03 — PLAYER NAMES', self.F['head'], TEXT3, 80, 508)

# #         for b in self.ruleset_btns:
# #             b.draw(surf)
# #         for b in self.board_btns:
# #             b.draw(surf)

# #         # Ruleset descriptions
# #         descs = {
# #             'A': 'Either player may place a domino in any orientation. Analysed with Sprague-Grundy / nimbers.',
# #             'B': 'Place in your orientation (H↔, V↕), then optionally rotate the opponent\'s most recent tile.',
# #             'C': 'Place in your orientation, then optionally rotate ANY tile on the board (except just-placed).',
# #         }
# #         desc_y = 316
# #         pygame.draw.rect(surf, SURFACE, (80, desc_y, 450, 60), border_radius=8)
# #         pygame.draw.rect(surf, BORDER, (80, desc_y, 450, 60), 1, border_radius=8)
# #         draw_text(surf, descs[self.selected_ruleset],
# #                   self.F['small'], TEXT2, 96, desc_y + 12)

# #         # Rotation note
# #         note = 'Rotation: pick a pivot end of any eligible tile; the other end moves to any of 3 neighbours of the pivot.'
# #         draw_text(surf, note, self.F['small'], TEXT3, 80, 390)

# #         # Player names
# #         hl_col = H_COL
# #         vl_col = V_COL
# #         draw_text(surf, 'H · Horizontal (places ↔)', self.F['small'], hl_col, 80, 515)
# #         draw_text(surf, 'V · Vertical (places ↕)',   self.F['small'], vl_col, 310, 515)
# #         self.name_h.draw(surf)
# #         self.name_v.draw(surf)

# #         # Normal play note
# #         draw_text(surf, 'Normal play — player who cannot move loses.',
# #                   self.F['small'], TEXT3, 80, 578)

# #         self.start_btn.draw(surf)

# #     def handle_event(self, event):
# #         self.name_h.handle_event(event)
# #         self.name_v.handle_event(event)
# #         mx, my = pygame.mouse.get_pos()

# #         if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
# #             for b in self.ruleset_btns:
# #                 if b.hit(event.pos):
# #                     self.selected_ruleset = b._key
# #                     for bb in self.ruleset_btns:
# #                         bb.active = (bb._key == self.selected_ruleset)
# #             for b in self.board_btns:
# #                 if b.hit(event.pos):
# #                     self.selected_board = b._key
# #                     for bb in self.board_btns:
# #                         bb.active = (bb._key == self.selected_board)
# #             if self.start_btn.hit(event.pos):
# #                 return self._build_game()

# #         if event.type == pygame.MOUSEMOTION:
# #             for b in self.ruleset_btns + self.board_btns + [self.start_btn]:
# #                 b.update(mx, my)

# #         return None

# #     def _build_game(self):
# #         rows, cols, cells_fn = PRESET_BOARDS[self.selected_board]
# #         if cells_fn:
# #             cells = make_custom_board(cells_fn())
# #         else:
# #             cells = make_grid_board(rows, cols)
# #         name_h = self.name_h.text or 'Player H'
# #         name_v = self.name_v.text or 'Player V'
# #         G = new_game(self.selected_ruleset, cells, rows, cols, name_h, name_v)
# #         return G


# # # ─────────────────────────────────────────────────────────
# # # GAME SCREEN
# # # ─────────────────────────────────────────────────────────

# # class GameScreen:
# #     def __init__(self, G: GameState, fonts: dict):
# #         self.G = G
# #         self.F = fonts
# #         self.origin = board_origin(G.rows, G.cols)

# #         # Interaction state
# #         self.hover_cell: Cell | None = None        # cell under mouse
# #         self.hover_placement: tuple | None = None  # (cell_a, cell_b) preview
# #         self.selected_domino_id: int | None = None # domino chosen for rotation
# #         self.rotation_options: list[dict] = []     # candidates for selected domino

# #         # Back button
# #         self.back_btn = Button(pygame.Rect(W - SIDEBAR + 16, H_WIN - 56, 120, 36),
# #                                '← New Game', fonts['btn'])
# #         self.skip_btn = Button(pygame.Rect(W - SIDEBAR + 16, H_WIN - 100, 120, 36),
# #                                'Skip Rotation', fonts['btn'])
# #         self.log_scroll = 0

# #     # ── Drawing ────────────────────────────────────────────

# #     def draw(self, surf):
# #         surf.fill(BG)
# #         self._draw_board(surf)
# #         self._draw_sidebar(surf)
# #         if self.G.over:
# #             self._draw_win_overlay(surf)

# #     def _draw_board(self, surf):
# #         G = self.G
# #         ox, oy = self.origin
# #         rotatables = set(rotatable_domino_ids(G))

# #         # Compute target cells if a domino is selected
# #         target_options = {}   # frozenset(cells) -> option dict
# #         if self.selected_domino_id is not None:
# #             for opt in self.rotation_options:
# #                 target_options[opt['cells']] = opt

# #         # Build placement preview
# #         preview_cells: set[Cell] = set()
# #         preview_orient = None
# #         if G.phase == 'place' and self.hover_placement:
# #             preview_cells = set(self.hover_placement)
# #             a, b = self.hover_placement
# #             preview_orient = 'H' if a[0] == b[0] else 'V'

# #         # Draw each cell
# #         for r in range(G.rows):
# #             for c in range(G.cols):
# #                 cell = (r, c)
# #                 rect = cell_rect(self.origin, r, c)

# #                 if cell not in G.board_cells:
# #                     # Inactive — draw faint dot
# #                     pygame.draw.rect(surf, (20, 20, 24), rect, border_radius=4)
# #                     continue

# #                 did = G.occupied.get(cell)

# #                 if did is not None:
# #                     # Occupied by a domino
# #                     d = G.domino_by_id(did)
# #                     base = H_DIM if d.player == 'H' else V_DIM
# #                     border = H_MID if d.player == 'H' else V_MID
# #                     draw_rounded_rect(surf, base, rect, 5)

# #                     # Rotatable highlight
# #                     if did in rotatables:
# #                         if did == self.selected_domino_id:
# #                             draw_rounded_rect(surf, SURFACE, rect, 5, 3)
# #                             pygame.draw.rect(surf, SELECTED, rect, 3, border_radius=5)
# #                         else:
# #                             pygame.draw.rect(surf, ROTATABLE, rect, 2, border_radius=5)
# #                     else:
# #                         draw_rounded_rect(surf, border, rect, 5, 1)

# #                     # Orientation arrow in center of domino (only on first cell)
# #                     d_cells = sorted(d.cells)
# #                     if cell == d_cells[0]:
# #                         arrow = '↔' if d.orientation() == 'H' else '↕'
# #                         col = H_COL if d.player == 'H' else V_COL
# #                         # Draw arrow spanning across both cells
# #                         if d.orientation() == 'H':
# #                             cx = rect.x + CELL + GAP // 2 + CELL // 2
# #                         else:
# #                             cx = rect.centerx
# #                         cy = rect.centery if d.orientation() == 'H' else rect.y + CELL + GAP // 2 + CELL // 2
# #                         draw_text(surf, arrow, self.F['body'],
# #                                   (*col, 120), cx, cy, 'center')

# #                 else:
# #                     # Empty active cell
# #                     if cell in preview_cells:
# #                         col = HOVER_H if preview_orient == 'H' else HOVER_V
# #                         draw_rounded_rect(surf, col, rect, 5)
# #                         border_c = H_COL if preview_orient == 'H' else V_COL
# #                         draw_rounded_rect(surf, border_c, rect, 5, 2)
# #                     else:
# #                         draw_rounded_rect(surf, EMPTY_CELL, rect, 5)
# #                         draw_rounded_rect(surf, BORDER, rect, 5, 1)

# #                     # Rotation target?
# #                     for opt_cells, opt in target_options.items():
# #                         if cell in opt_cells:
# #                             # This empty cell is the destination of a rotation
# #                             draw_dashed_rect(surf, ACCENT, rect, 2, 8, 5)
# #                             # Show which pivot would be used
# #                             piv = opt['pivot']
# #                             if piv == cell:
# #                                 pass  # pivot stays, draw nothing extra
# #                             else:
# #                                 # The non-pivot cell destination
# #                                 pygame.draw.circle(surf, ACCENT,
# #                                                    rect.center, 5)
# #                             break

# #     def _draw_sidebar(self, surf):
# #         G = self.G
# #         F = self.F
# #         sx = W - SIDEBAR
# #         pygame.draw.rect(surf, SURFACE, (sx, 0, SIDEBAR, H_WIN))
# #         pygame.draw.line(surf, BORDER, (sx, 0), (sx, H_WIN), 1)

# #         y = 18

# #         # Title
# #         draw_text(surf, 'TURNTILE', F['title'], TEXT, sx + SIDEBAR//2, y + 10, 'center')
# #         y += 46

# #         # Ruleset badge
# #         ruleset_label = {'A': 'Ruleset A · Impartial',
# #                          'B': 'Ruleset B · Partizan',
# #                          'C': 'Ruleset C · Partizan'}[G.ruleset]
# #         pygame.draw.rect(surf, SURFACE2,
# #                          (sx + 16, y, SIDEBAR - 32, 26), border_radius=13)
# #         draw_text(surf, ruleset_label, F['small'], ACCENT,
# #                   sx + SIDEBAR//2, y + 13, 'center')
# #         y += 38

# #         # Turn indicator
# #         is_h = G.current_player == 'H'
# #         turn_col = H_COL if is_h else V_COL
# #         turn_dim = H_DIM if is_h else V_DIM
# #         turn_name = G.name_h if is_h else G.name_v
# #         pygame.draw.rect(surf, turn_dim,
# #                          (sx + 16, y, SIDEBAR - 32, 62), border_radius=8)
# #         pygame.draw.rect(surf, H_MID if is_h else V_MID,
# #                          (sx + 16, y, SIDEBAR - 32, 62), 2, border_radius=8)
# #         draw_text(surf, 'CURRENT TURN', F['label'], TEXT3,
# #                   sx + SIDEBAR//2, y + 10, 'center')
# #         draw_text(surf, turn_name, F['head'], turn_col,
# #                   sx + SIDEBAR//2, y + 28, 'center')

# #         phase_text = {
# #             'place': ('↔ place domino' if G.ruleset == 'A' or is_h
# #                       else '↕ place domino'),
# #             'rotate': 'select tile to rotate',
# #         }[G.phase]
# #         draw_text(surf, phase_text, F['small'], TEXT2,
# #                   sx + SIDEBAR//2, y + 46, 'center')
# #         y += 78

# #         # Stats
# #         pygame.draw.rect(surf, SURFACE2, (sx + 16, y, SIDEBAR - 32, 80), border_radius=7)
# #         y2 = y + 10
# #         stats = [
# #             ('Move', str(G.move_count)),
# #             ('H pieces', str(sum(1 for d in G.dominoes if d.player == 'H'))),
# #             ('V pieces', str(sum(1 for d in G.dominoes if d.player == 'V'))),
# #             ('Phase', G.phase),
# #         ]
# #         for label, val in stats:
# #             draw_text(surf, label, F['small'], TEXT3, sx + 26, y2)
# #             draw_text(surf, val, F['mono'], TEXT2, sx + SIDEBAR - 22, y2, 'topright')
# #             y2 += 16
# #         y += 90

# #         # Rotation instructions (only in rotate phase)
# #         if G.phase == 'rotate' and not G.over:
# #             rids = rotatable_domino_ids(G)
# #             if rids:
# #                 inst = [
# #                     '① Click a gold-outlined',
# #                     '   tile to select it.',
# #                     '② Click a dashed target',
# #                     '   cell to rotate there.',
# #                     '③ SPACE or "Skip" to pass.',
# #                 ]
# #                 pygame.draw.rect(surf, (30, 28, 16),
# #                                  (sx + 16, y, SIDEBAR - 32, len(inst)*16+14),
# #                                  border_radius=6)
# #                 pygame.draw.rect(surf, ACCENT2,
# #                                  (sx + 16, y, SIDEBAR - 32, len(inst)*16+14),
# #                                  1, border_radius=6)
# #                 for i, line in enumerate(inst):
# #                     draw_text(surf, line, F['small'], ACCENT, sx + 24, y + 8 + i*16)
# #                 y += len(inst)*16 + 24

# #             self.skip_btn.rect.y = y
# #             self.skip_btn.draw(surf)
# #             y += 52

# #         # Move log
# #         log_y = y
# #         draw_text(surf, 'MOVE LOG', F['label'], TEXT3, sx + 16, log_y)
# #         log_y += 18
# #         log_h = H_WIN - log_y - 60
# #         pygame.draw.rect(surf, BG, (sx + 16, log_y, SIDEBAR - 32, log_h),
# #                          border_radius=5)
# #         clip = surf.subsurface((sx + 16, log_y, SIDEBAR - 32, log_h))
# #         for i, entry in enumerate(reversed(G.log[-30:])):
# #             col = H_COL if ' H ' in entry or entry.startswith(G.name_h) else (
# #                   V_COL if ' V ' in entry or entry.startswith(G.name_v) else TEXT3)
# #             # Wrap long entries
# #             words = entry.split()
# #             line, lines = '', []
# #             for w in words:
# #                 test = line + (' ' if line else '') + w
# #                 if F['small'].size(test)[0] > SIDEBAR - 44:
# #                     lines.append(line)
# #                     line = w
# #                 else:
# #                     line = test
# #             if line:
# #                 lines.append(line)
# #             for j, ln in enumerate(lines):
# #                 ey = (i * (len(lines) * 15 + 4)) + j * 15 + 4
# #                 if 0 <= ey < log_h - 14:
# #                     draw_text(clip, ln, F['small'], col, 4, ey)

# #         # Back button
# #         self.back_btn.draw(surf)

# #     def _draw_win_overlay(self, surf):
# #         G = self.G
# #         F = self.F
# #         overlay = pygame.Surface((W, H_WIN), pygame.SRCALPHA)
# #         overlay.fill((14, 14, 16, 200))
# #         surf.blit(overlay, (0, 0))

# #         card = pygame.Rect(W//2 - 220, H_WIN//2 - 140, 440, 280)
# #         draw_rounded_rect(surf, SURFACE, card, 14)
# #         draw_rounded_rect(surf, BORDER2, card, 14, 2)

# #         winner_name = G.name_h if G.winner == 'H' else G.name_v
# #         win_col = H_COL if G.winner == 'H' else V_COL

# #         draw_text(surf, '🏆 ' + winner_name + ' wins!', F['title'], win_col,
# #                   card.centerx, card.y + 40, 'center')
# #         draw_text(surf, 'Game over — opponent has no legal moves.',
# #                   F['body'], TEXT2, card.centerx, card.y + 80, 'center')

# #         h_count = sum(1 for d in G.dominoes if d.player == 'H')
# #         v_count = sum(1 for d in G.dominoes if d.player == 'V')
# #         stats = [
# #             (str(G.move_count), 'Turns'),
# #             (str(h_count), 'H pieces'),
# #             (str(v_count), 'V pieces'),
# #         ]
# #         for i, (val, lbl) in enumerate(stats):
# #             bx = card.x + 60 + i * 110
# #             draw_text(surf, val, F['big'], ACCENT, bx + 55, card.y + 120, 'center')
# #             draw_text(surf, lbl, F['small'], TEXT3, bx + 55, card.y + 162, 'center')

# #         draw_text(surf, 'Press R to rematch · ESC for new game',
# #                   F['small'], TEXT3, card.centerx, card.y + 210, 'center')

# #     # ── Input handling ──────────────────────────────────────

# #     def handle_event(self, event, mx, my) -> str | None:
# #         """Returns 'back' to go back to setup, 'rematch' to restart, else None."""
# #         G = self.G

# #         if event.type == pygame.KEYDOWN:
# #             if event.key == pygame.K_ESCAPE:
# #                 return 'back'
# #             if event.key == pygame.K_r and G.over:
# #                 return 'rematch'
# #             if event.key == pygame.K_SPACE and G.phase == 'rotate' and not G.over:
# #                 self._do_skip()

# #         if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
# #             pos = event.pos
# #             if self.back_btn.hit(pos):
# #                 return 'back'
# #             if G.phase == 'rotate' and self.skip_btn.hit(pos):
# #                 self._do_skip()
# #                 return None
# #             self._handle_click(mx, my)

# #         if event.type == pygame.MOUSEMOTION:
# #             self._handle_hover(mx, my)
# #             self.back_btn.update(mx, my)
# #             self.skip_btn.update(mx, my)

# #         return None

# #     def _cell_at(self, mx, my) -> Cell | None:
# #         return pixel_to_cell(self.origin, mx, my, self.G.rows, self.G.cols)

# #     def _handle_hover(self, mx, my):
# #         G = self.G
# #         if G.phase != 'place' or G.over:
# #             self.hover_placement = None
# #             return

# #         cell = self._cell_at(mx, my)
# #         if cell is None or cell not in G.board_cells or cell in G.occupied:
# #             self.hover_placement = None
# #             return

# #         r, c = cell
# #         # Find a valid placement that starts at this cell
# #         placements = valid_placements(G)
# #         # Prefer placement starting at hovered cell; also check if cell is second cell
# #         for a, b in placements:
# #             if a == cell or b == cell:
# #                 self.hover_placement = (a, b)
# #                 return
# #         self.hover_placement = None

# #     def _handle_click(self, mx, my):
# #         G = self.G
# #         if G.over:
# #             return

# #         cell = self._cell_at(mx, my)

# #         # ── PLACE PHASE ──
# #         if G.phase == 'place':
# #             if cell is None or cell not in G.board_cells or cell in G.occupied:
# #                 return
# #             # Find the placement this cell belongs to
# #             placements = valid_placements(G)
# #             for a, b in placements:
# #                 if a == cell or b == cell:
# #                     place_domino(G, a, b)
# #                     self.hover_placement = None
# #                     self.selected_domino_id = None
# #                     self.rotation_options = []
# #                     return

# #         # ── ROTATE PHASE ──
# #         elif G.phase == 'rotate':
# #             rotatables = set(rotatable_domino_ids(G))

# #             if cell is not None and cell in G.occupied:
# #                 did = G.occupied[cell]

# #                 if did in rotatables:
# #                     if self.selected_domino_id == did:
# #                         # Deselect
# #                         self.selected_domino_id = None
# #                         self.rotation_options = []
# #                     else:
# #                         # Select this domino
# #                         self.selected_domino_id = did
# #                         d = G.domino_by_id(did)
# #                         self.rotation_options = rotation_candidates(G, d)
# #                     return

# #             # Clicked an empty cell — is it a rotation target?
# #             if self.selected_domino_id is not None and cell is not None:
# #                 self._try_rotate_to(cell)

# #     def _try_rotate_to(self, target_cell: Cell):
# #         G = self.G
# #         # Find the option whose 'new_other' == target_cell
# #         # (i.e. the free end of the domino would land on target_cell)
# #         d = G.domino_by_id(self.selected_domino_id)
# #         own = set(d.cells)
# #         for opt in self.rotation_options:
# #             # new_other is the cell that ISN'T the pivot — it's the one that moves
# #             if opt['new_other'] == target_cell:
# #                 result = rotate_domino(G, self.selected_domino_id, opt['cells'])
# #                 if result['ok']:
# #                     self.selected_domino_id = None
# #                     self.rotation_options = []
# #                 return

# #     def _do_skip(self):
# #         skip_rotation(self.G)
# #         self.selected_domino_id = None
# #         self.rotation_options = []


# # # ─────────────────────────────────────────────────────────
# # # MAIN LOOP
# # # ─────────────────────────────────────────────────────────

# # def main():
# #     pygame.init()
# #     screen = pygame.display.set_mode((W, H_WIN))
# #     pygame.display.set_caption('Turntile — CGT')
# #     clock = pygame.time.Clock()

# #     fonts = make_fonts()
# #     setup = SetupScreen(fonts)
# #     game_screen: GameScreen | None = None
# #     current_game: GameState | None = None

# #     while True:
# #         mx, my = pygame.mouse.get_pos()
# #         events = pygame.event.get()

# #         for event in events:
# #             if event.type == pygame.QUIT:
# #                 pygame.quit()
# #                 sys.exit()

# #             if game_screen is None:
# #                 # Setup screen
# #                 result = setup.handle_event(event)
# #                 if result is not None:
# #                     current_game = result
# #                     game_screen = GameScreen(current_game, fonts)
# #             else:
# #                 action = game_screen.handle_event(event, mx, my)
# #                 if action == 'back':
# #                     game_screen = None
# #                     current_game = None
# #                     setup = SetupScreen(fonts)
# #                 elif action == 'rematch':
# #                     G = current_game
# #                     new_G = new_game(G.ruleset, G.board_cells, G.rows, G.cols,
# #                                      G.name_h, G.name_v)
# #                     current_game = new_G
# #                     game_screen = GameScreen(new_G, fonts)

# #         if game_screen is None:
# #             setup.draw(screen)
# #         else:
# #             game_screen.draw(screen)

# #         pygame.display.flip()
# #         clock.tick(FPS)


# # if __name__ == '__main__':
# #     main()

# """
# main.py — Turntile CGT Game (Pygame UI)
# ========================================
# Run: python main.py

# Interaction model:
#   PLACE phase:
#     - Hover over an empty cell to preview domino placement
#     - Left-click to confirm placement
#     - In rulesets B/C/D, after placing you enter ROTATE phase

#   ROTATE phase:
#     - All rotatable dominoes are outlined in gold
#     - Click a rotatable domino to SELECT it (it turns bright gold)
#     - All 6 (up to) valid rotation target positions are shown as dashed outlines
#     - Click one of those target outlines to confirm rotation
#     - Click the selected domino again to deselect
#     - Press SPACE or click "Skip" to skip rotation

#   Setup screen:
#     - Choose ruleset A / B / C / D
#     - Choose board: grid (2m x 2n) or one of several preset shapes
#     - Enter player names
#     - Click Start
# """

# import pygame
# import sys
# from game import (
#     GameState, Domino, Cell,
#     new_game, make_grid_board, make_custom_board,
#     valid_placements, rotation_candidates, rotatable_domino_ids,
#     place_domino, rotate_domino, skip_rotation,
#     h_placements, v_placements,
# )

# # ─────────────────────────────────────────────────────────
# # Constants
# # ─────────────────────────────────────────────────────────

# W, H_WIN = 1100, 720
# CELL = 56          # cell size in pixels
# GAP = 3            # gap between cells
# SIDEBAR = 280      # right sidebar width

# # Colours
# BG          = (14,  14,  16)
# SURFACE     = (22,  22,  28)
# SURFACE2    = (30,  30,  38)
# BORDER      = (42,  42,  54)
# BORDER2     = (58,  58,  74)
# TEXT        = (232, 232, 240)
# TEXT2       = (144, 144, 168)
# TEXT3       = (96,  96,  120)
# ACCENT      = (201, 169, 110)
# ACCENT2     = (13, 111,  62)

# H_COL       = (232, 115,  74)
# H_DIM       = ( 61,  34,  24)
# H_MID       = (12,  53,  32)
# V_COL       = ( 91, 141, 238)
# V_DIM       = ( 26,  38,  64)
# V_MID       = ( 142,  64, 128)

# EMPTY_CELL  = (28,  28,  36)
# HOVER_H     = ( 80,  40,  20)
# HOVER_V     = ( 20,  40,  80)
# ROTATABLE   = (100,  85,  40)
# SELECTED    = (201, 169, 110)
# TARGET_COL  = ( 80,  70,  30)
# GREEN       = ( 76, 175, 130)
# RED         = (200,  80,  80)

# FPS = 60


# # ─────────────────────────────────────────────────────────
# # Pygame helpers
# # ─────────────────────────────────────────────────────────

# def cell_rect(board_origin: tuple[int,int], r: int, c: int) -> pygame.Rect:
#     ox, oy = board_origin
#     x = ox + c * (CELL + GAP)
#     y = oy + r * (CELL + GAP)
#     return pygame.Rect(x, y, CELL, CELL)


# def pixel_to_cell(board_origin: tuple[int,int], px: int, py: int,
#                   rows: int, cols: int) -> tuple[int,int] | None:
#     ox, oy = board_origin
#     col = (px - ox) // (CELL + GAP)
#     row = (py - oy) // (CELL + GAP)
#     # Check it's actually inside the cell (not in the gap)
#     if 0 <= row < rows and 0 <= col < cols:
#         rx = ox + col * (CELL + GAP)
#         ry = oy + row * (CELL + GAP)
#         if rx <= px < rx + CELL and ry <= py < ry + CELL:
#             return (row, col)
#     return None


# def draw_rounded_rect(surf, color, rect, radius=6, width=0):
#     pygame.draw.rect(surf, color, rect, width, border_radius=radius)


# def draw_dashed_rect(surf, color, rect, width=2, dash=6, gap=4, radius=5):
#     """Draw a dashed rounded rectangle outline."""
#     x, y, w, h = rect
#     def dashes_h(x0, x1, y0):
#         pos = x0
#         draw = True
#         while pos < x1:
#             end = min(pos + (dash if draw else gap), x1)
#             if draw:
#                 pygame.draw.line(surf, color, (pos, y0), (end, y0), width)
#             pos = end
#             draw = not draw

#     def dashes_v(y0, y1, x0):
#         pos = y0
#         draw = True
#         while pos < y1:
#             end = min(pos + (dash if draw else gap), y1)
#             if draw:
#                 pygame.draw.line(surf, color, (x0, pos), (x0, end), width)
#             pos = end
#             draw = not draw

#     pad = radius
#     dashes_h(x + pad, x + w - pad, y)
#     dashes_h(x + pad, x + w - pad, y + h - 1)
#     dashes_v(y + pad, y + h - pad, x)
#     dashes_v(y + pad, y + h - pad, x + w - 1)


# def draw_text(surf, text, font, color, x, y, anchor='topleft'):
#     surf2 = font.render(text, True, color)
#     r = surf2.get_rect(**{anchor: (x, y)})
#     surf.blit(surf2, r)
#     return r


# def make_fonts():
#     pygame.font.init()
#     return {
#         'title':  pygame.font.SysFont('Georgia', 28, bold=True),
#         'head':   pygame.font.SysFont('Courier New', 13, bold=True),
#         'body':   pygame.font.SysFont('Arial', 13),
#         'small':  pygame.font.SysFont('Courier New', 11),
#         'mono':   pygame.font.SysFont('Courier New', 12),
#         'big':    pygame.font.SysFont('Georgia', 40, bold=True),
#         'btn':    pygame.font.SysFont('Arial', 14, bold=True),
#         'label':  pygame.font.SysFont('Arial', 11),
#     }


# # ─────────────────────────────────────────────────────────
# # Board layout calculation
# # ─────────────────────────────────────────────────────────

# def board_origin(rows: int, cols: int) -> tuple[int,int]:
#     """Centre the board in the left portion of the window."""
#     board_w = cols * CELL + (cols - 1) * GAP
#     board_h = rows * CELL + (rows - 1) * GAP
#     avail_w = W - SIDEBAR
#     ox = (avail_w - board_w) // 2
#     oy = (H_WIN - board_h) // 2
#     return max(20, ox), max(60, oy)


# # ─────────────────────────────────────────────────────────
# # SETUP SCREEN
# # ─────────────────────────────────────────────────────────

# PRESET_BOARDS = {
#     '4×4 Grid':      (4, 4, None),
#     '4×6 Grid':      (4, 6, None),
#     '6×6 Grid':      (6, 6, None),
#     '6×8 Grid':      (6, 8, None),
#     'T-shape (6×6)': (6, 6, lambda: {(r,c) for r in range(6) for c in range(6)
#                                      if r==0 or c in (2,3)}),
#     'L-shape (6×6)': (6, 6, lambda: {(r,c) for r in range(6) for c in range(6)
#                                      if c==0 or r==5}),
#     'Plus (7×7)':    (7, 7, lambda: {(r,c) for r in range(7) for c in range(7)
#                                      if r==3 or c==3}),
#     'Staircase':     (6, 6, lambda: {(r,c) for r in range(6) for c in range(r,6)}),
#     'Hollow (6×6)':  (6, 6, lambda: {(r,c) for r in range(6) for c in range(6)
#                                      if r in (0,5) or c in (0,5)}),
#     'Two Rooms':     (4, 8, lambda: {(r,c) for r in range(4) for c in range(8)
#                                      if c != 3 and c != 4}),
# }


# class Button:
#     def __init__(self, rect, text, font, active=False):
#         self.rect = pygame.Rect(rect)
#         self.text = text
#         self.font = font
#         self.active = active
#         self.hovered = False

#     def draw(self, surf):
#         if self.active:
#             col = ACCENT
#             tcol = (20, 15, 5)
#         elif self.hovered:
#             col = SURFACE2
#             tcol = TEXT
#         else:
#             col = SURFACE
#             tcol = TEXT2
#         draw_rounded_rect(surf, col, self.rect, 7)
#         draw_rounded_rect(surf, BORDER2 if not self.active else ACCENT2,
#                           self.rect, 7, 2)
#         cx, cy = self.rect.center
#         draw_text(surf, self.text, self.font, tcol, cx, cy, 'center')

#     def update(self, mx, my):
#         self.hovered = self.rect.collidepoint(mx, my)

#     def hit(self, pos):
#         return self.rect.collidepoint(pos)


# class TextInput:
#     def __init__(self, rect, font, placeholder=''):
#         self.rect = pygame.Rect(rect)
#         self.font = font
#         self.text = placeholder
#         self.active = False
#         self.placeholder = placeholder

#     def draw(self, surf):
#         border_col = ACCENT2 if self.active else BORDER
#         draw_rounded_rect(surf, SURFACE2, self.rect, 6)
#         draw_rounded_rect(surf, border_col, self.rect, 6, 2)
#         col = TEXT if self.text != self.placeholder else TEXT3
#         tx = self.rect.x + 10
#         ty = self.rect.centery
#         draw_text(surf, self.text, self.font, col, tx, ty, 'midleft')
#         if self.active:
#             tw = self.font.size(self.text)[0]
#             cx = tx + tw + 2
#             pygame.draw.line(surf, ACCENT, (cx, ty - 9), (cx, ty + 9), 2)

#     def handle_event(self, event):
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             self.active = self.rect.collidepoint(event.pos)
#             if self.active and self.text == self.placeholder:
#                 self.text = ''
#         elif event.type == pygame.KEYDOWN and self.active:
#             if event.key == pygame.K_BACKSPACE:
#                 self.text = self.text[:-1]
#             elif event.key not in (pygame.K_RETURN, pygame.K_TAB):
#                 if len(self.text) < 20:
#                     self.text += event.unicode


# class SetupScreen:
#     def __init__(self, fonts):
#         self.F = fonts
#         self.selected_ruleset = 'B'
#         self.selected_board = '6×6 Grid'
#         self.ruleset_btns = []
#         self.board_btns = []
#         self.start_btn = None
#         self.name_h = TextInput((80, 530, 200, 34), fonts['body'], 'Player H')
#         self.name_v = TextInput((310, 530, 200, 34), fonts['body'], 'Player V')
#         self._build_buttons()

#     def _build_buttons(self):
#         rulesets = [
#             ('B', 'Ruleset B — Opponent Rotation (Partizan)'),
#             ('C', 'Ruleset C — Own-History Rotation (Partizan)'),
#             ('D', 'Ruleset D — Self Rotation (Partizan)'),
#         ]
#         self.ruleset_btns = []
#         for i, (key, label) in enumerate(rulesets):
#             r = pygame.Rect(80, 140 + i * 54, 450, 44)
#             b = Button(r, label, self.F['body'], active=(key == self.selected_ruleset))
#             b._key = key
#             self.ruleset_btns.append(b)

#         self.board_btns = []
#         keys = list(PRESET_BOARDS.keys())
#         for i, key in enumerate(keys):
#             col = i % 3
#             row = i // 3
#             r = pygame.Rect(570 + col * 178, 140 + row * 54, 168, 44)
#             b = Button(r, key, self.F['label'], active=(key == self.selected_board))
#             b._key = key
#             self.board_btns.append(b)

#         self.start_btn = Button(pygame.Rect(W//2 - 120, 630, 240, 48),
#                                 'Start Match →', self.F['btn'])

#     def draw(self, surf):
#         surf.fill(BG)
#         # Title
#         draw_text(surf, 'TURNTILE', self.F['big'], TEXT, W//2, 45, 'center')
#         draw_text(surf, 'IE619 · Combinatorial Game Theory',
#                   self.F['head'], TEXT3, W//2, 82, 'center')

#         # Section labels
#         draw_text(surf, '01 — RULESET', self.F['head'], TEXT3, 80, 118)
#         draw_text(surf, '02 — BOARD SHAPE', self.F['head'], TEXT3, 570, 118)
#         draw_text(surf, '03 — PLAYER NAMES', self.F['head'], TEXT3, 80, 508)

#         for b in self.ruleset_btns:
#             b.draw(surf)
#         for b in self.board_btns:
#             b.draw(surf)

#         # Ruleset descriptions
#         descs = {
#             'A': 'Either player may place a domino in any orientation. Analysed with Sprague-Grundy / nimbers.',
#             'B': 'Place in your orientation (H↔, V↕), then optionally rotate the opponent\'s most recent tile.',
#             'C': 'Place in your orientation, then optionally rotate ANY tile on the board (except just-placed).',
#             'D': 'Place in your orientation, then optionally rotate only the tile you just placed.',
#         }
#         desc_y = 316
#         pygame.draw.rect(surf, SURFACE, (80, desc_y, 450, 60), border_radius=8)
#         pygame.draw.rect(surf, BORDER, (80, desc_y, 450, 60), 1, border_radius=8)
#         draw_text(surf, descs[self.selected_ruleset],
#                   self.F['small'], TEXT2, 96, desc_y + 12)

#         # Rotation note
#         note = 'Rotation: pick a pivot end of any eligible tile; the other end moves to any of 3 neighbours of the pivot.'
#         draw_text(surf, note, self.F['small'], TEXT3, 80, 390)

#         # Player names
#         hl_col = H_COL
#         vl_col = V_COL
#         draw_text(surf, 'H · Horizontal (places ↔)', self.F['small'], hl_col, 80, 515)
#         draw_text(surf, 'V · Vertical (places ↕)',   self.F['small'], vl_col, 310, 515)
#         self.name_h.draw(surf)
#         self.name_v.draw(surf)

#         # Normal play note
#         draw_text(surf, 'Normal play — player who cannot move loses.',
#                   self.F['small'], TEXT3, 80, 578)

#         self.start_btn.draw(surf)

#     def handle_event(self, event):
#         self.name_h.handle_event(event)
#         self.name_v.handle_event(event)
#         mx, my = pygame.mouse.get_pos()

#         if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#             for b in self.ruleset_btns:
#                 if b.hit(event.pos):
#                     self.selected_ruleset = b._key
#                     for bb in self.ruleset_btns:
#                         bb.active = (bb._key == self.selected_ruleset)
#             for b in self.board_btns:
#                 if b.hit(event.pos):
#                     self.selected_board = b._key
#                     for bb in self.board_btns:
#                         bb.active = (bb._key == self.selected_board)
#             if self.start_btn.hit(event.pos):
#                 return self._build_game()

#         if event.type == pygame.MOUSEMOTION:
#             for b in self.ruleset_btns + self.board_btns + [self.start_btn]:
#                 b.update(mx, my)

#         return None

#     def _build_game(self):
#         rows, cols, cells_fn = PRESET_BOARDS[self.selected_board]
#         if cells_fn:
#             cells = make_custom_board(cells_fn())
#         else:
#             cells = make_grid_board(rows, cols)
#         name_h = self.name_h.text or 'Player H'
#         name_v = self.name_v.text or 'Player V'
#         G = new_game(self.selected_ruleset, cells, rows, cols, name_h, name_v)
#         return G


# # ─────────────────────────────────────────────────────────
# # GAME SCREEN
# # ─────────────────────────────────────────────────────────

# class GameScreen:
#     def __init__(self, G: GameState, fonts: dict):
#         self.G = G
#         self.F = fonts
#         self.origin = board_origin(G.rows, G.cols)

#         # Interaction state
#         self.hover_cell: Cell | None = None
#         self.hover_placement: tuple | None = None
#         self.selected_domino_id: int | None = None
#         self.rotation_options: list[dict] = []

#         # Back button
#         self.back_btn = Button(pygame.Rect(W - SIDEBAR + 16, H_WIN - 56, 120, 36),
#                                '← New Game', fonts['btn'])
#         self.skip_btn = Button(pygame.Rect(W - SIDEBAR + 16, H_WIN - 100, 120, 36),
#                                'Skip Rotation', fonts['btn'])
#         self.log_scroll = 0

#     # ── Drawing ────────────────────────────────────────────

#     def draw(self, surf):
#         surf.fill(BG)
#         self._draw_board(surf)
#         self._draw_sidebar(surf)
#         if self.G.over:
#             self._draw_win_overlay(surf)

#     def _draw_board(self, surf):
#         G = self.G
#         ox, oy = self.origin
#         rotatables = set(rotatable_domino_ids(G))

#         # Compute target cells if a domino is selected
#         target_options = {}
#         if self.selected_domino_id is not None:
#             for opt in self.rotation_options:
#                 target_options[opt['cells']] = opt

#         # Build placement preview
#         preview_cells: set[Cell] = set()
#         preview_orient = None
#         if G.phase == 'place' and self.hover_placement:
#             preview_cells = set(self.hover_placement)
#             a, b = self.hover_placement
#             preview_orient = 'H' if a[0] == b[0] else 'V'

#         # Draw each cell
#         for r in range(G.rows):
#             for c in range(G.cols):
#                 cell = (r, c)
#                 rect = cell_rect(self.origin, r, c)

#                 if cell not in G.board_cells:
#                     pygame.draw.rect(surf, (20, 20, 24), rect, border_radius=4)
#                     continue

#                 did = G.occupied.get(cell)

#                 if did is not None:
#                     d = G.domino_by_id(did)
#                     base = H_DIM if d.player == 'H' else V_DIM
#                     border = H_MID if d.player == 'H' else V_MID
#                     draw_rounded_rect(surf, base, rect, 5)

#                     if did in rotatables:
#                         if did == self.selected_domino_id:
#                             draw_rounded_rect(surf, SURFACE, rect, 5, 3)
#                             pygame.draw.rect(surf, SELECTED, rect, 3, border_radius=5)
#                         else:
#                             pygame.draw.rect(surf, ROTATABLE, rect, 2, border_radius=5)
#                     else:
#                         draw_rounded_rect(surf, border, rect, 5, 1)

#                     d_cells = sorted(d.cells)
#                     if cell == d_cells[0]:
#                         arrow = '↔' if d.orientation() == 'H' else '↕'
#                         col = H_COL if d.player == 'H' else V_COL
#                         if d.orientation() == 'H':
#                             cx = rect.x + CELL + GAP // 2 + CELL // 2
#                         else:
#                             cx = rect.centerx
#                         cy = rect.centery if d.orientation() == 'H' else rect.y + CELL + GAP // 2 + CELL // 2
#                         draw_text(surf, arrow, self.F['body'],
#                                   (*col, 120), cx, cy, 'center')

#                 else:
#                     if cell in preview_cells:
#                         col = HOVER_H if preview_orient == 'H' else HOVER_V
#                         draw_rounded_rect(surf, col, rect, 5)
#                         border_c = H_COL if preview_orient == 'H' else V_COL
#                         draw_rounded_rect(surf, border_c, rect, 5, 2)
#                     else:
#                         draw_rounded_rect(surf, EMPTY_CELL, rect, 5)
#                         draw_rounded_rect(surf, BORDER, rect, 5, 1)

#                     for opt_cells, opt in target_options.items():
#                         if cell in opt_cells:
#                             draw_dashed_rect(surf, ACCENT, rect, 2, 8, 5)
#                             piv = opt['pivot']
#                             if piv != cell:
#                                 pygame.draw.circle(surf, ACCENT, rect.center, 5)
#                             break

#     def _draw_sidebar(self, surf):
#         G = self.G
#         F = self.F
#         sx = W - SIDEBAR
#         pygame.draw.rect(surf, SURFACE, (sx, 0, SIDEBAR, H_WIN))
#         pygame.draw.line(surf, BORDER, (sx, 0), (sx, H_WIN), 1)

#         y = 18

#         draw_text(surf, 'TURNTILE', F['title'], TEXT, sx + SIDEBAR//2, y + 10, 'center')
#         y += 46

#         ruleset_label = {'A': 'Ruleset A · Impartial',
#                          'B': 'Ruleset B · Partizan',
#                          'C': 'Ruleset C · Partizan',
#                          'D': 'Ruleset D · Partizan'}[G.ruleset]
#         pygame.draw.rect(surf, SURFACE2,
#                          (sx + 16, y, SIDEBAR - 32, 26), border_radius=13)
#         draw_text(surf, ruleset_label, F['small'], ACCENT,
#                   sx + SIDEBAR//2, y + 13, 'center')
#         y += 38

#         is_h = G.current_player == 'H'
#         turn_col = H_COL if is_h else V_COL
#         turn_dim = H_DIM if is_h else V_DIM
#         turn_name = G.name_h if is_h else G.name_v
#         pygame.draw.rect(surf, turn_dim,
#                          (sx + 16, y, SIDEBAR - 32, 62), border_radius=8)
#         pygame.draw.rect(surf, H_MID if is_h else V_MID,
#                          (sx + 16, y, SIDEBAR - 32, 62), 2, border_radius=8)
#         draw_text(surf, 'CURRENT TURN', F['label'], TEXT3,
#                   sx + SIDEBAR//2, y + 10, 'center')
#         draw_text(surf, turn_name, F['head'], turn_col,
#                   sx + SIDEBAR//2, y + 28, 'center')

#         phase_text = {
#             'place': ('↔ place domino' if G.ruleset == 'A' or is_h
#                       else '↕ place domino'),
#             'rotate': 'select tile to rotate',
#         }[G.phase]
#         draw_text(surf, phase_text, F['small'], TEXT2,
#                   sx + SIDEBAR//2, y + 46, 'center')
#         y += 78

#         pygame.draw.rect(surf, SURFACE2, (sx + 16, y, SIDEBAR - 32, 80), border_radius=7)
#         y2 = y + 10
#         stats = [
#             ('Move', str(G.move_count)),
#             ('H pieces', str(sum(1 for d in G.dominoes if d.player == 'H'))),
#             ('V pieces', str(sum(1 for d in G.dominoes if d.player == 'V'))),
#             ('Phase', G.phase),
#         ]
#         for label, val in stats:
#             draw_text(surf, label, F['small'], TEXT3, sx + 26, y2)
#             draw_text(surf, val, F['mono'], TEXT2, sx + SIDEBAR - 22, y2, 'topright')
#             y2 += 16
#         y += 90

#         if G.phase == 'rotate' and not G.over:
#             rids = rotatable_domino_ids(G)
#             if rids:
#                 inst = [
#                     '① Click a gold-outlined',
#                     '   tile to select it.',
#                     '② Click a dashed target',
#                     '   cell to rotate there.',
#                     '③ SPACE or "Skip" to pass.',
#                 ]
#                 pygame.draw.rect(surf, (30, 28, 16),
#                                  (sx + 16, y, SIDEBAR - 32, len(inst)*16+14),
#                                  border_radius=6)
#                 pygame.draw.rect(surf, ACCENT2,
#                                  (sx + 16, y, SIDEBAR - 32, len(inst)*16+14),
#                                  1, border_radius=6)
#                 for i, line in enumerate(inst):
#                     draw_text(surf, line, F['small'], ACCENT, sx + 24, y + 8 + i*16)
#                 y += len(inst)*16 + 24

#             self.skip_btn.rect.y = y
#             self.skip_btn.draw(surf)
#             y += 52

#         log_y = y
#         draw_text(surf, 'MOVE LOG', F['label'], TEXT3, sx + 16, log_y)
#         log_y += 18
#         log_h = H_WIN - log_y - 60
#         pygame.draw.rect(surf, BG, (sx + 16, log_y, SIDEBAR - 32, log_h),
#                          border_radius=5)
#         clip = surf.subsurface((sx + 16, log_y, SIDEBAR - 32, log_h))
#         for i, entry in enumerate(reversed(G.log[-30:])):
#             col = H_COL if ' H ' in entry or entry.startswith(G.name_h) else (
#                   V_COL if ' V ' in entry or entry.startswith(G.name_v) else TEXT3)
#             words = entry.split()
#             line, lines = '', []
#             for w in words:
#                 test = line + (' ' if line else '') + w
#                 if F['small'].size(test)[0] > SIDEBAR - 44:
#                     lines.append(line)
#                     line = w
#                 else:
#                     line = test
#             if line:
#                 lines.append(line)
#             for j, ln in enumerate(lines):
#                 ey = (i * (len(lines) * 15 + 4)) + j * 15 + 4
#                 if 0 <= ey < log_h - 14:
#                     draw_text(clip, ln, F['small'], col, 4, ey)

#         self.back_btn.draw(surf)

#     def _draw_win_overlay(self, surf):
#         G = self.G
#         F = self.F
#         overlay = pygame.Surface((W, H_WIN), pygame.SRCALPHA)
#         overlay.fill((14, 14, 16, 200))
#         surf.blit(overlay, (0, 0))

#         card = pygame.Rect(W//2 - 220, H_WIN//2 - 140, 440, 280)
#         draw_rounded_rect(surf, SURFACE, card, 14)
#         draw_rounded_rect(surf, BORDER2, card, 14, 2)

#         winner_name = G.name_h if G.winner == 'H' else G.name_v
#         win_col = H_COL if G.winner == 'H' else V_COL

#         draw_text(surf, '🏆 ' + winner_name + ' wins!', F['title'], win_col,
#                   card.centerx, card.y + 40, 'center')
#         draw_text(surf, 'Game over — opponent has no legal moves.',
#                   F['body'], TEXT2, card.centerx, card.y + 80, 'center')

#         h_count = sum(1 for d in G.dominoes if d.player == 'H')
#         v_count = sum(1 for d in G.dominoes if d.player == 'V')
#         stats = [
#             (str(G.move_count), 'Turns'),
#             (str(h_count), 'H pieces'),
#             (str(v_count), 'V pieces'),
#         ]
#         for i, (val, lbl) in enumerate(stats):
#             bx = card.x + 60 + i * 110
#             draw_text(surf, val, F['big'], ACCENT, bx + 55, card.y + 120, 'center')
#             draw_text(surf, lbl, F['small'], TEXT3, bx + 55, card.y + 162, 'center')

#         draw_text(surf, 'Press R to rematch · ESC for new game',
#                   F['small'], TEXT3, card.centerx, card.y + 210, 'center')

#     # ── Input handling ──────────────────────────────────────

#     def handle_event(self, event, mx, my) -> str | None:
#         G = self.G

#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 return 'back'
#             if event.key == pygame.K_r and G.over:
#                 return 'rematch'
#             if event.key == pygame.K_SPACE and G.phase == 'rotate' and not G.over:
#                 self._do_skip()

#         if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#             pos = event.pos
#             if self.back_btn.hit(pos):
#                 return 'back'
#             if G.phase == 'rotate' and self.skip_btn.hit(pos):
#                 self._do_skip()
#                 return None
#             self._handle_click(mx, my)

#         if event.type == pygame.MOUSEMOTION:
#             self._handle_hover(mx, my)
#             self.back_btn.update(mx, my)
#             self.skip_btn.update(mx, my)

#         return None

#     def _cell_at(self, mx, my) -> Cell | None:
#         return pixel_to_cell(self.origin, mx, my, self.G.rows, self.G.cols)

#     def _handle_hover(self, mx, my):
#         G = self.G
#         if G.phase != 'place' or G.over:
#             self.hover_placement = None
#             return

#         cell = self._cell_at(mx, my)
#         if cell is None or cell not in G.board_cells or cell in G.occupied:
#             self.hover_placement = None
#             return

#         r, c = cell
#         placements = valid_placements(G)
#         for a, b in placements:
#             if a == cell or b == cell:
#                 self.hover_placement = (a, b)
#                 return
#         self.hover_placement = None

#     def _handle_click(self, mx, my):
#         G = self.G
#         if G.over:
#             return

#         cell = self._cell_at(mx, my)

#         if G.phase == 'place':
#             if cell is None or cell not in G.board_cells or cell in G.occupied:
#                 return
#             placements = valid_placements(G)
#             for a, b in placements:
#                 if a == cell or b == cell:
#                     place_domino(G, a, b)
#                     self.hover_placement = None
#                     self.selected_domino_id = None
#                     self.rotation_options = []
#                     return

#         elif G.phase == 'rotate':
#             rotatables = set(rotatable_domino_ids(G))

#             if cell is not None and cell in G.occupied:
#                 did = G.occupied[cell]

#                 if did in rotatables:
#                     if self.selected_domino_id == did:
#                         self.selected_domino_id = None
#                         self.rotation_options = []
#                     else:
#                         self.selected_domino_id = did
#                         d = G.domino_by_id(did)
#                         self.rotation_options = rotation_candidates(G, d)
#                     return

#             if self.selected_domino_id is not None and cell is not None:
#                 self._try_rotate_to(cell)

#     def _try_rotate_to(self, target_cell: Cell):
#         G = self.G
#         d = G.domino_by_id(self.selected_domino_id)
#         for opt in self.rotation_options:
#             if opt['new_other'] == target_cell:
#                 result = rotate_domino(G, self.selected_domino_id, opt['cells'])
#                 if result['ok']:
#                     self.selected_domino_id = None
#                     self.rotation_options = []
#                 return

#     def _do_skip(self):
#         skip_rotation(self.G)
#         self.selected_domino_id = None
#         self.rotation_options = []


# # ─────────────────────────────────────────────────────────
# # MAIN LOOP
# # ─────────────────────────────────────────────────────────

# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((W, H_WIN))
#     pygame.display.set_caption('Turntile — CGT')
#     clock = pygame.time.Clock()

#     fonts = make_fonts()
#     setup = SetupScreen(fonts)
#     game_screen: GameScreen | None = None
#     current_game: GameState | None = None

#     while True:
#         mx, my = pygame.mouse.get_pos()
#         events = pygame.event.get()

#         for event in events:
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()

#             if game_screen is None:
#                 result = setup.handle_event(event)
#                 if result is not None:
#                     current_game = result
#                     game_screen = GameScreen(current_game, fonts)
#             else:
#                 action = game_screen.handle_event(event, mx, my)
#                 if action == 'back':
#                     game_screen = None
#                     current_game = None
#                     setup = SetupScreen(fonts)
#                 elif action == 'rematch':
#                     G = current_game
#                     new_G = new_game(G.ruleset, G.board_cells, G.rows, G.cols,
#                                      G.name_h, G.name_v)
#                     current_game = new_G
#                     game_screen = GameScreen(new_G, fonts)

#         if game_screen is None:
#             setup.draw(screen)
#         else:
#             game_screen.draw(screen)

#         pygame.display.flip()
#         clock.tick(FPS)


# if __name__ == '__main__':
#     main()

"""
main.py — Turntile CGT Game (Pygame UI)
========================================
Run: python main.py

Ruleset D (Partizan):
  Place in your orientation (H↔, V↕), then optionally rotate
  only the tile you just placed.

Interaction model:
  PLACE phase:
    - Hover over an empty cell to preview domino placement
    - Left-click to confirm placement

  ROTATE phase:
    - Your just-placed domino is outlined in gold
    - Click it to SELECT it (turns bright gold)
    - All valid rotation target positions are shown as dashed outlines
    - Click one of those target outlines to confirm rotation
    - Click the selected domino again to deselect
    - Press SPACE or click "Skip" to skip rotation

  Setup screen:
    - Choose board shape
    - Enter player names
    - Click Start
"""

import pygame
import sys
from game import (
    GameState, Domino, Cell,
    new_game, make_grid_board, make_custom_board,
    valid_placements, rotation_candidates, rotatable_domino_ids,
    place_domino, rotate_domino, skip_rotation,
    h_placements, v_placements,
)

# ─────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────

W, H_WIN = 1100, 720
CELL = 56
GAP = 3
SIDEBAR = 280

BG          = (14,  14,  16)
SURFACE     = (22,  22,  28)
SURFACE2    = (30,  30,  38)
BORDER      = (42,  42,  54)
BORDER2     = (58,  58,  74)
TEXT        = (232, 232, 240)
TEXT2       = (144, 144, 168)
TEXT3       = (96,  96,  120)
ACCENT      = (201, 169, 110)
ACCENT2     = (13, 111,  62)

H_COL       = (232, 115,  74)
H_DIM       = ( 61,  34,  24)
H_MID       = ( 12,  53,  32)
V_COL       = ( 91, 141, 238)
V_DIM       = ( 26,  38,  64)
V_MID       = (142,  64, 128)

EMPTY_CELL  = (28,  28,  36)
HOVER_H     = ( 80,  40,  20)
HOVER_V     = ( 20,  40,  80)
ROTATABLE   = (100,  85,  40)
SELECTED    = (201, 169, 110)

FPS = 60


# ─────────────────────────────────────────────────────────
# Pygame helpers
# ─────────────────────────────────────────────────────────

def cell_rect(board_origin: tuple[int,int], r: int, c: int) -> pygame.Rect:
    ox, oy = board_origin
    return pygame.Rect(ox + c * (CELL + GAP), oy + r * (CELL + GAP), CELL, CELL)


def pixel_to_cell(board_origin: tuple[int,int], px: int, py: int,
                  rows: int, cols: int) -> tuple[int,int] | None:
    ox, oy = board_origin
    col = (px - ox) // (CELL + GAP)
    row = (py - oy) // (CELL + GAP)
    if 0 <= row < rows and 0 <= col < cols:
        rx = ox + col * (CELL + GAP)
        ry = oy + row * (CELL + GAP)
        if rx <= px < rx + CELL and ry <= py < ry + CELL:
            return (row, col)
    return None


def draw_rounded_rect(surf, color, rect, radius=6, width=0):
    pygame.draw.rect(surf, color, rect, width, border_radius=radius)


def draw_dashed_rect(surf, color, rect, width=2, dash=6, gap=4, radius=5):
    x, y, w, h = rect
    def dashes_h(x0, x1, y0):
        pos, draw = x0, True
        while pos < x1:
            end = min(pos + (dash if draw else gap), x1)
            if draw:
                pygame.draw.line(surf, color, (pos, y0), (end, y0), width)
            pos, draw = end, not draw
    def dashes_v(y0, y1, x0):
        pos, draw = y0, True
        while pos < y1:
            end = min(pos + (dash if draw else gap), y1)
            if draw:
                pygame.draw.line(surf, color, (x0, pos), (x0, end), width)
            pos, draw = end, not draw
    pad = radius
    dashes_h(x + pad, x + w - pad, y)
    dashes_h(x + pad, x + w - pad, y + h - 1)
    dashes_v(y + pad, y + h - pad, x)
    dashes_v(y + pad, y + h - pad, x + w - 1)


def draw_text(surf, text, font, color, x, y, anchor='topleft'):
    surf2 = font.render(text, True, color)
    r = surf2.get_rect(**{anchor: (x, y)})
    surf.blit(surf2, r)
    return r


def make_fonts():
    pygame.font.init()
    return {
        'title':  pygame.font.SysFont('Georgia', 28, bold=True),
        'head':   pygame.font.SysFont('Courier New', 13, bold=True),
        'body':   pygame.font.SysFont('Arial', 13),
        'small':  pygame.font.SysFont('Courier New', 11),
        'mono':   pygame.font.SysFont('Courier New', 12),
        'big':    pygame.font.SysFont('Georgia', 40, bold=True),
        'btn':    pygame.font.SysFont('Arial', 14, bold=True),
        'label':  pygame.font.SysFont('Arial', 11),
    }


def board_origin(rows: int, cols: int) -> tuple[int,int]:
    board_w = cols * CELL + (cols - 1) * GAP
    board_h = rows * CELL + (rows - 1) * GAP
    avail_w = W - SIDEBAR
    ox = (avail_w - board_w) // 2
    oy = (H_WIN - board_h) // 2
    return max(20, ox), max(60, oy)


# ─────────────────────────────────────────────────────────
# SETUP SCREEN
# ─────────────────────────────────────────────────────────

PRESET_BOARDS = {
    '4×4 Grid':      (4, 4, None),
    '4×6 Grid':      (4, 6, None),
    '6×6 Grid':      (6, 6, None),
    '6×8 Grid':      (6, 8, None),
    'T-shape (6×6)': (6, 6, lambda: {(r,c) for r in range(6) for c in range(6)
                                     if r==0 or c in (2,3)}),
    'L-shape (6×6)': (6, 6, lambda: {(r,c) for r in range(6) for c in range(6)
                                     if c==0 or r==5}),
    'Plus (7×7)':    (7, 7, lambda: {(r,c) for r in range(7) for c in range(7)
                                     if r==3 or c==3}),
    'Staircase':     (6, 6, lambda: {(r,c) for r in range(6) for c in range(r,6)}),
    'Hollow (6×6)':  (6, 6, lambda: {(r,c) for r in range(6) for c in range(6)
                                     if r in (0,5) or c in (0,5)}),
    'Two Rooms':     (4, 8, lambda: {(r,c) for r in range(4) for c in range(8)
                                     if c != 3 and c != 4}),
}


class Button:
    def __init__(self, rect, text, font, active=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.active = active
        self.hovered = False

    def draw(self, surf):
        col  = ACCENT      if self.active  else (SURFACE2 if self.hovered else SURFACE)
        tcol = (20, 15, 5) if self.active  else (TEXT      if self.hovered else TEXT2)
        bcol = ACCENT2     if self.active  else BORDER2
        draw_rounded_rect(surf, col, self.rect, 7)
        draw_rounded_rect(surf, bcol, self.rect, 7, 2)
        cx, cy = self.rect.center
        draw_text(surf, self.text, self.font, tcol, cx, cy, 'center')

    def update(self, mx, my):
        self.hovered = self.rect.collidepoint(mx, my)

    def hit(self, pos):
        return self.rect.collidepoint(pos)


class TextInput:
    def __init__(self, rect, font, placeholder=''):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.text = placeholder
        self.active = False
        self.placeholder = placeholder

    def draw(self, surf):
        border_col = ACCENT2 if self.active else BORDER
        draw_rounded_rect(surf, SURFACE2, self.rect, 6)
        draw_rounded_rect(surf, border_col, self.rect, 6, 2)
        col = TEXT if self.text != self.placeholder else TEXT3
        tx, ty = self.rect.x + 10, self.rect.centery
        draw_text(surf, self.text, self.font, col, tx, ty, 'midleft')
        if self.active:
            tw = self.font.size(self.text)[0]
            cx = tx + tw + 2
            pygame.draw.line(surf, ACCENT, (cx, ty - 9), (cx, ty + 9), 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active and self.text == self.placeholder:
                self.text = ''
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in (pygame.K_RETURN, pygame.K_TAB):
                if len(self.text) < 20:
                    self.text += event.unicode


class SetupScreen:
    def __init__(self, fonts):
        self.F = fonts
        self.selected_board = '6×6 Grid'
        self.board_btns = []
        self.start_btn = None
        self.name_h = TextInput((80, 430, 200, 34), fonts['body'], 'Player H')
        self.name_v = TextInput((310, 430, 200, 34), fonts['body'], 'Player V')
        self._build_buttons()

    def _build_buttons(self):
        self.board_btns = []
        keys = list(PRESET_BOARDS.keys())
        for i, key in enumerate(keys):
            col = i % 3
            row = i // 3
            r = pygame.Rect(80 + col * 200, 160 + row * 54, 188, 44)
            b = Button(r, key, self.F['label'], active=(key == self.selected_board))
            b._key = key
            self.board_btns.append(b)

        self.start_btn = Button(pygame.Rect(W//2 - 120, 560, 240, 48),
                                'Start Match →', self.F['btn'])

    def draw(self, surf):
        surf.fill(BG)

        draw_text(surf, 'TURNTILE', self.F['big'], TEXT, W//2, 45, 'center')
        draw_text(surf, 'IE619 · Combinatorial Game Theory',
                  self.F['head'], TEXT3, W//2, 82, 'center')

        # Ruleset description (fixed, no selector)
        pygame.draw.rect(surf, SURFACE, (80, 110, 940, 30), border_radius=8)
        pygame.draw.rect(surf, BORDER,  (80, 110, 940, 30), 1, border_radius=8)
        desc = 'Ruleset D · Partizan — place in your orientation, then optionally rotate only the tile you just placed.'
        draw_text(surf, desc, self.F['small'], TEXT2, 96, 118)

        draw_text(surf, '01 — BOARD SHAPE', self.F['head'], TEXT3, 80, 148)
        for b in self.board_btns:
            b.draw(surf)

        note = 'Rotation: pick a pivot end of your tile; the other end moves to any of up to 3 neighbours of the pivot.'
        draw_text(surf, note, self.F['small'], TEXT3, 80, 380)

        draw_text(surf, '02 — PLAYER NAMES', self.F['head'], TEXT3, 80, 412)
        draw_text(surf, 'H · Horizontal (places ↔)', self.F['small'], H_COL, 80, 418)
        draw_text(surf, 'V · Vertical   (places ↕)', self.F['small'], V_COL, 310, 418)
        self.name_h.draw(surf)
        self.name_v.draw(surf)

        draw_text(surf, 'Normal play — player who cannot move loses.',
                  self.F['small'], TEXT3, 80, 478)

        self.start_btn.draw(surf)

    def handle_event(self, event):
        self.name_h.handle_event(event)
        self.name_v.handle_event(event)
        mx, my = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self.board_btns:
                if b.hit(event.pos):
                    self.selected_board = b._key
                    for bb in self.board_btns:
                        bb.active = (bb._key == self.selected_board)
            if self.start_btn.hit(event.pos):
                return self._build_game()

        if event.type == pygame.MOUSEMOTION:
            for b in self.board_btns + [self.start_btn]:
                b.update(mx, my)

        return None

    def _build_game(self):
        rows, cols, cells_fn = PRESET_BOARDS[self.selected_board]
        cells = make_custom_board(cells_fn()) if cells_fn else make_grid_board(rows, cols)
        name_h = self.name_h.text or 'Player H'
        name_v = self.name_v.text or 'Player V'
        return new_game(cells, rows, cols, name_h, name_v)

class GameScreen:
    def __init__(self, G: GameState, fonts: dict):
        self.G = G
        self.F = fonts
        self.origin = board_origin(G.rows, G.cols)

        self.hover_placement: tuple | None = None
        self.selected_domino_id: int | None = None
        self.rotation_options: list[dict] = []

        self.back_btn = Button(pygame.Rect(W - SIDEBAR + 16, H_WIN - 56, 120, 36),
                               '← New Game', fonts['btn'])
        self.skip_btn = Button(pygame.Rect(W - SIDEBAR + 16, H_WIN - 100, 120, 36),
                               'Skip Rotation', fonts['btn'])

    # ── Drawing ────────────────────────────────────────────

    def draw(self, surf):
        surf.fill(BG)
        self._draw_board(surf)
        self._draw_sidebar(surf)
        if self.G.over:
            self._draw_win_overlay(surf)

    def _draw_board(self, surf):
        G = self.G
        rotatables = set(rotatable_domino_ids(G))

        target_options = {}
        if self.selected_domino_id is not None:
            for opt in self.rotation_options:
                target_options[opt['cells']] = opt

        preview_cells: set[Cell] = set()
        preview_orient = None
        if G.phase == 'place' and self.hover_placement:
            preview_cells = set(self.hover_placement)
            a, b = self.hover_placement
            preview_orient = 'H' if a[0] == b[0] else 'V'

        for r in range(G.rows):
            for c in range(G.cols):
                cell = (r, c)
                rect = cell_rect(self.origin, r, c)

                if cell not in G.board_cells:
                    pygame.draw.rect(surf, (20, 20, 24), rect, border_radius=4)
                    continue

                did = G.occupied.get(cell)

                if did is not None:
                    d = G.domino_by_id(did)
                    base   = H_DIM if d.player == 'H' else V_DIM
                    border = H_MID if d.player == 'H' else V_MID
                    draw_rounded_rect(surf, base, rect, 5)

                    if did in rotatables:
                        if did == self.selected_domino_id:
                            draw_rounded_rect(surf, SURFACE, rect, 5, 3)
                            pygame.draw.rect(surf, SELECTED, rect, 3, border_radius=5)
                        else:
                            pygame.draw.rect(surf, ROTATABLE, rect, 2, border_radius=5)
                    else:
                        draw_rounded_rect(surf, border, rect, 5, 1)

                    d_cells = sorted(d.cells)
                    if cell == d_cells[0]:
                        arrow = '↔' if d.orientation() == 'H' else '↕'
                        col = H_COL if d.player == 'H' else V_COL
                        cx = (rect.x + CELL + GAP // 2 + CELL // 2
                              if d.orientation() == 'H' else rect.centerx)
                        cy = (rect.centery if d.orientation() == 'H'
                              else rect.y + CELL + GAP // 2 + CELL // 2)
                        draw_text(surf, arrow, self.F['body'], (*col, 120), cx, cy, 'center')

                else:
                    if cell in preview_cells:
                        col = HOVER_H if preview_orient == 'H' else HOVER_V
                        draw_rounded_rect(surf, col, rect, 5)
                        draw_rounded_rect(surf, H_COL if preview_orient == 'H' else V_COL,
                                          rect, 5, 2)
                    else:
                        draw_rounded_rect(surf, EMPTY_CELL, rect, 5)
                        draw_rounded_rect(surf, BORDER, rect, 5, 1)

                    for opt_cells, opt in target_options.items():
                        if cell in opt_cells:
                            draw_dashed_rect(surf, ACCENT, rect, 2, 8, 5)
                            if opt['pivot'] != cell:
                                pygame.draw.circle(surf, ACCENT, rect.center, 5)
                            break

    def _draw_sidebar(self, surf):
        G = self.G
        F = self.F
        sx = W - SIDEBAR
        pygame.draw.rect(surf, SURFACE, (sx, 0, SIDEBAR, H_WIN))
        pygame.draw.line(surf, BORDER, (sx, 0), (sx, H_WIN), 1)

        y = 18
        draw_text(surf, 'TURNTILE', F['title'], TEXT, sx + SIDEBAR//2, y + 10, 'center')
        y += 46

        pygame.draw.rect(surf, SURFACE2, (sx + 16, y, SIDEBAR - 32, 26), border_radius=13)
        draw_text(surf, 'Ruleset D · Partizan', F['small'], ACCENT,
                  sx + SIDEBAR//2, y + 13, 'center')
        y += 38

        is_h = G.current_player == 'H'
        turn_col  = H_COL if is_h else V_COL
        turn_dim  = H_DIM if is_h else V_DIM
        turn_mid  = H_MID if is_h else V_MID
        turn_name = G.name_h if is_h else G.name_v
        pygame.draw.rect(surf, turn_dim,  (sx + 16, y, SIDEBAR - 32, 62), border_radius=8)
        pygame.draw.rect(surf, turn_mid,  (sx + 16, y, SIDEBAR - 32, 62), 2, border_radius=8)
        draw_text(surf, 'CURRENT TURN', F['label'], TEXT3, sx + SIDEBAR//2, y + 10, 'center')
        draw_text(surf, turn_name,        F['head'],  turn_col, sx + SIDEBAR//2, y + 28, 'center')
        phase_text = ('↔ place domino' if G.phase == 'place' and is_h else
                      '↕ place domino' if G.phase == 'place' else
                      'select tile to rotate')
        draw_text(surf, phase_text, F['small'], TEXT2, sx + SIDEBAR//2, y + 46, 'center')
        y += 78

        pygame.draw.rect(surf, SURFACE2, (sx + 16, y, SIDEBAR - 32, 80), border_radius=7)
        y2 = y + 10
        for label, val in [
            ('Move',    str(G.move_count)),
            ('H pieces', str(sum(1 for d in G.dominoes if d.player == 'H'))),
            ('V pieces', str(sum(1 for d in G.dominoes if d.player == 'V'))),
            ('Phase',   G.phase),
        ]:
            draw_text(surf, label, F['small'], TEXT3, sx + 26, y2)
            draw_text(surf, val,   F['mono'],  TEXT2, sx + SIDEBAR - 22, y2, 'topright')
            y2 += 16
        y += 90

        if G.phase == 'rotate' and not G.over:
            rids = rotatable_domino_ids(G)
            if rids:
                inst = [
                    '① Click the gold-outlined',
                    '   tile to select it.',
                    '② Click a dashed target',
                    '   cell to rotate there.',
                    '③ SPACE or "Skip" to pass.',
                ]
                box_h = len(inst) * 16 + 14
                pygame.draw.rect(surf, (30, 28, 16),  (sx + 16, y, SIDEBAR - 32, box_h), border_radius=6)
                pygame.draw.rect(surf, ACCENT2,        (sx + 16, y, SIDEBAR - 32, box_h), 1, border_radius=6)
                for i, line in enumerate(inst):
                    draw_text(surf, line, F['small'], ACCENT, sx + 24, y + 8 + i * 16)
                y += box_h + 10

            self.skip_btn.rect.y = y
            self.skip_btn.draw(surf)
            y += 52

        # Move log
        log_y = y
        draw_text(surf, 'MOVE LOG', F['label'], TEXT3, sx + 16, log_y)
        log_y += 18
        log_h = H_WIN - log_y - 60
        pygame.draw.rect(surf, BG, (sx + 16, log_y, SIDEBAR - 32, log_h), border_radius=5)
        clip = surf.subsurface((sx + 16, log_y, SIDEBAR - 32, log_h))
        for i, entry in enumerate(reversed(G.log[-30:])):
            col = (H_COL if entry.startswith(G.name_h) else
                   V_COL if entry.startswith(G.name_v) else TEXT3)
            words = entry.split()
            line, lines = '', []
            for w in words:
                test = line + (' ' if line else '') + w
                if F['small'].size(test)[0] > SIDEBAR - 44:
                    lines.append(line); line = w
                else:
                    line = test
            if line:
                lines.append(line)
            for j, ln in enumerate(lines):
                ey = (i * (len(lines) * 15 + 4)) + j * 15 + 4
                if 0 <= ey < log_h - 14:
                    draw_text(clip, ln, F['small'], col, 4, ey)

        self.back_btn.draw(surf)

    def _draw_win_overlay(self, surf):
        G = self.G
        F = self.F
        overlay = pygame.Surface((W, H_WIN), pygame.SRCALPHA)
        overlay.fill((14, 14, 16, 200))
        surf.blit(overlay, (0, 0))

        card = pygame.Rect(W//2 - 220, H_WIN//2 - 140, 440, 280)
        draw_rounded_rect(surf, SURFACE, card, 14)
        draw_rounded_rect(surf, BORDER2, card, 14, 2)

        winner_name = G.name_h if G.winner == 'H' else G.name_v
        win_col = H_COL if G.winner == 'H' else V_COL
        draw_text(surf, '🏆 ' + winner_name + ' wins!', F['title'], win_col,
                  card.centerx, card.y + 40, 'center')
        draw_text(surf, 'Game over — opponent has no legal moves.',
                  F['body'], TEXT2, card.centerx, card.y + 80, 'center')

        h_count = sum(1 for d in G.dominoes if d.player == 'H')
        v_count = sum(1 for d in G.dominoes if d.player == 'V')
        for i, (val, lbl) in enumerate([
            (str(G.move_count), 'Turns'),
            (str(h_count),      'H pieces'),
            (str(v_count),      'V pieces'),
        ]):
            bx = card.x + 60 + i * 110
            draw_text(surf, val, F['big'],   ACCENT, bx + 55, card.y + 120, 'center')
            draw_text(surf, lbl, F['small'], TEXT3,  bx + 55, card.y + 162, 'center')

        draw_text(surf, 'Press R to rematch · ESC for new game',
                  F['small'], TEXT3, card.centerx, card.y + 210, 'center')

    # ── Input handling ──────────────────────────────────────

    def handle_event(self, event, mx, my) -> str | None:
        G = self.G

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            if event.key == pygame.K_r and G.over:
                return 'rematch'
            if event.key == pygame.K_SPACE and G.phase == 'rotate' and not G.over:
                self._do_skip()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.hit(event.pos):
                return 'back'
            if G.phase == 'rotate' and self.skip_btn.hit(event.pos):
                self._do_skip()
                return None
            self._handle_click(mx, my)

        if event.type == pygame.MOUSEMOTION:
            self._handle_hover(mx, my)
            self.back_btn.update(mx, my)
            self.skip_btn.update(mx, my)

        return None

    def _cell_at(self, mx, my) -> Cell | None:
        return pixel_to_cell(self.origin, mx, my, self.G.rows, self.G.cols)

    def _handle_hover(self, mx, my):
        G = self.G
        if G.phase != 'place' or G.over:
            self.hover_placement = None
            return
        cell = self._cell_at(mx, my)
        if cell is None or cell not in G.board_cells or cell in G.occupied:
            self.hover_placement = None
            return
        for a, b in valid_placements(G):
            if a == cell or b == cell:
                self.hover_placement = (a, b)
                return
        self.hover_placement = None

    def _handle_click(self, mx, my):
        G = self.G
        if G.over:
            return
        cell = self._cell_at(mx, my)

        if G.phase == 'place':
            if cell is None or cell not in G.board_cells or cell in G.occupied:
                return
            for a, b in valid_placements(G):
                if a == cell or b == cell:
                    place_domino(G, a, b)
                    self.hover_placement = None
                    self.selected_domino_id = None
                    self.rotation_options = []
                    return

        elif G.phase == 'rotate':
            rotatables = set(rotatable_domino_ids(G))
            if cell is not None and cell in G.occupied:
                did = G.occupied[cell]
                if did in rotatables:
                    if self.selected_domino_id == did:
                        self.selected_domino_id = None
                        self.rotation_options = []
                    else:
                        self.selected_domino_id = did
                        self.rotation_options = rotation_candidates(G, G.domino_by_id(did))
                    return

            if self.selected_domino_id is not None and cell is not None:
                for opt in self.rotation_options:
                    if opt['new_other'] == cell:
                        result = rotate_domino(G, self.selected_domino_id, opt['cells'])
                        if result['ok']:
                            self.selected_domino_id = None
                            self.rotation_options = []
                        return

    def _do_skip(self):
        skip_rotation(self.G)
        self.selected_domino_id = None
        self.rotation_options = []


# ─────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H_WIN))
    pygame.display.set_caption('Turntile — CGT IE619')
    clock = pygame.time.Clock()

    fonts = make_fonts()
    setup = SetupScreen(fonts)
    game_screen: GameScreen | None = None
    current_game: GameState | None = None

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_screen is None:
                result = setup.handle_event(event)
                if result is not None:
                    current_game = result
                    game_screen = GameScreen(current_game, fonts)
            else:
                action = game_screen.handle_event(event, mx, my)
                if action == 'back':
                    game_screen = None
                    current_game = None
                    setup = SetupScreen(fonts)
                elif action == 'rematch':
                    G = current_game
                    current_game = new_game(G.board_cells, G.rows, G.cols, G.name_h, G.name_v)
                    game_screen = GameScreen(current_game, fonts)

        if game_screen is None:
            setup.draw(screen)
        else:
            game_screen.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()