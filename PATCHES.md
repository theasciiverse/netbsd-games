# Changes from upstream

This is the Asciiverse packaging of the BSD games that Mike Sharov's
bsd-games (packaged in `theasciiverse/bsdgames`) dropped: canfield, cgram,
hack, hunt, larn, rogue and warp, from NetBSD's own source tree. The first
commit imports NetBSD's `src/games` folders for them unchanged, at
NetBSD commit `1fc61a5c45cdd2a67b7e1b272c41a67aa200f621` (2026-10-13,
tag `netbsd-1fc61a5`); phantasia came along and is not built. Everything
after it is ours.

In the Asciiverse catalog each game is its own title, credited as part of
BSD Games.

## Shared

- `compat/`: what the games expect from NetBSD's headers and libc
  (`__RCSID`, `__dead`, `__printflike`, `reallocarr`, `getprogname` and
  the like), included before every source file. musl's `struct stat` has
  a field named `__unused`, so `compat.h` reads `<sys/stat.h>` before
  defining that macro, and `compat/fallback/sys/cdefs.h` stands in for
  the `<sys/cdefs.h>` musl does not have.
- `asciiverse/build.sh` runs one script per game in `asciiverse/build/`;
  `asciiverse/package.sh` packs one archive per game from the list in
  `asciiverse/archive/<id>.txt`; `.github/workflows/release.yml` builds
  static Linux in Alpine (x86_64, aarch64) and macOS (x86_64, arm64).
- Nothing is setgid and nothing is written to system folders: each game
  keeps its files in the player's data folder, `bsdgames/<game>` under
  `$XDG_DATA_HOME` (else `~/.local/share`), and reads its shipped files
  from the folder it is started in, where av installs them.

## hack

- Files: hack's playground (record, saved games, bones, the level files
  of a game in progress) is `bsdgames/hack` in the data folder, made on
  the first run with its save folder and the empty `record` and `perm`
  files hack expects (`hack/asciiverse.c`); `HACKDIR` and `-d` still
  choose another. `help`, `hh`, `data`, `rumors` and `news` are read from
  the folder the game was started in first (`config.h`).
- Build: `asciiverse/build/hack.sh` builds `makedefs`, generates
  `hack.onames.h` and builds the game, linking libtinfo where it is
  separate. Tab expansion uses `XTABS` on Linux where the BSDs have
  `OXTABS`. hack's own `delay_output()` is renamed
  `hack_delay_output()`, since ncurses has one with another signature.
- Centred: on a terminal bigger than 80x24 every cursor movement goes
  through `cursor_address` with an offset, so the field is drawn centred
  (`hack.terminfo.c`). `readchar()` waits with `poll()` on an unbuffered
  stdin and, after a resize, places the field again and redraws the level
  and the top line (without the `--More--` the old screen's message would
  ask for). The character questions before the game and the end-of-game
  pages are plain text and stay at the left.
- The player's name already came from `$USER` and `$LOGNAME` before the
  login records; unchanged.

## larn

- Build: its Makefile's own defines (`BSD`, `VER=12`, `SUBVER=0`,
  `NONAP`, `UIDSCORE`, `TERMIOS`), terminal through terminfo. `signal.c`
  uses `sigprocmask` instead of `sigsetmask` and `sigblock` (not in
  musl), catches `SIGEMT` only where it exists and names a fatal signal
  with `strsignal` instead of `sys_signame`.
- Files: the scoreboard, log, player ids, saved and checkpointed games
  and the diagnostic file go to `bsdgames/larn` in the data folder
  (`setpaths()`); `larn.help` and `larnmaze` are read from the folder the
  game was started in first.
- Centred: `lflush()` places every cursor position, the clear-screen
  home, the scrolling message lines and each new line with an offset on a
  terminal bigger than 80x24. `av_waitkey()`, called before every key
  read, waits with `poll()` and redraws centred after a resize.
- The player's name comes from `$USER` or `$LOGNAME` before `getlogin()`.
- `asciiverse/larn/NOTICE`, in the archive: Larn is copyright 1986 Noah
  Morgan, free by his terms for Larn 12.0 as long as no profit is made,
  so this title is free and never sold.

## warp

- Build: warp drives the terminal through termcap alone, so it links
  tinfo (termcap on macOS) rather than curses, and renames its own
  `LINES`, `COLS` and `typeahead`, which a static ncurses also defines.
  `warp/asciiverse.h` adds `termcap.h` and `time.h`, renames warp's
  `eaccess` (glibc has its own) and gives musl BSD's `sigblock` and
  `sigsetmask`. The star maps `smap.0` to `smap.7` are made at build
  time by `sm` from `smp.0` to `smp.7`.
- Files: the shipped files (the star maps, `warp.doc`, `warp.news`) are
  read from the folder the game was started in when `smap.0` is there.
  Saved games, scoreboards, the log and the half-gone universes are kept
  in `bsdgames/warp` in the data folder, where warp runs; `warp.log` is
  created at start, since `score()` locks by linking to it and otherwise
  waited ten seconds. The listing of saved games built its path without
  a slash; fixed.
- Three overflows in NetBSD's code, found with AddressSanitizer:
  `make_object` named its parameters x before y while every caller
  passes y before x, so every object was placed transposed and written
  past the end of `occupant[][]` (a second game in one run crashed about
  one time in three); `make_plink` and `make_blast` had the same swap,
  and `make_blast` took its size before its mass, unlike every caller;
  zapping and self-destructing near the edge blasted outside the
  universe, and those coordinates are now wrapped as everywhere else.
  The tty name buffer held 12 bytes, too few for `/dev/pts/100` and up.
- Centred: `move()` adds an offset to its `cursor_address` moves and
  `clear()` leaves the position unknown, so on a terminal bigger than
  80x24 the screen is drawn centred; the game loop checks for a resize
  every turn and redraws with `rewrite()`, warp's own ^R. The news and
  the instructions question before the game are plain text at the left.
- The scoreboard's name comes from `$NAME` first, as rn does, then the
  full name in the user database, then the login name.
