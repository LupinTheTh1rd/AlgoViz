import pygame
from tkinter import *
from tkinter import messagebox
from colorCodes import *
from queue import PriorityQueue

WIDTH=800
WIN=pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* shortest path algorithm")

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = WIDTH
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neightbors = []
        if self.col > 0 and not grid[self.row][self.col-1].is_barrier():   # LEFT
            self.neighbors.append(grid[self.row][self.col-1])

        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_barrier():   # RIGHT
            self.neighbors.append(grid[self.row][self.col+1])

        if self.row > 0 and not grid[self.row-1][self.col].is_barrier():   # UP
            self.neighbors.append(grid[self.row-1][self.col])

        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_barrier():   # DOWN
            self.neighbors.append(grid[self.row+1][self.col])

    def __lt__(self, other):
        return False
        

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, start, current, draw):
    while current in came_from:
        current = came_from[current]
        if current != start:
            current.make_path()
        draw()


def shortestPath(draw, grid, start, end):
    count=0
    open_set = PriorityQueue()

    open_set.put((0, count, start))
    came_from = {}

    g_score = {spot: float("inf") for row in grid for spot in row}      # keeping track of current shortest distance to get from start node to current node
    g_score[start]=0
    f_score = {spot: float("inf") for row in grid for spot in row}      # keping track of PREDICTED distance from current node to the end node *** using manhattan distance formula
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}     # to check from priority queue whether or not the node is present (tracker); essentially a copy of q, but can check easily

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            current = open_set.get()[2] # index2 to get node from (fScore, count, node)
            open_set_hash.remove(current)   # sync contents of priority q with hash, so fetch is correct

            if current == end:
                reconstruct_path(came_from, start, end, draw)
                end.make_end()
                Tk().wm_withdraw() #to hide the main window
                messagebox.showinfo('A* Shortest Path algorithm','Shortest path found!\nPath has been highlighted in purple.')
                return True        # we found shortest path, now draw path

            for neighbor in current.neighbors:
                temp_g_score = g_score[current]+1       # g score for next node is g score for current+1 (since moving to next)

                if temp_g_score < g_score[neighbor]:    # if we find a better path for the current node, update q
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                    
                    if neighbor not in open_set_hash:
                        count+=1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
                        if neighbor != end:
                            neighbor.make_open()        # depending on better g score, this node is taken into account for further guesses (made open/green)

            draw()

            if current != start:
                current.make_closed()   # nodes which are determined to not be the shortest path, can be ruled off as not needed (made closed/red)
    
    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in  range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))
    # for j in range(rows):
    #     pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col

def main(win, width):
    ROWS = 20
    grid = make_grid(ROWS, WIDTH)

    start=None
    end=None
    run=True

    while run:
        draw(win, grid, ROWS, WIDTH)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                
                elif spot != end and spot != start:
                    spot.make_barrier()


            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()

                if spot == start:
                    start = None
                if spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    
                    shortestPath(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_r:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, WIDTH)


    



