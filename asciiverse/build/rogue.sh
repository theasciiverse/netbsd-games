# rogue: the 1980s original, with UNIX for its machine-dependent code
cd rogue
# centred in the terminal by compat/centre.h and centre.c
C=$(dirname "$COMPAT")
$CC $CFLAGS -DUNIX -include "$C/centre.h" *.c "$COMPAT" "$C/centre.c" $LDFLAGS \
  $LIBS -o "$OUT/rogue"
echo "built rogue"
