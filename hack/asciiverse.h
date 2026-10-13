/*
 * Asciiverse: what hack needs beyond compat/compat.h on Linux and macOS,
 * included before every source file with -include.
 */
#ifndef HACK_ASCIIVERSE_H
#define HACK_ASCIIVERSE_H

#include <termios.h>

/*
 * musl's struct stat has a field named __unused, which compat.h defines
 * as a macro: read <sys/stat.h> once without it, then put it back.
 */
#ifdef __unused
#undef __unused
#include <sys/stat.h>
#define __unused __attribute__((__unused__))
#endif

/* tab expansion: OXTABS on the BSDs and macOS, XTABS (TAB3) on Linux */
#if !defined(OXTABS) && defined(XTABS)
#define OXTABS XTABS
#elif !defined(OXTABS) && defined(TAB3)
#define OXTABS TAB3
#endif

/* the field centred on a bigger terminal (hack.terminfo.c) */
#include <signal.h>
extern volatile sig_atomic_t av_resized;
void av_replace_field(void);
void av_redraw_topl(void);

/* where the game keeps its files, and where it finds its read-only ones */
void av_datadir_init(void);
const char *av_datafile(const char *);
char *av_playground(void);

#endif
