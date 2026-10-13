/*
 * Asciiverse: where hack keeps its files when installed without root.
 *
 * The playground, where hack writes its record, saved games, bones and
 * the level files of a game in progress, is the player's own folder,
 * bsdgames/hack under $XDG_DATA_HOME (else ~/.local/share), made on the
 * first run with its save folder and the empty record and perm files hack
 * expects there. The read-only files (help, hh, data, rumors, news) are
 * looked for first in the folder the game was started from, where av
 * installs them beside the binary.
 *
 * This file is in the public domain.
 */

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static char datadir[1024];

/* remember the folder the game was started from, before hack leaves it */
void
av_datadir_init(void)
{
	if (getcwd(datadir, sizeof datadir) == NULL)
		datadir[0] = '\0';
}

/* name in the start folder when it is there, else name as it was */
const char *
av_datafile(const char *name)
{
	static char path[4][sizeof datadir + 64];
	static int next;
	char *p;

	if (datadir[0] == '\0')
		return name;
	p = path[next];
	next = (next + 1) % 4;
	snprintf(p, sizeof path[0], "%s/%s", datadir, name);
	return access(p, R_OK) == 0 ? p : name;
}

static void
mkpath(char *path)
{
	char *p;

	for (p = path + 1; *p != '\0'; p++)
		if (*p == '/') {
			*p = '\0';
			(void) mkdir(path, 0755);
			*p = '/';
		}
	(void) mkdir(path, 0755);
}

static void
touch(const char *dir, const char *name)
{
	char path[sizeof datadir + 64];
	int fd;

	snprintf(path, sizeof path, "%s/%s", dir, name);
	if ((fd = open(path, O_WRONLY | O_CREAT, 0644)) >= 0)
		(void) close(fd);
}

/* the player's playground, made when it is not there yet; NULL without
 * $XDG_DATA_HOME or $HOME */
char *
av_playground(void)
{
	static char dir[sizeof datadir];
	char save[sizeof datadir + 8];
	const char *base;

	if ((base = getenv("XDG_DATA_HOME")) != NULL && *base != '\0')
		snprintf(dir, sizeof dir, "%s/bsdgames/hack", base);
	else if ((base = getenv("HOME")) != NULL && *base != '\0')
		snprintf(dir, sizeof dir, "%s/.local/share/bsdgames/hack", base);
	else
		return NULL;
	snprintf(save, sizeof save, "%s/save", dir);
	mkpath(save);
	touch(dir, "record");
	touch(dir, "perm");
	return dir;
}
