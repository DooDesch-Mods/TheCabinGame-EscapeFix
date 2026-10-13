# CabinEscapeFix

> 🛟 **Need help or found a bug?** Get support at [support.doodesch.de/escapefix](https://support.doodesch.de/escapefix).

Press Escape to return from Settings, Credits or Bug Report to the pause menu. Press it again to close the pause menu. An open quit confirmation uses the game's original No action.

This changes only the local pause menu. It does not alter game rules or multiplayer authority.

## Requirements

- The Cabin Game, Steam build `25553694`.
- [UE4SS for the cabin game](https://www.nexusmods.com/thecabingame/mods/4), `v3.0.1-1164-g5e627997`.
- Optional: [Mod Settings](https://www.nexusmods.com/thecabingame/mods/6) for the Enabled checkbox. Escape Fix is enabled by default without it.

## Install

1. Close the game and install UE4SS.
2. Copy `Mods/CabinEscapeFix` from the ZIP into `the_cabin_game/Binaries/Win64/ue4ss/Mods`.

With Mod Settings installed, open the main menu's Mods card, choose settings, select Escape Fix and change Enabled. Apply saves the setting.

## Remove

Close the game and remove only `ue4ss/Mods/CabinEscapeFix`. Back up its `Scripts/settings.dat` first if you want to keep the Enabled preference.

## Troubleshooting

If Escape does not close a pause-menu subview, check that Escape Fix is enabled and that UE4SS loaded the mod. Its messages appear in `ue4ss/UE4SS.log` under `[CabinEscapeFix]`.

## Development

Use Python 3.13. Install `requirements-dev.txt`, run `python -m unittest discover -s tests -v` and `python tests/check_lua.py`. `python tools/package.py --release` requires acceptance of the exact runtime payload. See [publishing](docs/publishing.md).

By DooDesch. Uses [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS). Code license: [MIT](LICENSE.md).
