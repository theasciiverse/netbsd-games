# Changes from upstream

This is the Asciiverse packaging of the BSD games that Mike Sharov's
bsd-games (packaged in `theasciiverse/bsdgames`) dropped: canfield, cgram,
hack, hunt, larn, rogue and warp, from NetBSD's own source tree. The first
commit imports NetBSD's `src/games` folders for them unchanged, at
NetBSD commit `1fc61a5c45cdd2a67b7e1b272c41a67aa200f621` (2026-10-13,
tag `netbsd-1fc61a5`); phantasia came along and is not built. A later
commit imports `rain` and `worms`, Eric P. Scott's screen pieces from
Caltech (1980), unchanged from the same NetBSD commit; they are Art &
Demos titles (kind `art`) in the catalog. A third imports `backgammon`
(Alan Char, 1980) with its rules and tutorial, `teachgammon`, unchanged
from the same commit (all 29 files checked against its tree), which
Sharov's bsd-games had dropped in favour of GNU Backgammon. Everything
after the imports is ours.

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
- `compat.h` also gives `__CTASSERT` (a `_Static_assert`), for worms,
  and maps BSD's `OXTABS` termios flag to Linux's `XTABS`, for backgammon.
- `compat/centre.h` and `compat/centre.c` centre the curses games (canfield,
  cgram, hunt, rogue) in the terminal: New BSD Games' `src/centre.h` (CC0),
  split so a game of several source files shares one state. `stdscr`
  becomes a pad, `refresh()` shows its drawn area centred (grown at once,
  shrunk once the drawing has stayed smaller for two seconds) and a resized
  terminal re-centres it, also for games that read their keys without
  `getch()`; `nb_fixed()` centres a field of fixed size whole, however
  much of it is drawn yet.
- `asciiverse/record/`: the drivers that play each game for its preview
  in `asciiverse/casts/`, reading the screen through pyte (`rec.py`, from
  BSD Games').
- Nothing is setgid and nothing is written to system folders: each game
  keeps its files in the player's data folder, `bsdgames/<game>` under
  `$XDG_DATA_HOME` (else `~/.local/share`), and reads its shipped files
  from the folder it is started in, where av installs them.

## canfield

- Scores: without the shared score file, the player's betting record is
  kept in `bsdgames/cfscores` in the data folder (`openuserscores()`).
  `cfscores`, which lists every user's record on a shared machine, is not
  built.
- Centred by `compat/centre.h`; the table is the same size all game.
- `asciiverse/canfield/LICENSE`: the BSD licence from the source header.

## cgram

- Quotes: with a file named `maxims` in the folder it is started in, each
  game picks one of its entries at random (`readlocalquote()`) instead of
  running `fortune`, which the Asciiverse does not install.
  `asciiverse/cgram/maxims` holds 456 of La Rochefoucauld's maxims in
  J. Hain Friswell's 1871 translation, public domain, from Project
  Gutenberg ebook 9105 (`pg9105.txt`, sha256 `1bbcb977...`), the
  translator's bracketed notes removed.
- Centred by `compat/centre.h`; the help line is drawn under the text
  instead of on the terminal's last line, so the two are centred as one
  block.
- `asciiverse/cgram/LICENSE`: the BSD licence from the source header.

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

## hunt

- Starting the server: `hunt` starts the `huntd` that sits beside it
  (found through `/proc/self/exe` on Linux and `_NSGetExecutablePath` on
  macOS, then `./huntd`, then the system path), with its output going
  nowhere instead of onto the player's screen.
- Linux: the broadcast search crashed on network interfaces with no
  address, which Linux lists and NetBSD does not; a server on this machine
  that answers from two addresses (Debian and Ubuntu map the host name to
  127.0.1.1) is offered once. `SO_USELOOPBACK` is used only where it
  exists, `setpgid` replaces BSD `setpgrp`, and the computer player's
  pause uses `sigprocmask` and `sigsuspend` instead of BSD `sigblock`,
  `sigpause` and `sigsetmask` (`sigpause` means something else on Linux).
  `hunt/asciiverse-compat.h` adds `INFTIM` and the headers musl needs.
- Centred by `compat/centre.h`, the whole 80x24 arena and status
  (`nb_fixed()`); `hunt` reads its keys itself, so a resize shows at the
  next refresh.
- Players who vanish leave the game: when a client's connection closed
  (its terminal closed, or it was killed), `huntd` was meant to play a
  `q` for it, but did so only when `errno` was `EINTR`, which it never is
  at the end of a connection, and left the count of keys at 0, so the
  player stayed in the game for good, and the server with it
  (`havechar()` in `huntd/driver.c`, a NetBSD bug).
- The computer player (`hunt -o`) plays on: the server confirms keys
  with READY only in a pass with new input and dropped the count of keys
  carried out in other passes, and a second key read with the first
  waited for the next network event; READY now counts every key carried
  out, and read keys are carried out at once. The client counted keys
  that its limit then kept from being sent. Either left otto waiting for
  ever for answers. And otto, when it has stood still facing the same
  way for eight turns, now turns and steps somewhere at random instead of
  pushing at the same spot for ever (`otto.c`).
- `asciiverse/hunt/LICENSE`: the BSD licence from the source headers.

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

## rogue

- Build: `-DUNIX` for its machine-dependent code; `<time.h>` and
  `<fcntl.h>` are always included, and `fpurge` is `__fpurge` from
  `<stdio_ext.h>` on glibc and musl.
- Files: the score file, saved games (`rogue.save`, and `rogue.esave` on
  a hangup) and screen dumps go to `bsdgames/rogue` in the data folder
  (`md_datafile()`); a name with a slash is used as given, and restoring a
  bare name looks in the data folder when it is not in the current one.
  The score file is made at the first lock, so a new install no longer
  says "cannot lock score file".
- The player's name comes from `$LOGNAME` or `$USER` before the password
  database (`md_gln()`).
- Centred by `compat/centre.h`, the whole 80x24 dungeon, explored or not
  (`nb_fixed()`); rogue reads its keys itself, so a resize shows at the
  next refresh.
- `asciiverse/rogue/NOTICE`, in the archive: besides the BSD licence, the
  source carries the notice that it "is not to be traded, sold, or used
  for personal gain or profit", so this title is free and never sold.

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

## rain

- Any key quits, q among them (upstream: only a signal, such as Ctrl+C,
  which still works): curses reads keys without waiting between drops.
- A resize clears the screen and starts the drops over inside the new
  size. Upstream's own check, `is_term_resized(LINES, COLS)`, compares
  the size with itself under ncurses (which keeps `LINES` and `COLS` in
  step with the screen) and never fires; the resize now comes in as
  `KEY_RESIZE`. Below 4 lines or columns the drop area went negative,
  which upstream's check for 0 missed; it is now at least 1.
- A new seed every run (`srandom()` from the time and process id);
  upstream never seeded, so every run rained the same.
- Not centred: it draws over the whole terminal.
- `asciiverse/rain/LICENSE`: the BSD licence from the source header.

## worms

- Any key quits, q among them (upstream: only a signal); Ctrl+C and the
  other signals still do.
- A resize starts the worms over on the new screen (upstream quit on
  `SIGWINCH`): the size-dependent half of `main()` is now `arena()`, run
  again after each `KEY_RESIZE`, freeing the old worms and grid.
- Sizes are fitted instead of refused, since the screen can change under
  it: more worms than fit (`-n`) are cut to the number that fits and worms
  too long for the screen (`-l`) are shortened, where upstream stopped
  with an error; a screen too small for worms (under 3 lines or columns,
  or under 40 cells) shows nothing until it is made bigger instead of
  exiting.
- The seed: `arc4random()` where libc has it (glibc, macOS), else the
  time and process id (musl has none).
- Not centred: it draws over the whole terminal.
- `asciiverse/worms/LICENSE`: the BSD licence from the source header.

## backgammon

backgammon and teachgammon (the rules and a tutorial game) are one title,
`backgammon`, shipped together.

- **Found beside each other.** backgammon starts teachgammon when the
  player asks for the rules, and teachgammon starts backgammon after the
  tutorial; both looked in `/usr/games`. Each now finds the other in the
  folder it was started from (`/proc/self/exe`, `_NSGetExecutablePath`),
  else the old path (`common_source/asciiverse.c`, `sibling()`).
- **Saved games in the data folder.** A game saved under a bare name goes
  in `bsdgames/backgammon` in the player's data folder and is recovered
  from there (`backgammon <name>` or `-s <name>`); a name with a `/` is
  used as it is. The save name was typed into a 50-byte buffer with no
  limit, so a long name overflowed it; it now stops at 49 characters.
- **Centred.** The game draws through its own cursor code (`fancy.c`), not
  curses, from the terminal's top left corner. Its 80x24 screen is now
  centred in a bigger terminal, sideways by its 53-column board as far as
  the 80 columns of messages still fit (20 columns in at 100, 33 at 120):
  direct cursor motion adds the offset, the
  moves that start from the terminal's own corner (home, carriage return)
  are not used when the screen is offset, and a cleared screen moves to
  the screen's corner. The real window size is read over the terminal
  type's. A resize interrupts the key read and redraws the board in the
  new place, as Ctrl+L does. teachgammon is centred the same way.
- **The computer checks the right squares for a hit.** `canhit()`
  (`odds.c`) judges whether a blot on point `i` can be hit by a man on `j`
  with a combination of dice. It checked the squares `k` and `diff - k`
  beyond `i`, away from `j`, instead of the squares the man lands on
  first, short of `i`; near either end of the board those indices ran
  past `board[26]` (AddressSanitizer: global-buffer-overflow, on most of
  the computer's moves). It now checks `i - a*k` and `i - a*(diff - k)`.
  This changes the computer's judgement of blots; chosen by David
  (2026-10-20) over only bounding the indices. OpenBSD's copy has the
  same code.
- **`raw` renamed `rawtty`.** The global `struct termios raw` clashed with
  curses' `raw()` in a static ncurses (Alpine's link failed).
- `asciiverse/backgammon/LICENSE`: the BSD licence from the source header.
- Catalog id `bsd-backgammon` (shown as BSD Backgammon, beside Nard), so
  the archives are `bsd-backgammon-<target>` and the preview is
  `asciiverse/casts/bsd-backgammon.cast`; the program is still
  `backgammon`.
- Left as it is: a hidden option in the colour question (`P` and the
  password `losfurng`) that lets the player choose the dice.
- Checked: Linux (glibc and static musl) at 100x30 and 120x40, with a
  resize mid-game; the rules starting teachgammon from another folder; a
  game saved under a 60-character name (cut to 49) in the data folder and
  recovered from another folder. ASan and UBSan: four 40-second runs of
  random keys, moves, saves, quits and resizes, clean after the `canhit`
  fix (leak checking off: the game never frees its tables). macOS: not
  built here.
- `asciiverse/record/backgammon.py`: the preview, White against the
  computer with moves chosen from the board on screen (legal sequences
  that use the most dice, then most hits, most points made, fewest blots
  left).
