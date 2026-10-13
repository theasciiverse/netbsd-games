#!/bin/sh
# Builds every game into out/: each asciiverse/build/<game>.sh compiles one
# game with the compiler, flags and curses library from the environment,
# so one script serves every target (see .github/workflows/release.yml):
#
#   asciiverse/build.sh                                   # Debian, Ubuntu
#   LIBS=-lncursesw LDFLAGS=-static asciiverse/build.sh   # Alpine, static
#   LIBS=-lncurses asciiverse/build.sh                    # macOS
#
# compat/ supplies what the games expect from NetBSD's own headers and libc.
set -eu
cd "$(dirname "$0")/.."
export CC="${CC:-cc}"
export CFLAGS="${CFLAGS:--O2} -std=gnu99 -include $PWD/compat/compat.h -I$PWD/compat -idirafter $PWD/compat/fallback -Wno-unused-result"
export LDFLAGS="${LDFLAGS:-}"
export LIBS="${LIBS:--lncursesw}"
export OUT="$PWD/out"
export COMPAT="$PWD/compat/compat.c"
mkdir -p out
for s in asciiverse/build/*.sh; do
  sh -eu "$s"
done
