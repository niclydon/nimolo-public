#!/bin/bash
# Build Nimolo Dock.app (the Dock renderer;
# bundle id io.niclydon.nimolo, agent label
# io.niclydon.nimolo-dock) and (re)install it.
set -euo pipefail
cd "$(dirname "$0")"
swiftc -O -o PetsBin main.swift
rm -rf "Nimolo Dock.app"
mkdir -p "Nimolo Dock.app/Contents/MacOS" "Nimolo Dock.app/Contents/Resources"
mv PetsBin "Nimolo Dock.app/Contents/MacOS/Nimolo Dock"
cp Info.plist "Nimolo Dock.app/Contents/Info.plist"
cp -R frames "Nimolo Dock.app/Contents/Resources/frames"
mkdir -p ~/Applications ~/Library/LaunchAgents ~/.config/pets
rm -rf ~/Applications/Pets.app
rm -rf ~/Applications/"Nimolo Dock.app"
cp -R "Nimolo Dock.app" ~/Applications/
cp io.niclydon.nimolo-dock.plist ~/Library/LaunchAgents/
launchctl bootout gui/$(id -u)/io.niclydon.nimolo-dock 2>/dev/null || true
# bootstrap can race the bootout above (EIO); retry.
for i in 1 2 3 4 5; do
  launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/io.niclydon.nimolo-dock.plist 2>/dev/null && break
  sleep 2
done
echo "Nimolo Dock.app installed and launched"
