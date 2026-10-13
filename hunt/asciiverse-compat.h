/*
 * Asciiverse: what hunt and huntd need on Linux and macOS beyond
 * compat/compat.h.
 */

#include <sys/types.h>		/* u_short, u_int on musl */
#include <poll.h>
#include <stdint.h>
#include <time.h>

#ifndef INFTIM
#define INFTIM	(-1)	/* poll(2): wait for ever */
#endif
