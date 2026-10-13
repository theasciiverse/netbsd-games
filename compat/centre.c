/*
 * Asciiverse: the centring behind compat/centre.h, from New BSD Games'
 * src/centre.h (CC0), which has the full description. Added here: a game
 * that reads its keys with getchar() or read() never lets curses see
 * KEY_RESIZE, so every refresh asks the terminal for its size.
 */
#include <sys/ioctl.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include "centre.h"

/* the build may have read centre.h before this file: the real calls here */
#undef initscr
#undef refresh
#undef getch

#define NB_PAD_LINES 100
#define NB_PAD_COLS 300

static WINDOW *nb_pad;		/* where the game draws */
static chtype *nb_row;		/* one row of it, for measuring */
/* the current screen's area, inclusive */
static int nb_top, nb_left, nb_bottom = -1, nb_right = -1;
/* where that is shown, for which terminal size */
static int nb_oy, nb_ox, nb_lines, nb_cols;
/* what has been drawn since it last filled that area, and since when */
static int nb_st, nb_sl, nb_sb = -1, nb_sr;
static time_t nb_small_since;
/* a field of fixed size, set by nb_fixed(); 0 when the drawing decides */
static int nb_fix_lines, nb_fix_cols;

void
nb_fixed(int lines, int cols)
{
	nb_fix_lines = lines;
	nb_fix_cols = cols;
}

WINDOW *
nb_initscr(void)
{
	if (nb_pad == NULL) {
		if (initscr() == NULL)
			return NULL;
		nb_pad = newpad(LINES > NB_PAD_LINES ? LINES : NB_PAD_LINES,
		    COLS > NB_PAD_COLS ? COLS : NB_PAD_COLS);
		nb_row = nb_pad != NULL ?
		    malloc((getmaxx(nb_pad) + 1) * sizeof(chtype)) : NULL;
		if (nb_pad != NULL && nb_row != NULL) {
			/*
			 * no scrolling of screen regions: the picture moves
			 * by rewriting, as the games do anyway
			 */
			idlok(nb_pad, FALSE);
			idlok(curscr, FALSE);
			/* keypad and the like are set on stdscr afterwards */
			stdscr = nb_pad;
		} else if (nb_pad != NULL) {
			/* no memory: draw at the top left as before */
			delwin(nb_pad);
			nb_pad = NULL;
		}
	}
	return stdscr;
}

/* the area of every cell that is not a plain blank; false when none */
static bool
nb_measure(int *top, int *left, int *bottom, int *right)
{
	int h = getmaxy(nb_pad), w = getmaxx(nb_pad);

	*top = h;
	*left = w;
	*bottom = -1;
	*right = -1;
	for (int y = 0; y < h; ++y) {
		int n = mvwinchnstr(nb_pad, y, 0, nb_row, w);
		for (int x = 0; x < n; ++x) {
			if (nb_row[x] != (chtype)' ') {
				if (y < *top)
					*top = y;
				if (y > *bottom)
					*bottom = y;
				if (x < *left)
					*left = x;
				if (x > *right)
					*right = x;
			}
		}
	}
	return *bottom >= 0;
}

/* keep the current screen's area, grown or shrunk, or start a new one */
static void
nb_follow(int top, int left, int bottom, int right)
{
	if (nb_bottom >= 0) {
		int it = top > nb_top ? top : nb_top;
		int ib = bottom < nb_bottom ? bottom : nb_bottom;
		int il = left > nb_left ? left : nb_left;
		int ir = right < nb_right ? right : nb_right;
		long both = (it <= ib && il <= ir) ?
		    (long)(ib - it + 1) * (ir - il + 1) : 0;
		long drawn = (long)(bottom - top + 1) * (right - left + 1);
		long area = (long)(nb_bottom - nb_top + 1) *
		    (nb_right - nb_left + 1);

		if (2 * both >= drawn + area - both) {
			/* overlapping by half or more: the same screen */
			bool inside = top >= nb_top && left >= nb_left &&
			    bottom <= nb_bottom && right <= nb_right;
			if (!inside || (top == nb_top && left == nb_left &&
			    bottom == nb_bottom && right == nb_right)) {
				if (top < nb_top)
					nb_top = top;
				if (left < nb_left)
					nb_left = left;
				if (bottom > nb_bottom)
					nb_bottom = bottom;
				if (right > nb_right)
					nb_right = right;
				nb_sb = -1;
				return;
			}
			/* smaller than the area: shrink to it once that lasted */
			if (nb_sb < 0) {
				nb_st = top;
				nb_sl = left;
				nb_sb = bottom;
				nb_sr = right;
				nb_small_since = time(NULL);
			} else {
				if (top < nb_st)
					nb_st = top;
				if (left < nb_sl)
					nb_sl = left;
				if (bottom > nb_sb)
					nb_sb = bottom;
				if (right > nb_sr)
					nb_sr = right;
			}
			if (time(NULL) - nb_small_since >= 2) {
				nb_top = nb_st;
				nb_left = nb_sl;
				nb_bottom = nb_sb;
				nb_right = nb_sr;
				nb_sb = -1;
			}
			return;
		}
	}
	nb_top = top;
	nb_left = left;
	nb_bottom = bottom;
	nb_right = right;
	nb_sb = -1;
}

/* follow a resized terminal even when the game never calls getch() */
static void
nb_check_size(void)
{
#ifdef TIOCGWINSZ
	struct winsize ws;

	if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == 0 && ws.ws_row > 0 &&
	    ws.ws_col > 0 && (ws.ws_row != LINES || ws.ws_col != COLS))
		resize_term(ws.ws_row, ws.ws_col);
#endif
	stdscr = nb_pad;
}

int
nb_refresh(void)
{
	int cy, cx, top, left, bottom, right;

	if (nb_pad == NULL)
		return wrefresh(stdscr);
	nb_check_size();
	if (nb_fix_lines > 0) {
		nb_top = nb_left = 0;
		nb_bottom = nb_fix_lines - 1;
		nb_right = nb_fix_cols - 1;
	} else {
		getyx(nb_pad, cy, cx);
		bool drawn = nb_measure(&top, &left, &bottom, &right);
		wmove(nb_pad, cy, cx);
		if (drawn)
			nb_follow(top, left, bottom, right);
	}
	if (nb_bottom < 0) {
		/* nothing drawn yet */
		stdscr = nb_pad;
		return OK;
	}
	int h = nb_bottom - nb_top + 1, w = nb_right - nb_left + 1;
	int oy = LINES > h ? (LINES - h) / 2 : 0;
	int ox = COLS > w ? (COLS - w) / 2 : 0;
	if (oy != nb_oy || ox != nb_ox || LINES != nb_lines ||
	    COLS != nb_cols) {
		/* the picture moved: blank the old place */
		WINDOW *screen = newwin(0, 0, 0, 0);
		if (screen != NULL) {
			wnoutrefresh(screen);
			delwin(screen);
		}
		nb_oy = oy;
		nb_ox = ox;
		nb_lines = LINES;
		nb_cols = COLS;
	}
	int vh = h < LINES ? h : LINES, vw = w < COLS ? w : COLS;
	pnoutrefresh(nb_pad, nb_top, nb_left, oy, ox, oy + vh - 1,
	    ox + vw - 1);
	int r = doupdate();
	/* ncurses points stdscr back at the screen in doupdate */
	stdscr = nb_pad;
	return r;
}

int
nb_getch(void)
{
	int c;

	if (nb_pad == NULL)
		return wgetch(stdscr);
	nb_refresh();	/* wgetch does not refresh a pad by itself */
	while ((c = wgetch(nb_pad)) == KEY_RESIZE) {
		stdscr = nb_pad;
		nb_refresh();
	}
	stdscr = nb_pad;
	return c;
}
