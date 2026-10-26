# Pet faces: the charm pack

Front-facing face portraits for all three pets, designed for
small face-only displays, with Pip as the first target: its
128x128 monochrome SH1107 OLED takes a full frame through
pip_image, so a pet's face fills the little screen and the
expression follows what the pet is doing across the platform.
This is the Tier S face pack from the platform tier design;
the colour masters also serve any future colour face screen
(Pane could take them at its own size).

## The vocabulary

Eight expressions, one shared vocabulary for every pet, named
by the files in pip/<pet>/:

- content: the resting face. Relaxed eyes, small smile.
- blink: content with the eyes closed. Not a mood, an
  animation frame: the coordinator swaps it in for ~200 ms
  every 4-7 s so the charm feels alive.
- happy: greetings and meetings. Bright eyes, open smile.
- love: being petted (the Mac petting interaction). Blissful
  closed eyes and floating hearts; Carbon gets heart pupils.
- sleepy: the sleep ambient state. Closed eyes, a yawn, a Z.
- surprised: portal_in and arrivals. Wide eyes, small o.
- dizzy: thrown, falling, bumped. Spiral eyes, wavy mouth.
- sad: the featured pet leaving, or a screen going away.
  Droopy everything; Carbon's ears fold flat.

## Mapping (what the coordinator sends)

- ambient idle / sit / peace / walk: content, with blink
  swaps while the state holds
- ambient sleep: sleepy (no blinking; the Z is the motion)
- greet event, pet_meet: happy, held ~4 s
- say event: happy while the bubble is up
- portal_in, arrive on a screen: surprised, ~2 s, then the
  ambient face
- petting on the Mac: love, while the hand is there and ~2 s
  after
- throw / fall / bump meet: dizzy, ~2 s
- featured pet departs the platform's attention (roams off,
  screen sleeps): sad, ~3 s, then the next featured pet

## Featured pet

A face screen shows ONE pet: the featured pet. Default is
Carbon (the house cat). The feature passes to whichever pet
most recently did something (arrived, greeted, got petted);
after ~10 quiet minutes it drifts back to Carbon. The face
always reflects the featured pet's own state, wherever in
the house that pet currently is.

## Format and build

- Masters: source/<pet>-sheet.png, a 4x2 expression grid in
  grid order content, happy, love, sleepy / surprised,
  dizzy, sad, blink. (source/mike-sheet-textured.png is the
  first Mike sheet, kept for the record; his hair and beard
  texture defeated the converter, so his master is the flat
  sticker-style sheet.)
- Build: python3 build_faces.py slices the sheets, extracts
  line art, and writes pip/<pet>/<expression>.bin, exactly
  2048 bytes each in the Adafruit GFX layout pip_image
  expects (128x128, row-major, MSB first), plus a PNG twin
  per frame and contact sheets in previews/.
- Why line art: the masters are flat colour with dark fills
  (hair, beard, fur at luminance 60-130). A plain threshold
  turns those fills into solid lit masses and the faces
  drown. The converter lights only near-black strokes,
  strong local outline drops, grey strokes on paper, and
  bright strokes on darker fills (whiskers on fur), so the
  fills stay dark and every drawn line survives. The
  constants at the top of build_faces.py were tuned over
  three measured rounds; the previews are the evidence.
- Pack size: 24 frames x 2048 B = 48 KB total.

## Known soft spots (v1)

- Mike converts roughest: a heavy brow band, and his
  surprised panel drew round glasses. Recognisable, not
  polished. A hand-cleaned Mike master is the fix if it
  matters at 1.5 inches.
- Carbon's sad ears fold so flat he reads dog-like out of
  context; in sequence on the device it parses as sad cat.
- The unnamed friend's open eyes are soft rings at
  128 px; his mouths and fringe carry the expressions.
