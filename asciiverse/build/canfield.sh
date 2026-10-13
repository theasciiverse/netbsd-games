# canfield; its score lister cfscores reads every user's record on a
# shared machine and is not shipped
cd canfield/canfield
$CC $CFLAGS canfield.c "$COMPAT" $LDFLAGS $LIBS -o "$OUT/canfield"
echo "built canfield"
