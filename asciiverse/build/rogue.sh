# rogue: the 1980s original, with UNIX for its machine-dependent code
cd rogue
$CC $CFLAGS -DUNIX *.c "$COMPAT" $LDFLAGS $LIBS -o "$OUT/rogue"
echo "built rogue"
