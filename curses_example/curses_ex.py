#!/usr/bin/python

import curses
import traceback

def inc_r(r):
    r = r + 1
    return r

def main():
    try:
        stdscr = curses.initscr()
        stdscr.clear()
        curses.echo()
        r = 2
        c = 3
        stdscr.addstr(r, c, "Enter your name")
        r = inc_r(r)
        name = stdscr.getstr(r, c, 20)
        r = inc_r(r)
        stdscr.addstr(r, c, "Hello " + name)
        stdscr.refresh()
        #stdscr.clear()
        stdscr.getch()
        stdscr.endwin()
    except:
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        traceback.print_exc()

if __name__ == '__main__':
    main()
