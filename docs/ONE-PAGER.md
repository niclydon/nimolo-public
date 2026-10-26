# Nimolo: one cast of characters, every screen in the house

## The concept

Nimolo is a small living system, not five separate desk toys. A cast of chibi sprite characters ("Nims"), two friends and Carbon the cat, plus Nova and ARIA, the house's AI agents embodied, inhabit the screens of the house as if the screens were rooms: the Pane panel, the Flint TV console, the MacBook, the Orbit round display, and the AIPI companion screen, arranged in a fixed spatial order (pane, flint, macbook, orbit, aipi) the way rooms line a hallway. A pet exists in exactly one room at a time. It walks out of one screen's edge and into the next, or steps through a portal when the trip is long. Left alone, the cast wanders the whole house on its own: strolling to the neighbouring room, travelling to visit a friend, greeting each other when they meet, talking in small speech bubbles, and, when a human pet meets the cat, petting him. The system is ambient: nobody has to drive it. It is also fully directable: any pet can be summoned, sent, teleported, fenced out of a room, made to speak, or switched off, by name, at any time.

## Components

**The cast.** Each pet is a sprite set generated from reference photos of its real-life counterpart (the cat from a photo library cluster of him), derived from one canonical sheet per pet: walk cycles in both directions, idle, peace-sign, sit and sleep frames. Each pet also carries a persona (voice, traits, line banks, an affect baseline), an episodic memory, and a driver: the two agents are embodied, driven by their real presence and state, with a character engine understudying the body in character while the agent is away; the rest are driven by the character engine outright.

**The rooms (renderers).** Screens are deliberately dumb. Each runs the same ambient state machine (walk 42%, idle 20%, sit 15%, peace 12%, sleep 11%) and the same event vocabulary (arrive/depart at either edge, portal in/out, greet, say), sizes each pet by the registry scale the coordinator carries on every intent (Carbon at 0.5), and adds what its hardware is good at. Pane (ESP32-S3, 480x320 touchscreen) reacts to touch and persists presence in NVS across reboots. Flint (Raspberry Pi, SDL on the TV) is a wide ambient stage with presence readback every second. The MacBook app (Nimolo Dock: single-file Swift, an overlay that must never take keyboard or mouse focus) is the physical one: spring-based drag and throw, gravity, bounce, panic falls, and the full social layer; it pulls its art from the coordinator's pack store and verifies every file against the pack manifest before showing a pet. Orbit (ESP32-S3, 240x240 round touch display) is bus-only, and its companion Pip face follows the resident pet. AIPI (a small ESP32-S3 companion display with a 128x128 colour face screen) is a resident room: the house in miniature, showing the tracked world on its own bus channel.

**The coordinator (nimolo-mcp, not included in this edition).** One Python service on a home server is the only brain. Its store is a small Postgres database, with JSON exports as the working copy and rollback. It owns the registry and each pet's tracked location, and it is the single writer of moves: serialized, one pet at a time, with a departure confirmed on the source screen before any arrival is allowed on the destination. Tracked state is continuously reconciled against live readback from all five screens, and a room that goes dark past its window is evacuated to the nearest answering room, so a disagreement is a visible fact, not a silent drift.

**The event bus.** A realtime channel inside the same service (token-authenticated; screens never hold the coordinator's API secret). Screens publish their live state every second and subscribe to a server-sent stream of intents, which arrive in milliseconds; an older file channel runs underneath as fallback for the screens that have it, and a screen that restarts is automatically resynced with the pets it is supposed to have.

**Network packs.** Shipped, not future work: the coordinator serves per-pet asset packs built from the canonical sheets behind a sha256 parity gate, one profile per screen family (mac-240, pip-face, pip-anim, orbit-240, aipi-face). A renderer need not carry the cast's art: on enable it pulls the pack for its profile, verifies it, and only then shows the pet; on disable the cache is evicted. A pet whose art cannot be pulled stays absent: honest absence over wrong art.

## Coordination and the roaming director

A background director in the coordinator gives the cast its autonomy: every pet gets a decision every 55 to 130 seconds, weighted between staying put (42%), visiting another pet (22%), strolling to the spatially neighbouring room (22%) and portaling anywhere allowed (14%). It honours per-pet fences, disabled pets, each pet's compiled frame sets, screen availability, and never interrupts a pet being dragged on the Mac. Every decision is logged and inspectable.

## Interaction

On one screen, pets are aware of each other locally: a greeting becomes a walk-over, then a paired exchange (a "?" answered with a word; Carbon answers in mrrp and meow). Wandering pets that bump into each other stop and talk. A human meeting Carbon pets him instead, arm raised, while Carbon purrs. Across screens, interaction is mediated by the coordinator: meets, follows (one pet shadows another room to room), gatherings, and direct speech. People interact too: touch on the panels, click and drag on the Mac.

## The MCP surface

The coordinator exposes 59 MCP tools: 32 canonical nimolo_* tools covering status, moves, speech, fences, roaming, reconciliation and personas, plus 27 legacy aliases kept for older callers.

## The one rule that keeps it honest

A pet is in one place, provably. Moves are sequence-numbered, departures are confirmed before arrivals, sequence counters can never rewind, and any screen's live readback can contradict the coordinator in nimolo_status. Everything else, the wandering, the talking, the petting, is built on that floor.

*Status: live in the author's house across all five screens, roaming on. This edition carries the Mac renderer, the asset pipelines, and the cast artwork; the coordinator and the device firmware live in the author's private repos.*
