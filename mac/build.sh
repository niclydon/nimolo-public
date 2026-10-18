#!/bin/bash
# Build Pets.app on the MacBook and (re)install it.
set -euo pipefail
cd "$(dirname "$0")"
swiftc -O -o PetsBin main.swift
rm -rf Pets.app
mkdir -p Pets.app/Contents/MacOS Pets.app/Contents/Resources
mv PetsBin Pets.app/Contents/MacOS/Pets
cp Info.plist Pets.app/Contents/Info.plist
cp -R frames Pets.app/Contents/Resources/frames
mkdir -p ~/Applications ~/Library/LaunchAgents ~/.config/pets
rm -rf ~/Applications/Pets.app
cp -R Pets.app ~/Applications/Pets.app
cp io.niclydon.pets.plist ~/Library/LaunchAgents/
launchctl bootout gui/$(id -u)/io.niclydon.pets 2>/dev/null || true
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/io.niclydon.pets.plist
echo "Pets.app installed and launched"
