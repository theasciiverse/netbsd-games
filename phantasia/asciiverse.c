/*
 * Asciiverse: where phantasia keeps its files when installed without root.
 *
 * NetBSD installs phantasia setgid games, with its files shared by every
 * player of the machine in /var/games/phantasia, made at build time by
 * setup.c. Here they are the player's own: bsdgames/phantasia under
 * $XDG_DATA_HOME (else ~/.local/share), made on the first run with the
 * empty files setup.c makes, and the monster database it builds from
 * monsters.asc, which is read from the folder the game was started in,
 * where av installs it beside the binary. "Care to give it another try?"
 * starts the game again from the path it was started by.
 *
 * This file is in the public domain.
 */

#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "phantdefs.h"
#include "phantstruct.h"

static char playdir[1024];
static char startdir[1024];
static char gameprog[PATH_MAX];

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

/* name in the player's phantasia folder */
const char *
av_path(const char *name)
{
	static char path[4][sizeof playdir + 32];
	static int next;
	char *p = path[next];

	next = (next + 1) % 4;
	snprintf(p, sizeof path[0], "%s/%s", playdir, name);
	return p;
}

/* the program to start for another try */
const char *
av_gameprog(void)
{
	return gameprog;
}

/* the binary monster database from monsters.asc, as setup.c makes it */
static void
mkmonsters(void)
{
	char asc[sizeof startdir + 32], line[SZ_DATABUF];
	struct monster m;
	FILE *in, *out;

	snprintf(asc, sizeof asc, "%s/monsters.asc", startdir);
	if ((in = fopen(asc, "r")) == NULL &&
	    (in = fopen("monsters.asc", "r")) == NULL) {
		fprintf(stderr, "phantasia: cannot read monsters.asc in %s\n",
		    startdir);
		exit(1);
	}
	if ((out = fopen(av_path("monsters"), "w")) == NULL) {
		perror(av_path("monsters"));
		exit(1);
	}
	memset(&m, 0, sizeof m);
	while (fgets(line, sizeof line, in) != NULL) {
		sscanf(&line[24], "%lf%lf%lf%lf%lf%d%d%lf",
		    &m.m_strength, &m.m_brains, &m.m_speed, &m.m_energy,
		    &m.m_experience, &m.m_treasuretype, &m.m_type,
		    &m.m_flock);
		line[24] = '\0';
		strcpy(m.m_name, line);
		fwrite(&m, sizeof m, 1, out);
	}
	fclose(in);
	if (fclose(out) != 0) {
		perror(av_path("monsters"));
		exit(1);
	}
}

/* find the folders and make the player's files when they are not there */
void
av_init(const char *argv0)
{
	static const char *const files[] = {
		"characs", "mess", "lastdead", "motd", "gold", "void",
		"scoreboard", NULL
	};
	const char *const *f;
	const char *base, *path, *p;
	struct stat sb;
	int fd;

	if (getcwd(startdir, sizeof startdir) == NULL)
		strcpy(startdir, ".");

	/* the game's own path: as given, else found in $PATH */
	gameprog[0] = '\0';
	if (strchr(argv0, '/') != NULL) {
		if (realpath(argv0, gameprog) == NULL)
			snprintf(gameprog, sizeof gameprog, "%s", argv0);
	} else if ((path = getenv("PATH")) != NULL) {
		while (*path != '\0' && gameprog[0] == '\0') {
			char try[PATH_MAX];
			size_t n = strcspn(path, ":");

			snprintf(try, sizeof try, "%.*s/%s", (int) n, path, argv0);
			if (access(try, X_OK) == 0)
				snprintf(gameprog, sizeof gameprog, "%s", try);
			path += n;
			if (*path == ':')
				path++;
		}
	}
	if (gameprog[0] == '\0')
		snprintf(gameprog, sizeof gameprog, "%s", argv0);

	if ((base = getenv("XDG_DATA_HOME")) != NULL && *base != '\0')
		snprintf(playdir, sizeof playdir, "%s/bsdgames/phantasia", base);
	else if ((base = getenv("HOME")) != NULL && *base != '\0')
		snprintf(playdir, sizeof playdir,
		    "%s/.local/share/bsdgames/phantasia", base);
	else
		snprintf(playdir, sizeof playdir, "%s", startdir);
	mkpath(playdir);

	for (f = files; *f != NULL; f++) {
		p = av_path(*f);
		if ((fd = open(p, O_WRONLY | O_CREAT, 0600)) >= 0)
			(void) close(fd);
	}
	p = av_path("monsters");
	if (stat(p, &sb) != 0 || sb.st_size == 0)
		mkmonsters();
}
