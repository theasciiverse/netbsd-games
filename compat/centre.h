/*
 * Asciiverse: show a curses game centred in the terminal.
 *
 * Taken from New BSD Games' src/centre.h (Asciiverse, CC0), split in two
 * so games of several source files share one state: this header, included
 * before every source file of a game with -include, turns initscr(),
 * refresh() and getch() into the functions in centre.c.
 *
 * The games draw on stdscr at fixed positions from the top left corner.
 * stdscr is swapped for a pad as soon as curses starts, so every drawing
 * call works unchanged; refresh() then shows the part of the pad the game
 * has drawn on, centred in the terminal. The area grows at once while the
 * game keeps drawing over it, shrinks only once the drawing has stayed
 * smaller for two seconds, and starts over when the game moves to another
 * screen. A resized terminal re-centres the picture, also for games that
 * read their keys without getch(); a terminal too small for the game shows
 * its top left part, as before.
 */
#ifndef ASCIIVERSE_CENTRE_H
#define ASCIIVERSE_CENTRE_H

#include <curses.h>

WINDOW *nb_initscr(void);
int nb_refresh(void);
int nb_getch(void);
/*
 * A game with a field of fixed size calls this after initscr(): the whole
 * field is centred, however much of it is drawn yet (a dungeon that is
 * explored room by room does not move about).
 */
void nb_fixed(int lines, int cols);

#undef initscr
#define initscr() nb_initscr()
#undef refresh
#define refresh() nb_refresh()
#undef getch
#define getch() nb_getch()

#endif
