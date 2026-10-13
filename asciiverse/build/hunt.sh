# hunt (the client) and huntd (the server it starts), as NetBSD builds
# them: game options from hunt/Makefile.inc, Internet sockets, and
# hunt/asciiverse-compat.h for what Linux and macOS lack
cd hunt
P="-DRANDOM -DREFLECT -DMONITOR -DOOZE -DFLY -DVOLCANO -DBOOTS -DOTTO -DINTERNET"
I="-Iinclude -include asciiverse-compat.h"
# the client is centred in the terminal by compat/centre.h and centre.c
C=$(dirname "$COMPAT")
$CC $CFLAGS $P $I -include "$C/centre.h" hunt/connect.c hunt/hunt.c \
  hunt/otto.c hunt/playit.c hunt/server.c "$COMPAT" "$C/centre.c" $LDFLAGS \
  $LIBS -o "$OUT/hunt"
$CC $CFLAGS $P $I huntd/answer.c huntd/draw.c huntd/driver.c \
  huntd/execute.c huntd/expl.c huntd/extern.c huntd/makemaze.c \
  huntd/shots.c huntd/support.c huntd/terminal.c "$COMPAT" $LDFLAGS \
  -o "$OUT/huntd"
echo "built hunt, huntd"
