# cgram: one file and curses
cd cgram
$CC $CFLAGS cgram.c "$COMPAT" $LDFLAGS $LIBS -o "$OUT/cgram"
echo "built cgram"
