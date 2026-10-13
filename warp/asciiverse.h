/*
 * Asciiverse: what warp needs on Linux and macOS beyond compat/compat.h.
 * Included before every source file by asciiverse/build/warp.sh.
 */
#ifndef WARP_ASCIIVERSE_H
#define WARP_ASCIIVERSE_H

#include <signal.h>
#include <time.h>
#include <unistd.h>
#include <termcap.h>	/* tgetent and friends, BC, UP, PC, ospeed */

/* glibc declares its own eaccess(); warp's is a different function */
#define eaccess warp_eaccess

/* warp keeps its own LINES, COLS and typeahead; with a static ncurses
 * (where tinfo is all of ncurses, as on Alpine) curses' ones would clash.
 * term.h also defines TERMIOS, which warp's config.h defines again. */
#include <term.h>
#undef TERMIOS
#define LINES warp_LINES
#define COLS warp_COLS
#define typeahead warp_typeahead

/* musl has no BSD sigblock() or sigsetmask(); the same with sigprocmask() */
#if !defined(__GLIBC__) && !defined(__APPLE__) && !defined(sigmask)
#define sigmask(s) (1 << ((s) - 1))

static inline int
warp_sigmask_call(int how, int mask)
{
    sigset_t set, old;
    int i, r = 0;

    sigemptyset(&set);
    for (i = 1; i < 32; i++)
	if (mask & sigmask(i))
	    sigaddset(&set, i);
    sigprocmask(how, &set, &old);
    for (i = 1; i < 32; i++)
	if (sigismember(&old, i))
	    r |= sigmask(i);
    return r;
}
#define sigblock(m) warp_sigmask_call(SIG_BLOCK, (m))
#define sigsetmask(m) warp_sigmask_call(SIG_SETMASK, (m))
#endif

#endif
