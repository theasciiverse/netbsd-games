# rain: one file and curses; draws over the whole terminal, so not centred
cd rain
$CC $CFLAGS rain.c "$COMPAT" $LDFLAGS $LIBS -o "$OUT/rain"
echo "built rain"
