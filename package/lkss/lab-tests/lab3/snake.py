#!/bin/python3

import random
import sys
import time
import tty
import termios
import select

UP = 0x0
DOWN = 0x1
LEFT = 0x2
RIGHT = 0x3
NONE = 0x4

WIDTH, HEIGHT = 40, 20

def move_cursor(x, y):
    print(f"\033[{y+1};{x+1}H", end='')  # ANSI uses 1-based indexing

def hide_cursor():
    print("\033[?25l", end='')

def show_cursor():
    print("\033[?25h", end='')

def get_key(fd):
    return int.from_bytes(fd.read(4), byteorder="little")

def draw_border():
    # Draw top and bottom border
    print("\033[1;1H" + '+' + '-'*WIDTH + '+')
    for y in range(HEIGHT):
        print(f"\033[{y+2};1H|{' '*WIDTH}|")
    print(f"\033[{HEIGHT+2};1H+" + '-'*WIDTH + '+')

def main():
    snake_dev = open("/dev/snake", "rb")

    snake = [[WIDTH//4, HEIGHT//2], [WIDTH//4-1, HEIGHT//2], [WIDTH//4-2, HEIGHT//2]]
    food = [random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)]

    direction = 'RIGHT'
    directions = {UP:'UP', DOWN:'DOWN', LEFT:'LEFT', RIGHT:'RIGHT'}
    reverse = {'UP':'DOWN', 'DOWN':'UP', 'LEFT':'RIGHT', 'RIGHT':'LEFT'}

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    hide_cursor()
    print("\033[2J")  # Clear screen once at start
    draw_border()

    # Draw initial snake and food
    for x,y in snake:
        move_cursor(x, y+1)
        print('#', end='')
    move_cursor(food[0], food[1]+1)
    print('O', end='')

    try:
        while True:
            key = get_key(snake_dev)
            if key in directions:
                new_direction = directions[key]
                if reverse[new_direction] != direction:
                    direction = new_direction

            head = snake[0].copy()
            if direction == 'UP':
                head[1] -= 1
            elif direction == 'DOWN':
                head[1] += 1
            elif direction == 'LEFT':
                head[0] -= 1
            elif direction == 'RIGHT':
                head[0] += 1

            # Check collisions with walls (border) or self
            if (head[0] < 0 or head[0] >= WIDTH or
                head[1] < 0 or head[1] >= HEIGHT or
                head in snake):
                move_cursor(0, HEIGHT + 3)
                print("\nGame Over! Press Ctrl-C to exit.")
                break

            snake.insert(0, head)
            move_cursor(head[0], head[1]+1)
            print('#', end='')

            if head == food:
                while True:
                    food = [random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)]
                    if food not in snake:
                        break
                move_cursor(food[0], food[1]+1)
                print('O', end='')
            else:
                tail = snake.pop()
                move_cursor(tail[0], tail[1]+1)
                print(' ', end='')

            # Flush output immediately
            sys.stdout.flush()
            time.sleep(0.2)

    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == '__main__':
    main()

