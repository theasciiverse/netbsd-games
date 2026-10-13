# canfield; its score lister cfscores reads every user's record on a
# shared machine and is not shipped
cd canfield/canfield
# centred in the terminal by compat/centre.h and centre.c
C=$(dirname "$COMPAT")
$CC $CFLAGS -include "$C/centre.h" canfield.c "$COMPAT" "$C/centre.c" $LDFLAGS \
  $LIBS -o "$OUT/canfield"
echo "built canfield"
