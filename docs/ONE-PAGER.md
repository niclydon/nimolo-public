# Nimolo: one cast of characters, every screen in the house

## The concept

Nimolo is a small living system, not three separate desk toys. A cast of chibi sprite characters, two friends and Carbon the cat, inhabit the screens of the house as if the screens were rooms: the Pane panel, the Flint TV console, and the MacBook, arranged in a fixed spatial order (Pane, Flint, MacBook) the way rooms line a hallway. A pet exists in exactly one room at a time. It walks out of one screen's edge and into the next, or steps through a portal when the trip is long. Left alone, the cast wanders the whole house on its own: strolling to the neighbouring room, travelling to visit a friend, greeting each other when they meet, talking in small speech bubbles, and, when a human pet meets the cat, petting him. The system is Ambient: nobody has to drive it. It is also fully directable: any pet can be summoned, sent, teleported, fenced out of a room, made to speak, or switched off, by name, at any time.

## Components

**The cast.** Each pet is a sprite set generated from reference photos of its real-life counterpart (the cat from a photo library cluster of him): walk cycles in both directions, idle, peace-sign, sit and sleep frames, rendered at 90 points tall on the Mac and 120 pixels on Flint.

**The rooms (renderers).** Screens are deliberately dumb. Each runs the same ambient state machine (walk 42%, idle 20%, sit 15%, peace 12%, sleep 11%) and the same event vocabulary (arrive/depart at either edge, portal in/out, greet, say), and each adds what its hardware is good at. Pane (ESP32, 480x320 touchscreen) reacts to touch: tap a pet for its reaction cycle, double-tap to portal in the next absent pet; presence persists in NVS across reboots. Flint (Raspberry Pi, SDL on the TV) is a wide ambient stage with presence readback every second. The MacBook app (single-file Swift, a full-screen overlay that must never take keyboard or mouse focus, pets are grabbed through global mouse monitors) is the physical one: spring-based drag and throw, gravity, bounce, panic falls, and the full social layer.

**The coordinator (pets-mcp).** One Python service on a home server (systemd, MCP over streamable HTTP on loopback, origin-secret guarded) is the only brain. It owns the registry and each pet's tracked location, and it is the single writer of moves: serialized, one pet at a time, with a departure confirmed on the source screen before any arrival is allowed on the destination. Tracked state is continuously reconciled against live readback from all three screens, so a disagreement is a visible fact, not a silent drift.

**The event bus.** A realtime channel inside the same service (tailnet listener, per-bus token; screens never hold the MCP secret). Screens publish their live state every second and subscribe to a server-sent stream of intents, which now arrive in milliseconds instead of on the next file poll; the older SSH file channel runs underneath as fallback, and a screen that restarts is automatically resynced with the pets it is supposed to have. The Mac is fully on the bus today; Flint's client is the next build.

## Coordination and the roaming director

A background director in pets-mcp gives the cast its autonomy: every pet gets a decision every 55 to 130 seconds, weighted between staying put (42%), visiting another pet (22%), strolling to the spatially neighbouring room (22%) and portaling anywhere allowed (14%). It honours per-pet fences (Carbon can be barred from Flint), disabled pets, each pet's compiled frame sets, screen availability, and never interrupts a pet being dragged on the Mac. Every decision is logged and inspectable.

## Interaction

On one screen, pets are aware of each other locally: a greeting becomes a walk-over, then a paired exchange (a "?" answered with a word; Carbon answers in mrrp and meow). Wandering pets that bump into each other stop and talk. A human meeting Carbon pets him instead, arm raised, while Carbon purrs. Across screens, interaction is mediated by the coordinator: meets, follows (one pet shadows another room to room), gatherings, and direct speech with pet_say. People interact too: touch on Pane, click and drag on the Mac.

## The MCP surface

Sixteen tools expose the whole system to agents: pets_list, pets_status, pets_bus, pet_register, pet_send, pet_call, pet_teleport, pet_meet, pets_together, pet_event, pet_say, pet_follow, pet_disable, pet_enable, pet_fence, pets_roam.

## The one rule that keeps it honest

A pet is in one place, provably. Moves are sequence-numbered, departures are confirmed before arrivals, sequence counters can never rewind, and any screen's live readback can contradict the coordinator in pets_status. Everything else, the wandering, the talking, the petting, is built on that floor.

*Status: live across a Mac, a TV display, and embedded screens, roaming on. Next: cross-screen reactions (pets noticing each other across the gap between rooms), and network-served pet packs so new cast members ship from the coordinator instead of per-device builds.*
