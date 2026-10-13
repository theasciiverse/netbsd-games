/*
 * Asciiverse: NetBSD libc functions the games use that Linux (glibc and
 * musl), macOS or MinGW lack.
 */
#include <errno.h>
#include <stdint.h>
#include <string.h>
#include "compat.h"

/* reallocarr(3): resize the array *ptrp to n elements of size each */
int
reallocarr(void *ptrp, size_t n, size_t size)
{
	void *p;

	if (size != 0 && n > SIZE_MAX / size)
		return errno = EOVERFLOW;
	memcpy(&p, ptrp, sizeof p);
	if (n == 0 || size == 0) {
		free(p);
		p = NULL;
	} else if ((p = realloc(p, n * size)) == NULL)
		return errno;
	memcpy(ptrp, &p, sizeof p);
	return 0;
}

#if !defined(__APPLE__) && !defined(__FreeBSD__)
static const char *progname = "";

const char *
getprogname(void)
{
	return progname;
}

void
setprogname(const char *name)
{
	const char *slash = strrchr(name, '/');

	progname = slash != NULL ? slash + 1 : name;
}
#endif
