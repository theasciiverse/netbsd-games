# warp: the game, plus its eight star maps, made from warp/smp.N by the
# helper sm, built for and run on the build machine (HOST_CC). warp drives
# the terminal through termcap only and defines its own LINES and
# typeahead, so it links the termcap library alone, not curses: tinfo,
# or termcap on macOS (WARP_TERMLIB overrides)
cd warp
HOST_CC="${HOST_CC:-cc}"
$HOST_CC -O2 -w -o "$OUT/warp-sm" sm.c
mkdir -p "$OUT/warp-data"
for n in 0 1 2 3 4 5 6 7; do
  "$OUT/warp-sm" < "smp.$n" > "$OUT/warp-data/smap.$n"
done
rm -f "$OUT/warp-sm"
cp warp.doc warp.news README "$OUT/warp-data/"
if [ "$(uname)" = Darwin ]; then
  WARP_TERMLIB="${WARP_TERMLIB:--ltermcap}"
else
  WARP_TERMLIB="${WARP_TERMLIB:--ltinfo}"
fi
$CC $CFLAGS -include asciiverse.h -DHAVETERMLIB \
  bang.c init.c intrp.c move.c object.c play.c score.c sig.c term.c \
  them.c us.c util.c version.c warp.c weapon.c "$COMPAT" \
  $LDFLAGS $WARP_TERMLIB -lm -o "$OUT/warp"
echo "built warp"
