/*
 * Asciiverse: what phantasia gets from NetBSD's headers, included before
 * every source file after compat/compat.h and compat/centre.h.
 *
 * phantstruct.h defines bool as char for its file records, and the
 * sources then #undef it and include <curses.h> for curses' bool. Here
 * curses is in already (compat/centre.h), so that include does nothing;
 * a typedef of bool survives the #undef and stands in for curses' one.
 * main.c uses time() and localtime(), which NetBSD's headers bring along.
 *
 * This file is in the public domain.
 */
#include <time.h>
#include <curses.h>
#undef bool
typedef _Bool bool;
