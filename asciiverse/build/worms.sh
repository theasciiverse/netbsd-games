# worms: one file and curses, plus terminfo's tigetstr() for -C, which
# Debian and Ubuntu keep in a separate libtinfo; draws over the whole
# terminal, so not centred
cd worms
$CC $CFLAGS worms.c "$COMPAT" $LDFLAGS $LIBS -o "$OUT/worms" 2>/dev/null ||
	$CC $CFLAGS worms.c "$COMPAT" $LDFLAGS $LIBS -ltinfo -o "$OUT/worms"
echo "built worms"
