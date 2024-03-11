import numpy as np
from state import *
from logic import *


dirs = {
    "dl": Direction.DownLeft,
    "dd": Direction.DownRight,
    "gl": Direction.UpLeft,
    "gd": Direction.UpRight
}

def prompt_move():
    while(True):
        print("Potez: <red slovo> <kolona broj> <indeks figure u steku> <smer: GL|GD|DL|DD>")
        move_str = input("Unesite potez: ")
        tokens = move_str.split(" ")
        if (len(tokens) != 4):
            print("Invalidan potez")
            continue
        row = int(ord(tokens[0].lower()) - ord('a'))
        col = int(tokens[1]) - 1
        idx = int(tokens[2])
        smer = dirs[tokens[3].lower()]
        return (row,col,idx,smer)


if __name__ == "__main__":

    try:
        table_size = -1
        while True:
            table_size = int(input("Velicina table (1 broj): "))
            if table_size != 8 and table_size != 10 and table_size != 16:  # jedini brojevi za koje vazi uslov iz zadatka
                print("Losa velicina table. Validne: 8, 10, 16")
            else: break
        
        player_first = input("Hocete da igrate prvi (kao X)? (d/n): ")
        player_first = player_first.lower() == "d"
        
        byte_board = ByteBoard(table_size, player_first)
        byte_board.print_board()

        mov_num = 1

        ##print("Move: <row letter> <column number> <number of a piece in a stack> <direction: ul|ur|dl|dr>")
        while True:
            if byte_board.player_turn:
                gen_moves = byte_board.generate_moves()
                if not gen_moves:
                    byte_board.change_player()
                    continue
                tokens = prompt_move()
                while byte_board.move(tokens[0], tokens[1], tokens[2], tokens[3])==False:
                    tokens = prompt_move() #nastavi ispitivanje za potez dok se ne unese validan
            else:
                d = 2
                if mov_num > 5 and mov_num and mov_num <= 9:
                    d = 3
                elif mov_num > 9 and mov_num <= 14:
                    d = 4
                elif mov_num > 14:
                    d = 5
                if byte_board.x_score > 0 or byte_board.o_score > 0:
                    d = 8
                h = ai_play(byte_board, d)
                print(f"Heuristika stanja: {h}")
            is_over, winner, score = byte_board.check_if_end()
            if is_over:
                print(f"{winner} je pobedio sa {score} poena.")
                break
            byte_board.print_board()
            mov_num += 1

    except ValueError as e:
        print(f"Error: {e}")
