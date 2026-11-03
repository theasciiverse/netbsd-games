# hack: makedefs generates hack.onames.h from def.objects.h first; it runs
# during the build, so it is built for the build machine (HOST_CC, else
# CC). The objects and the generated header go to out/build-hack. hack
# draws with terminfo, which Debian and Ubuntu keep in a separate libtinfo.
cd hack
B="$OUT/build-hack"
rm -rf "$B" && mkdir -p "$B"
HFLAGS="$CFLAGS -include asciiverse.h -I. -I$B -idirafter asciiverse-include"
${HOST_CC:-$CC} $HFLAGS makedefs.c "$COMPAT" -o "$B/makedefs"
"$B/makedefs" def.objects.h > "$B/hack.onames.h"
for f in $(sed -n '/^SRCS/,/rnd\.c/p' Makefile | tr -d '\\' | sed 's/SRCS+=//') asciiverse.c; do
	$CC $HFLAGS -c "$f" -o "$B/${f%.c}.o"
done
$CC "$B"/*.o "$COMPAT" "$(dirname "$COMPAT")/tiparm.c" $HFLAGS $LDFLAGS $LIBS -o "$OUT/hack" 2>/dev/null ||
	$CC "$B"/*.o "$COMPAT" "$(dirname "$COMPAT")/tiparm.c" $HFLAGS $LDFLAGS $LIBS -ltinfo -o "$OUT/hack"
echo "built hack"
