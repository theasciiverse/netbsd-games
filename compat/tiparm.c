/*
 * Asciiverse: tiparm() for macOS (see compat.h), where the oldest
 * supported libncurses (5.7) lacks it. Elsewhere this file is empty.
 */
#ifdef __APPLE__
#include <stdarg.h>
#include <curses.h>
#include <term.h>

char *
av_tiparm(const char *cap, ...)
{
	va_list ap;
	int a, b;

	va_start(ap, cap);
	a = va_arg(ap, int);
	b = va_arg(ap, int);
	va_end(ap);
	return tparm((char *)cap, (long)a, (long)b);
}
#else
typedef int av_tiparm_unused;
#endif
