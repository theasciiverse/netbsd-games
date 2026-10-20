/*
 * Asciiverse: what backgammon and teachgammon need to run from wherever
 * av installs them, keep a saved game where an update does not touch it,
 * and follow a resized terminal.
 */

#include <errno.h>
#include <limits.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#ifdef __APPLE__
#include <mach-o/dyld.h>
#endif

#include "back.h"

/*
 * The program called name in the folder this program was started from
 * (backgammon and teachgammon are installed together, anywhere), else the
 * path the original used.
 */
const char *
sibling(const char *name, const char *fallback)
{
	static char path[PATH_MAX];
	char exe[PATH_MAX];
	char *slash;
	ssize_t len = -1;

#if defined(__linux__)
	len = readlink("/proc/self/exe", exe, sizeof(exe) - 1);
#elif defined(__APPLE__)
	{
		uint32_t size = sizeof(exe);
		char *real;

		if (_NSGetExecutablePath(exe, &size) == 0 &&
		    (real = realpath(exe, NULL)) != NULL) {
			strlcpy(exe, real, sizeof(exe));
			free(real);
			len = (ssize_t)strlen(exe);
		}
	}
#endif
	if (len > 0) {
		exe[len] = '\0';
		if ((slash = strrchr(exe, '/')) != NULL) {
			*slash = '\0';
			snprintf(path, sizeof(path), "%s/%s", exe, name);
			if (access(path, X_OK) == 0)
				return path;
		}
	}
	return fallback;
}

/*
 * The full name of a saved game given the name the player typed: a bare
 * name goes in the player's data folder, $XDG_DATA_HOME or else
 * ~/.local/share, under bsdgames/backgammon/, made as needed. A name with a
 * '/' in it is used as it is, and so is a bare name when neither variable
 * is set.
 */
const char *
datafile(const char *name)
{
	static char path[PATH_MAX];
	const char *base;

	if (strchr(name, '/') != NULL)
		return name;
	if ((base = getenv("XDG_DATA_HOME")) != NULL && *base != '\0')
		snprintf(path, sizeof(path), "%s/bsdgames/backgammon", base);
	else if ((base = getenv("HOME")) != NULL && *base != '\0')
		snprintf(path, sizeof(path), "%s/.local/share/bsdgames/backgammon",
		    base);
	else
		return name;
	for (char *q = path + 1; *q != '\0'; q++) {
		if (*q == '/') {
			*q = '\0';
			(void)mkdir(path, 0755);
			*q = '/';
		}
	}
	(void)mkdir(path, 0755);
	strlcat(path, "/", sizeof(path));
	strlcat(path, name, sizeof(path));
	return path;
}

/*
 * A resized terminal: SIGWINCH interrupts the read in readc(), which then
 * centres the board again and redraws it, as Ctrl+L does.
 */
static volatile sig_atomic_t winched;

static void
onwinch(int sig)
{
	(void)sig;
	winched = 1;
}

void
watchresize(void)
{
	struct sigaction sa;

	memset(&sa, 0, sizeof(sa));
	sa.sa_handler = onwinch;
	sigemptyset(&sa.sa_mask);
	/* no SA_RESTART: the read in readc() must return */
	sigaction(SIGWINCH, &sa, NULL);
}

int
resized(void)
{
	if (!winched)
		return 0;
	winched = 0;
	return 1;
}
