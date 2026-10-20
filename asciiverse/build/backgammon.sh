# backgammon and its rules and tutorial, teachgammon, which start each
# other from the folder they are installed in; both use termcap through
# curses' library (Debian and Ubuntu keep it in libtinfo) and centre
# themselves in fancy.c's own cursor code
cd backgammon
for prog in backgammon teachgammon; do
	$CC $CFLAGS -Icommon_source $prog/*.c common_source/*.c "$COMPAT" \
	  $LDFLAGS $LIBS -o "$OUT/$prog" 2>/dev/null ||
	$CC $CFLAGS -Icommon_source $prog/*.c common_source/*.c "$COMPAT" \
	  $LDFLAGS $LIBS -ltinfo -o "$OUT/$prog"
done
echo "built backgammon, teachgammon"
