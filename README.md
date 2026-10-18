# Pets

A cast of characters who live on your screens.

Pets is a small ambient platform: a handful of pets wander
between the displays in a house, walking off one screen and
arriving on the next, sitting with you while you work, and
reacting to your day. One coordinator service (not included
in this edition) owns where every pet is; each screen is a
renderer that draws whichever pets are currently visiting.

This repository is the public edition: the macOS renderer,
the asset pipelines, and the cast artwork. It is a curated
snapshot of a private working repo, published so the code
and the approach can be read, borrowed, and built on.

## The cast

- Lucas and Mike, two friends, and Carbon the cat.
- Nova and ARIA, the house's AI agents, embodied as cast
  members whose behaviour is driven by the agents' real
  state rather than a random number generator.

Every cast member has the same anatomy: a persona, a mood
that drifts with events, a memory of recent happenings, a
vocabulary, and a driver. Pets whose driver is a live agent
show the agent's working state on their bodies; when the
agent is away, a character engine understudies the body and
sticks to character speech.

## What's here

- `mac/` The macOS app. The pets live in a strip along the
  Dock: spring physics, drag and throw, window-aware play
  (they gather near the window you are working in), and a
  social layer. It renders real sprite animation and takes
  speech bubbles from the coordinator.
- `mac/context_reporter.py` A small reporter that classifies
  what you are doing (coding, writing, meeting, browsing,
  idle, away) on the Mac and posts only that classification,
  plus calendar pressure, to the coordinator. Raw window
  titles and URLs never leave the machine. The pets use the
  feed to warn you about a meeting in a few minutes or to
  nudge you, gently and then less gently, to take a break.
- `faces/` The 1-bit face pack for a 128 by 128 monochrome
  OLED companion display: eight expressions per pet, the
  converter that builds them from sheets, and animated
  6 fps sequences converted from short motion loops.
- `mac/frames/`, `mac/walk8-source/` The sprite frames and
  the eight-frame walk cycles, with the slicer that built
  them.
- `docs/ONE-PAGER.md` The architecture on one page.

## The coordinator

The coordinator (pets-mcp in the author's house) is a
single Python service that owns the registry, each pet's
tracked location, roaming, reconciliation against live
screen readback, and an event bus the screens speak. It is
described in the one-pager but is not part of this edition.
The wire shape is simple: screens publish their live state
about once a second and subscribe to a stream of intents
(arrive, depart, portal, greet, say), with a file-based
channel underneath as fallback. A bus token in
`~/.config/pets/bus-token` authenticates a screen; the
coordinator's own API secret never reaches a screen.

## Running the Mac app

You need a coordinator speaking the protocol above, or the
app runs happily in ambient-only mode with whoever is home.

1. Point the app at your coordinator: write its base URL
   (for example `http://192.168.1.10:7891`) into
   `~/.config/pets/bus-host`, put the shared bus token in
   `~/.config/pets/bus-token`, and replace
   YOUR-COORDINATOR-HOST in `mac/Info.plist` with the same
   host so the ATS exception matches.
2. Edit the path in `mac/io.niclydon.pets.plist` to your
   own home directory.
3. Run `mac/build.sh`. It compiles the app, installs it to
   `~/Applications/Pets.app`, and registers the LaunchAgent.

The context reporter is optional: install
`mac/context_reporter.py` behind a LaunchAgent that runs
it every 30 seconds, and set PETS_BUS_URL if your
coordinator is not on localhost. Its calendar read uses a
small EventKit bridge app on the author's Mac; without it,
the reporter degrades to app and idle classification only.

## License

The code is MIT licensed (see LICENSE). The artwork is
not: the cast are likenesses of real people, a real cat,
and the author's agents, and the art ships all rights
reserved (see ASSETS.md). Build your own cast; the
pipeline makes it easy.
