/*	$NetBSD: config.c,v 1.6 2008/01/28 05:38:53 dholland Exp $	 */

/*
 * config.c --	This defines the installation dependent variables.
 *              Some strings are modified later.  ANSI C would
 *              allow compile time string concatenation, we must
 *              do runtime concatenation, in main.
 *
 *		Larn is copyrighted 1986 by Noah Morgan.
 */
#include <sys/cdefs.h>
#ifndef lint
__RCSID("$NetBSD: config.c,v 1.6 2008/01/28 05:38:53 dholland Exp $");
#endif /* not lint */

#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "header.h"
#include "extern.h"
#include "pathnames.h"

/*
 * All these strings will be appended to in main() to be complete filenames
 */

/* the game save filename */
char  savefilename[1024];

/* the logging file */
char  logfile[1024] = _PATH_LOG;

/* the help text file */
char  helpfile[1024] = _PATH_HELP;

/* the score file */
char  scorefile[1024] = _PATH_SCORE;

/* the maze data file */
char  larnlevels[1024] = _PATH_LEVELS;

/* the .larnopts filename */
char  optsfile[1024] = "/.larnopts";

/* the player id datafile name */
char  playerids[1024] = _PATH_PLAYERIDS;

char  diagfile[1024] = "Diagfile";		/* the diagnostic filename */
char  ckpfile[1024] = "Larn12.0.ckp";	/* the checkpoint filename */
const char *password = "pvnert(x)";	/* the wizards password <=32 */
char  psname[PSNAMESIZE] = "larn";	/* the process name */

#define	WIZID	1
int   wisid = 0;	/* the user id of the only person who can be wizard */

/*
 * Asciiverse: the files Larn writes (scoreboard, log, player ids, saved
 * and checkpointed games, diagnostics) go in the player's data folder,
 * $XDG_DATA_HOME or else ~/.local/share, under bsdgames/larn/, made as
 * needed.  The help text and the mazes are read from the current
 * directory, where av starts the game, when they are there, and from
 * their installed place otherwise.
 */
void
setpaths(void)
{
	char		dir[900];
	const char     *base;
	char	       *p;

	if ((base = getenv("XDG_DATA_HOME")) != NULL && *base != '\0')
		snprintf(dir, sizeof(dir), "%s/bsdgames/larn", base);
	else if ((base = getenv("HOME")) != NULL && *base != '\0')
		snprintf(dir, sizeof(dir), "%s/.local/share/bsdgames/larn", base);
	else
		goto readonly;
	for (p = dir + 1; *p != '\0'; p++)
		if (*p == '/') {
			*p = '\0';
			mkdir(dir, 0755);
			*p = '/';
		}
	mkdir(dir, 0755);
	snprintf(logfile, sizeof(logfile), "%s/%s", dir, _NAME_LOG);
	snprintf(scorefile, sizeof(scorefile), "%s/%s", dir, _NAME_SCORE);
	snprintf(playerids, sizeof(playerids), "%s/%s", dir, _NAME_PLAYERIDS);
	snprintf(savefilename, sizeof(savefilename), "%s/%s", dir, _NAME_SAVE);
	snprintf(ckpfile, sizeof(ckpfile), "%s/%s", dir, _NAME_CKP);
	snprintf(diagfile, sizeof(diagfile), "%s/%s", dir, _NAME_DIAG);
readonly:
	if (access(_NAME_HELP, R_OK) == 0)
		strlcpy(helpfile, _NAME_HELP, sizeof(helpfile));
	if (access(_NAME_LEVELS, R_OK) == 0)
		strlcpy(larnlevels, _NAME_LEVELS, sizeof(larnlevels));
}
