/*
 * Asciiverse: what the NetBSD games expect from NetBSD's headers, for
 * Linux (glibc and musl), macOS and MinGW. Included before every source
 * file with -include.
 */
#ifndef ASCIIVERSE_COMPAT_H
#define ASCIIVERSE_COMPAT_H

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#ifndef _DEFAULT_SOURCE
#define _DEFAULT_SOURCE
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
/*
 * musl's struct stat has a field named __unused: read the header before
 * __unused becomes a macro below (its include guard keeps it from being
 * read again).
 */
#include <sys/stat.h>

#define __RCSID(x)
#define __COPYRIGHT(x)
#define __KERNEL_RCSID(n, x)
#define __SCCSID(x)
#ifndef __dead
#define __dead __attribute__((__noreturn__))
#endif
#ifndef __printflike
#define __printflike(f, a) __attribute__((__format__(__printf__, f, a)))
#endif
#ifndef __unused
#define __unused __attribute__((__unused__))
#endif
#ifndef __arraycount
#define __arraycount(a) (sizeof(a) / sizeof((a)[0]))
#endif
#ifndef __UNCONST
#define __UNCONST(a) ((void *)(unsigned long)(const void *)(a))
#endif
#ifndef __CTASSERT
#define __CTASSERT(x) _Static_assert(x, #x)
#endif
#ifndef __unreachable
#define __unreachable() __builtin_unreachable()
#endif

/* NetBSD libc functions other systems lack (compat/compat.c) */
int reallocarr(void *, size_t, size_t);
#if !defined(__APPLE__) && !defined(__FreeBSD__)
const char *getprogname(void);
void setprogname(const char *);
#endif

#endif
