# Snapshot and provenance

This repository is the second **public edition** of Nimolo, a small
ambient platform whose cast of characters lives on the screens of a
house (see README.md and docs/ONE-PAGER.md).

- Source: the private `nimolo` repository, HEAD of October 21, 2026.
- Form: a single-commit curated snapshot, scrubbed as below. Not a
  mirror; the private platform has moved on since the snapshot date.
- Predecessor: the first edition (October 2026) was built from the
  platform's earlier codebase and published here; it is preserved,
  archived, as `nimolo-public-legacy`. This edition replaces it
  because the platform was renamed and restructured after that
  snapshot was cut.

## What is included, what is not

Included: the macOS renderer (`mac/`, including the context
reporter), the face-pack pipelines and artwork (`faces/`), the
sprite sources, and the architecture one-pager.

Excluded, as in the first edition: the reference-photo directories
for two cast members (real photographs never ship), the private
design narratives and change diary, desktop snapshot/preview
images, AI media-generation provenance files, and the coordinator
service itself (described in the one-pager; it stays private).

`docs/ONE-PAGER.md` is carried from the first edition's scrubbed
text: the private copy still carries the platform's old name and
house details, and the scrubbed text is the current one.

## Scrub standard

- The coordinator's private network address is parameterized in
  code, not merely documented: the renderer and the context
  reporter resolve the bus base URL from `~/.config/nimolo/bus-host`,
  else `$NIMOLO_BUS_URL`, else a localhost default; the ATS
  exception in Info.plist is a placeholder the reader replaces
  with their own coordinator host; the LaunchAgent program path
  uses a placeholder home directory.
- Every shipped image was scanned: no GPS or location EXIF
  anywhere (334 images checked), and the one AI-generation
  provenance text chunk present in the source art was stripped.
- Pattern scans for names, addresses, home paths, and hostnames,
  plus a gitleaks pass over the tree: clean before publication.

## Refresh policy

Editions are cut deliberately, not continuously: when the platform
changes materially, a new snapshot is built to this standard and
this page is updated.
