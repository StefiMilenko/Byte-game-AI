# imports
import math

import numpy
import numpy as np
import copy


class BytePiece:
    White = 'O'
    Black = 'X'


# vraca figuru na vrhu novog stack-a
def add_stack(first: list, second: list) -> BytePiece:
    second.extend(first)
    return second[-1]



# vraca listu figura koje se uklanjaju sa steka
def remove_stack(stack: list, idx_from: int) -> list:
    substack = stack[idx_from:]
    del stack[idx_from:]
    return substack


def get_new_coords(old_coords: (int, int), direction:int, board_width: int):
    ve = ValueError("Destinaciona pozicija je van dometa")
    left_edge = old_coords[1] == 0
    right_edge = old_coords[1] == (board_width - 1)
    upper_edge = old_coords[0] == 0
    lower_edge = old_coords[0] == (board_width - 1)
    
    match direction:
        case Direction.UpLeft:
            if upper_edge or left_edge:
                raise ve
            else:
                return old_coords[0] - 1, old_coords[1] - 1
        case Direction.UpRight:
            if upper_edge or right_edge:
                raise ve
            else:
                return old_coords[0] - 1, old_coords[1] + 1
        case Direction.DownLeft:
            if lower_edge or left_edge:
                raise ve
            else:
                return old_coords[0] + 1, old_coords[1] - 1
        case Direction.DownRight:
            if lower_edge or right_edge:
                raise ve
            else:
                return old_coords[0] + 1, old_coords[1] + 1
    raise ValueError("Invalidna vrednost za smer")


class Direction:
    UpLeft = 1
    UpRight = 2
    DownLeft = 3
    DownRight = 4


def convert_format(moves): # pretvori koordinate u lep format
    result = []
    for mov in moves:
        converted_move = (
            f'{chr(ord("A") + mov[0][0])}{mov[0][1] + 1}',
            f'{chr(ord("A") + mov[1][0])}{mov[1][1] + 1}',
            str(mov[2])
        )
        result.append(converted_move)
    return tuple(result)


# proverava da li moze da se postavi stack na drugi stack
def can_put_stack(first: list, idx: int, second:list) -> (bool, list, BytePiece):
    st = first[idx:]
    len1 = len(st)
    len2 = len(second)
    new_len = len1 + len2

    if(idx!=0 and (idx>=len2)):
        return False,st,None  # ne moze biti nize ili jednako visini u starom steku
    
    if new_len == 8:
        return True,st, first[-1]  #Moze potez i ima pobednika
    elif new_len < 8:
         return True,st, None #Moze potez, al nema pobednika

    return False,st, None


class ByteBoard:

    def __init__(self, width: int = 8, player_first: bool = True):
        if width != 8 and width != 10 and width != 16:  # jedini brojevi za koje vazi uslov iz zadatka
            raise ValueError("Invalidna velicina table")
        self.player_turn = player_first
        self.x_score = 0
        self.o_score = 0
        self.max_score = ((width - 2) * width) / 16
        self.is_over = False
        self.x_turn = True
        self.width = width
        self.board = np.empty((width, width), dtype=object)
        for row in range(width):
            for col in range(width):
                if (row + col) % 2 != 0:
                    self.board[row, col] = []
                elif row % 2 != 0:
                    self.board[row, col] = [] if (row == (width - 1)) else [BytePiece.Black]
                else:
                    self.board[row, col] = [] if (row == 0) else [BytePiece.White]
        self.board_moved = np.empty((width, width), dtype=object)
        for row in range(width):
            for col in range(width):
                if (row + col) % 2 != 0:
                    self.board_moved[row, col] = False

    def copy(self):
        new_state = ByteBoard(width=self.width)
        new_state.board = copy.deepcopy(self.board)
        new_state.board_moved = copy.deepcopy(self.board_moved)
        new_state.x_turn = self.x_turn
        new_state.player_turn = self.player_turn
        new_state.is_over = self.is_over
        new_state.o_score = self.o_score
        new_state.x_score = self.x_score
        new_state.max_score = self.max_score
        return new_state

    def change_player(self):
        self.x_turn = not self.x_turn
        self.player_turn = not self.player_turn

    def generate_states(self):
        valid_states = []
        state = self.copy()
        valid_moves = state.generate_moves()
        if not valid_moves:
            cpy = state.copy()
            cpy.change_player()
            valid_states.append(cpy)
        for mov in valid_moves:
            cpy = state.copy()
            cpy.ai_move(mov)
            valid_states.append(cpy)
        return valid_states

    def ai_move(self, mov):
        from_pos = (mov[0][0], mov[0][1])
        to_pos = mov[1][0], mov[1][1]
        idx = mov[2]
        valid, stek, score = can_put_stack(self.board[from_pos], idx, self.board[to_pos])
        if score == BytePiece.White:
            self.o_score += 1
            self.board[to_pos].clear()
            remove_stack(self.board[from_pos[0], from_pos[1]], idx)
        elif score == BytePiece.Black:
            self.x_score += 1
            self.board[to_pos].clear()
            remove_stack(self.board[from_pos[0], from_pos[1]], idx)
        else:
            add_stack(stek, self.board[to_pos])
            remove_stack(self.board[from_pos[0], from_pos[1]], idx)
        self.board_moved[from_pos] = True
        self.board_moved[to_pos] = True
        self.x_turn = not self.x_turn
        self.player_turn = not self.player_turn
        return True  # ok potez odigran



    # postavlja stack/figuru na polje
    def set_tile(self, row: int, column: int, stack: list):
        if row >= self.width or column >= self.width or row < 0 or column < 0:
            raise ValueError("Pozicija je van table")
        else:
            self.board[row, column] = stack

    def check_if_end(self):
        if self.x_score > self.max_score / 2:
            return True, "X", self.x_score
        elif self.o_score > self.max_score / 2:
            return True, "O", self.o_score
        return False, None, None



    def validate_move(self, from_pos:(int,int), to_pos:(int,int), idx:int) -> (list,BytePiece):
        piece_color = BytePiece.Black if self.x_turn else BytePiece.White
        
        if not ((0 <= from_pos[0] < self.width) and (0 <= from_pos[1] < self.width)):
            raise ValueError("Pozicija van dometa")
        if not self.board[from_pos]:
            raise ValueError("Pozicija nema figura")
        if (idx >= len(self.board[from_pos])) or (self.board[from_pos][idx] != piece_color):
            raise ValueError("Invalidna figura izabrana")
        
        valid,stek, score = can_put_stack(self.board[from_pos], idx, self.board[to_pos])
        if not valid:
            raise ValueError("Ne moze se staviti stek na vrh tog steka")

        valid_moves = self.generate_moves()

        validan = (from_pos,to_pos,idx) in valid_moves
        if not validan:
            raise ValueError("Invalidan potez.")

        return (stek,score)

    def move(self, row: int, column: int, idx: int, direction:int):
        try:
            from_pos = (row, column)
            to_pos = get_new_coords(old_coords=from_pos, direction=direction, board_width=self.width)
            stek,score = self.validate_move(from_pos,to_pos,idx)

            if score == BytePiece.White:
                self.o_score += 1

                self.board[to_pos].clear()
                remove_stack(self.board[row, column], idx)
            elif score == BytePiece.Black:
                self.x_score += 1

                self.board[to_pos].clear()
                remove_stack(self.board[row, column], idx)
            else:
                add_stack(stek, self.board[to_pos])
                remove_stack(self.board[row, column], idx)
            self.board_moved[from_pos] = True
            self.board_moved[to_pos] = True
            self.x_turn = not self.x_turn
            self.player_turn = not self.player_turn
            return True #ok potez odigran
        except ValueError as e:
            print(f"Nevazeci potez: {e}")
            return False #los potez

    def figure_in_stack(self, x, y, piece_color):
        for idx in range(len(self.board[x, y])):
            if self.board[x, y][idx] == piece_color:
                return True
        return False

    def generate_moves(self):
        moves_set = set()
        piece_color = BytePiece.Black if self.x_turn else BytePiece.White
        for i in range(self.width):
            for j in range(self.width):
                if (i + j) % 2 == 0 and self.board[i, j] and self.figure_in_stack(i, j, piece_color): # Trazimo poteze za svako polje koje ima stek
                    current_position = (i, j)
                    if self.board_moved[i, j]:
                        current_position = (i, j)
                        near_pos = self.check_near(current_position)  # Gleda prvo da li ima susede
                        if near_pos:
                            moves_set.update(near_pos)#(convert_format(near_pos))
                            continue
                    else:
                        quick_moves = self.quick_check(current_position)  # Koristi se za polja koja su ista kao na pocetku
                        if quick_moves:
                            moves_set.update(quick_moves)
                            continue
                    if not self.board[i, j][0] == piece_color:  # ako donja figura nije nase boje preskoci
                        continue
                    closest_positions = []  # Ovde cuvamo sve najblize figure
                    offset = 2  # Pocetna razdaljina koju gledamo
                    position_found = False
                    while not position_found:  # Vrti se dok ne nademo barem jednu poziciju
                        for x in range(-offset, offset+1, 2):  # Koristimo offset da pogledamo sva crna polja oko figure
                            for y in range(-offset, offset+1, 2):
                                if 0 <= i + x < self.width and 0 <= j + y < self.width:
                                    if self.board[i + x, j + y] and not (x == 0 and y == 0):
                                        closest_positions.append((i + x, j + y))
                                        position_found = True
                        offset += 1
                        if offset>self.width-1:
                            break
                    for pos in closest_positions:  # Saljemo najblize figure da bi nam naslo moguce poteze
                        valid_moves = self.get_valid_moves(current_position, pos)
                        moves_set.update(valid_moves)#(convert_format(valid_moves))  # posto su potezi u pogresnom formatu, prvo promeni format pa onda doda
        sorted_moves = (list(moves_set))
        ##sorted_moves = sorted(list(moves_set), key=lambda move: (move[0][0], move[0][1]))
        ##print(sorted_moves)
        return sorted_moves

    def get_valid_moves(self, start, end):
        valid_moves_set = set()
        dx = 1 if end[0] > start[0] else -1 #dx i dy su offset
        dy = 1 if end[1] > start[1] else -1

        x, y = start[0] + dx, start[1] + dy  # Uvek postoji barem jedan validan potez
        if 0 <= x < self.width and 0 <= y < self.width:
            valid_moves_set.add((start, (x, y), 0))
        if abs(end[0] - start[0]) != abs(end[1] - start[1]): # Ako end nije dijagonalan u odnosu na start, onda ima dva validna poteza
            dx2, dy2 = dx, dy  # namestamo offset za drugi validan potez
            if end[1] == start[1] or end[0] == start[0]:  # ako je isti red ili kolona
                if end[1] == start[1]:
                    dy2 *= -1
                elif end[0] == start[0]:
                    dx2 *= -1
            else:  # treci slucaj, ni red ni kolona nisu iste
                if abs(end[0] - start[0]) > abs(end[1] - start[1]):  # ako je dalje po redu nego po koloni
                    dy2 *= -1
                elif abs(end[0] - start[0]) < abs(end[1] - start[1]):  # ako je dalje po koloni nego po redu
                    dx2 *= -1
            x2, y2 = start[0] + dx2, start[1] + dy2
            if 0 <= x2 < self.width and 0 <= y2 < self.width:
                valid_moves_set.add((start, (x2, y2), 0))
        return valid_moves_set

    def check_near(self, start):
        x, y = start
        valid_moves_set = set()
        diagonal = [(x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)]
        piece_color = BytePiece.Black if self.x_turn else BytePiece.White
        for dx, dy in diagonal:
            if 0 <= dx < self.width and 0 <= dy < self.width:
                if self.board[dx, dy]:
                    for idx in range(len(self.board[x, y])):
                        if self.board[x, y][idx] != piece_color:
                            continue
                        valid, substack, color = can_put_stack(self.board[x, y], idx, self.board[dx, dy])
                        if valid:
                            #print(start, (dx, dy), idx)
                            valid_moves_set.add((start, (dx, dy), idx))
        return valid_moves_set

    def quick_check(self, start):
        x, y = start
        valid_moves_set = set()
        diagonal = [(x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)]
        for dx, dy in diagonal:
            if 0 <= dx < self.width and 0 <= dy < self.width:
                if self.board[dx, dy]:
                    valid_moves_set.add((start, (dx, dy), 0))
        return valid_moves_set

    def print_board(self):
        player_color = "O"
        if self.x_turn:
            player_color = "X"
        player = "AI"
        if self.player_turn:
            player = "Igrac"

        turn = "X" if self.x_turn else "O"
        print(f"{player}-ev potez ({turn})   trenutni rezultat: X: {self.x_score}, O: {self.o_score}", end="\n\n")
        s = "  "
        for x in range(1, self.width + 1):
            s += " %d   " % x if x < 10 else " %d  " % x
        print(s)
        for r in range(0, self.width):  # red tabele
            for l in range(0, 3):  # red 3x3 matrice (1 celije tabele)
                s = (chr(ord('A') + r) + " ") if (l == 1) else "  "
                for c in range(0, self.width):  # kolona tabele
                    for k in range(0, 3):  # kolona 3x3 matrice
                        idx = 8 - (l * 3 + (2 - k))  # indeks u celiji (listi), negiran da bi bili u donji levi ugao
                        v, = self.board[r, c][idx:idx + 1] or ["." if ((c + r) % 2 == 0) else "_"]  # uzmi sa idx or default
                        s += v
                    s += "  "
                print(s)
            print()


if __name__ == '__main__':
    pass
