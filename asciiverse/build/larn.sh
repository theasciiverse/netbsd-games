# larn: the 1986 original, version 12.0; it drives the terminal through
# terminfo, which some systems keep in a separate libtinfo
cd larn
set -- -DBSD -DVER=12 -DSUBVER=0 -DNONAP -DUIDSCORE -DTERMIOS
$CC $CFLAGS "$@" *.c "$COMPAT" "$(dirname "$COMPAT")/tiparm.c" $LDFLAGS $LIBS -o "$OUT/larn" 2>/dev/null ||
	$CC $CFLAGS "$@" *.c "$COMPAT" "$(dirname "$COMPAT")/tiparm.c" $LDFLAGS $LIBS -ltinfo -o "$OUT/larn"
echo "built larn"
