import random
import os
from collections import deque

if os.name == 'nt':
    import winsound
from rich.console import Console
from rich.style import Style
from rich.text import Text
from rich.panel import Panel
from rich.box import SIMPLE

MAP_SIZE = 33
MINE_PROBABILITY = 0.05
TOTAL_CELLS = MAP_SIZE * MAP_SIZE
TOTAL_MINES = int((TOTAL_CELLS - 1) * MINE_PROBABILITY)
CENTER = MAP_SIZE // 2

console = Console()


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.has_mine = False
        self.mine_deactivated = False
        self.is_safe = False
        self.is_orange = False
        self.is_discovered = False
        self.is_visible = False

    def get_neighbors(self, game):
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                    neighbors.append(game.grid[ny][nx])
        return neighbors

    def count_adjacent_mines(self, game):
        count = 0
        for neighbor in self.get_neighbors(game):
            if neighbor.has_mine and not neighbor.mine_deactivated:
                count += 1
        return count

    def has_adjacent_orange(self, game):
        for neighbor in self.get_neighbors(game):
            if neighbor.is_orange or (neighbor.has_mine and not neighbor.mine_deactivated):
                return True
        return False


class Game:
    def __init__(self):
        self.grid = [[Cell(x, y) for x in range(MAP_SIZE)] for y in range(MAP_SIZE)]
        self.player_x = CENTER
        self.player_y = CENTER
        self.lives = 3
        self.game_over = False
        self.won = False
        self.message = ""
        self.generate_map()

    def generate_map(self):
        self._create_safe_region()
        self._place_mines()
        self._mark_center_safe()
        self._update_discovered()
        self._update_visibility()

    def _create_safe_region(self):
        self.grid[CENTER][CENTER].is_safe = True
        
        queue = deque([(CENTER, CENTER)])
        visited = set()
        visited.add((CENTER, CENTER))
        
        target_size = int(TOTAL_CELLS * random.uniform(0.35, 0.45))
        
        while len(visited) < target_size:
            candidates = []
            for y, x in visited:
                for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < MAP_SIZE and 0 <= nx < MAP_SIZE and (nx, ny) not in visited:
                        candidates.append((nx, ny))
            
            if not candidates:
                break
            
            new_cell = random.choice(candidates)
            visited.add(new_cell)
            self.grid[new_cell[1]][new_cell[0]].is_safe = True
            queue.append(new_cell)

    def _get_frontier(self):
        frontier = []
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                cell = self.grid[y][x]
                if cell.is_safe:
                    continue
                for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < MAP_SIZE and 0 <= nx < MAP_SIZE:
                        if self.grid[ny][nx].is_safe:
                            frontier.append(cell)
                            break
        return frontier

    def _bfs_connected_safe_cells(self, start):
        visited = set()
        queue = deque([(start.x, start.y)])
        visited.add((start.x, start.y))
        
        while queue:
            cx, cy = queue.popleft()
            for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                    cell = self.grid[ny][nx]
                    if cell.is_safe and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        
        return visited

    def _place_mines(self):
        mines_placed = 0
        attempts = 0
        max_attempts = 1000
        
        while mines_placed < TOTAL_MINES and attempts < max_attempts:
            attempts += 1
            frontier = self._get_frontier()
            
            if not frontier:
                break
            
            candidates = [c for c in frontier if not c.has_mine]
            if not candidates:
                break
            
            candidate = random.choice(candidates)
            
            safe_cells = self._bfs_connected_safe_cells(self.grid[CENTER][CENTER])
            
            candidate.has_mine = True
            new_safe_cells = self._bfs_connected_safe_cells(self.grid[CENTER][CENTER])
            
            if len(new_safe_cells) < len(safe_cells) * 0.5:
                candidate.has_mine = False
                continue
            
            mines_placed += 1
            self._update_orange_cells()

    def _update_orange_cells(self):
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                cell = self.grid[y][x]
                if cell.has_mine:
                    continue
                cell.is_orange = cell.has_adjacent_orange(self)

    def _mark_center_safe(self):
        center_cell = self.grid[CENTER][CENTER]
        center_cell.is_safe = True
        center_cell.is_discovered = True
        
        for cell in center_cell.get_neighbors(self):
            if cell.has_mine:
                continue
            if cell.has_adjacent_orange(self):
                cell.is_orange = True
            else:
                cell.is_safe = True

    def _flood_fill_discover(self, start_cell):
        queue = deque([start_cell])
        discovered = set()
        
        while queue:
            cell = queue.popleft()
            if (cell.x, cell.y) in discovered:
                continue
            if cell.has_mine:
                continue
            
            discovered.add((cell.x, cell.y))
            cell.is_discovered = True
            
            if cell.is_safe:
                for neighbor in cell.get_neighbors(self):
                    if neighbor.has_mine:
                        continue
                    if not neighbor.is_discovered and (neighbor.x, neighbor.y) not in discovered:
                        queue.append(neighbor)
            elif cell.is_orange:
                pass

    def _update_discovered(self):
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                cell = self.grid[y][x]
                if cell.is_safe and not cell.is_discovered:
                    self._flood_fill_discover(cell)

    def _update_visibility(self):
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                cell = self.grid[y][x]
                cell.is_visible = (abs(x - self.player_x) <= 5 and abs(y - self.player_y) <= 5)

    def move_player(self, dx, dy):
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        if not (0 <= new_x < MAP_SIZE and 0 <= new_y < MAP_SIZE):
            return
        
        current_cell = self.grid[self.player_y][self.player_x]
        new_cell = self.grid[new_y][new_x]
        
        if new_cell.has_mine and not new_cell.mine_deactivated:
            self.reveal_all_mines()
            self.lives = 0
            self.game_over = True
            self.message = "¡Has pisado una mina! Juego terminado."
            return
        
        self.player_x = new_x
        self.player_y = new_y
        
        self._update_visibility()
        self._check_win()

    def deactivate_mine(self):
        cell = self.grid[self.player_y][self.player_x]
        
        if cell.has_mine:
            cell.mine_deactivated = True
            cell.is_safe = True
            self._update_orange_cells()
            self._update_discovered()
            self._check_win()
            self.message = "¡Mina desactivada!"
        else:
            self.lives -= 1
            self.message = f"¡No había mina! Te quedan {self.lives} vidas."
            if self.lives <= 0:
                self.game_over = True
                self.message = "¡Te has quedado sin vidas! Juego terminado."

    def use_radar(self):
        cell = self.grid[self.player_y][self.player_x]
        count = cell.count_adjacent_mines(self)
        
        notes = {
            0: ('Do', 262),
            1: ('Re', 294),
            2: ('Mi', 330),
            3: ('Fa', 349),
            4: ('Sol', 392),
        }
        
        if count >= 5:
            note_name, frequency = ('Sol+', 523)
        else:
            note_name, frequency = notes[count]
        
        if os.name == 'nt':
            try:
                winsound.Beep(frequency, 300)
            except:
                pass
        
        self.message = f"Nota: {note_name}"
        return count

    def reveal_all_mines(self):
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                cell = self.grid[y][x]
                if cell.has_mine and not cell.mine_deactivated:
                    cell.is_visible = True
                    cell.is_discovered = True

    def _check_win(self):
        mines_remaining = 0
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                cell = self.grid[y][x]
                if cell.has_mine and not cell.mine_deactivated:
                    mines_remaining += 1
        
        if mines_remaining == 0:
            self.won = True
            self.game_over = True
            self.message = "¡Felicidades! Has desactivado todas las minas."

    def get_cell_display(self, cell):
        if self.player_x == cell.x and self.player_y == cell.y:
            return "☺", "cyan"
        
        if cell.has_mine and not cell.mine_deactivated:
            if cell.is_visible:
                return "✸", "red"
            return "?", "white"
        
        if cell.mine_deactivated:
            return "✓", "green"
        
        if cell.is_discovered:
            if cell.is_safe:
                return " ", "white"
            elif cell.is_orange:
                return "▒", "yellow"
        
        if cell.is_visible:
            if cell.is_safe:
                return " ", "white"
            elif cell.is_orange:
                return "▒", "yellow"
        
        return "░", "bright_black"


def draw_game(game):
    console.clear()
    
    title = Text(" BUSCAMINAS RADAR ", justify="center", style="bold cyan")
    console.print(Panel(title, style="on blue"))
    console.print()
    
    info = Text(f" Vidas: {game.lives} | Posicion: ({game.player_x}, {game.player_y}) ", style="bold white")
    console.print(Panel(info, style="on black"))
    console.print()
    
    view_range = 8
    start_x = max(0, game.player_x - view_range)
    end_x = min(MAP_SIZE, game.player_x + view_range + 1)
    start_y = max(0, game.player_y - view_range)
    end_y = min(MAP_SIZE, game.player_y + view_range + 1)
    
    grid_text = Text()
    
    for y in range(start_y, end_y):
        row = Text()
        for x in range(start_x, end_x):
            cell = game.grid[y][x]
            char, color = game.get_cell_display(cell)
            
            style = f"on black {color} bold"
            if game.player_x == x and game.player_y == y:
                style = f"on cyan white bold"
            
            row.append_text(Text(f"{char}", style=style))
        grid_text.append_text(row)
        grid_text.append_text(Text("\n"))
    
    console.print(Panel(grid_text, style="on black", box=SIMPLE))
    console.print()
    
    if game.message:
        msg_style = "bold yellow" if "¡" in game.message else "bold white"
        console.print(Panel(Text(game.message, justify="center", style=msg_style), style="on red"))
        console.print()
    
    controls = Text("⬆⬇⬅➡: Mover | Q: Radar | W: Desactivar mina | R: Reiniciar | ESC: Salir", style="dim")
    console.print(Panel(controls, style="on black"))


def main():
    game = Game()
    
    import sys
    import tty
    import termios
    
    def get_key():
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(sys.stdin.fileno())
            try:
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    ch2 = sys.stdin.read(2)
                    if ch2 == '[A':
                        return 'up'
                    elif ch2 == '[B':
                        return 'down'
                    elif ch2 == '[C':
                        return 'right'
                    elif ch2 == '[D':
                        return 'left'
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except termios.error:
            return input("Accion (q/w/r/esc): ")[0] if input else 'q'
    
    while True:
        draw_game(game)
        
        if game.game_over:
            if game.won:
                console.print(Panel(Text(" HAS GANADO! ", justify="center", style="bold green on black"), style="green"))
            else:
                console.print(Panel(Text(" GAME OVER ", justify="center", style="bold red on black"), style="red"))
            console.print()
            console.print("[bold]Presiona R para reiniciar o ESC para salir[/bold]")
            
            key = get_key()
            if key.lower() == 'r':
                game = Game()
                continue
            elif key == '\x1b':
                break
            continue
        
        key = get_key()
        
        if key == 'up':
            game.move_player(0, -1)
        elif key == 'down':
            game.move_player(0, 1)
        elif key == 'left':
            game.move_player(-1, 0)
        elif key == 'right':
            game.move_player(1, 0)
        elif key.lower() == 'q':
            game.use_radar()
        elif key.lower() == 'w':
            game.deactivate_mine()
        elif key.lower() == 'r':
            game = Game()
        elif key == '\x1b':
            break
    
    console.print(Text("\nGracias por jugar!", style="bold cyan", justify="center"))


if __name__ == "__main__":
    main()
