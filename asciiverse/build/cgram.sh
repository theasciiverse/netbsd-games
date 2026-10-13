# cgram: one file and curses
cd cgram
# centred in the terminal by compat/centre.h and centre.c
C=$(dirname "$COMPAT")
$CC $CFLAGS -include "$C/centre.h" cgram.c "$COMPAT" "$C/centre.c" $LDFLAGS $LIBS \
  -o "$OUT/cgram"
echo "built cgram"
