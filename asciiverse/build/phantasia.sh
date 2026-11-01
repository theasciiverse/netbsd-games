# phantasia: the game without setup.c, whose work (the empty files and
# the monster database from monsters.asc) asciiverse.c does on the first
# run in the player's data folder; maths library and curses, terminfo
# where it is separate
cd phantasia
# centred in the terminal by compat/centre.h and centre.c; asciiverse-compat.h
# for what NetBSD's headers bring along
C=$(dirname "$COMPAT")
set -- fight.c gamesupport.c interplayer.c io.c main.c misc.c phantglobs.c \
  asciiverse.c "$COMPAT" "$C/centre.c"
$CC $CFLAGS -include "$C/centre.h" -include asciiverse-compat.h "$@" $LDFLAGS $LIBS -lm -o "$OUT/phantasia" 2>/dev/null ||
	$CC $CFLAGS -include "$C/centre.h" -include asciiverse-compat.h "$@" $LDFLAGS $LIBS -ltinfo -lm -o "$OUT/phantasia"
echo "built phantasia"
