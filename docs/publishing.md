# Publishing

Publish only after the exact runtime payload passes game acceptance. Escape Fix's criterion is a real Escape key closing the original top pause-menu subview through its original return function. Native readback must confirm that the subview closes and Pause remains. Enabled Apply/reopen must also pass. Each passed check in `acceptance.json` names its observed evidence. Packaging does not replace native acceptance.

`single_mod` and `multiplayer` are explicitly `not_applicable`, with `passed: false`, a rationale and evidence. The mod changes local pause-menu UI and has no authority or replicated gameplay behavior. No isolated full round or network session is claimed. The other four checks remain required, and the payload fingerprint must match.

CI builds candidates on Linux and Windows. Both archive hashes must match the local build. The manual Release and update Nexus workflow repeats checks, requires acceptance, builds the release and verifies its public tag and downloaded ZIP/checksum. It never runs on a normal push.

Use the existing Nexus mod page and Main File. Configure repository variables:

| Variable | Value |
|---|---|
| NEXUS_FILE_GROUP_ID | Numeric API File ID from Main File > Advanced |
| NEXUS_MOD_ID | Numeric Unique Mod ID from the same panel |
| NEXUS_VORTEX_READY | true only after this mod's actual Nexus/Vortex download and deployment pass |

Use the existing organization secret NEXUSMODS_API_KEY. Its value stays in GitHub Secrets. The workflow's publish_nexus option checks the exact mod and file group, captures the latest Main File's file-to-file requirement ranges before upload, then copies those ranges to the acknowledged release version and reads them back. The receipt is retained as a workflow artifact. Parent status may be published or not_published; draft upload guards remain unchanged.

The first GitHub release can run with publish_nexus disabled. An existing release is reused only if its tag and uploaded bytes match this exact commit. Failed or unclear Nexus uploads must be inspected on Nexus before another upload; do not replay a timed-out upload automatically.

The successful release workflow dispatches the Discord announcement for its exact release tag. It does not rely on a release event from GITHUB_TOKEN.

Do not include the game, UE4SS runtime, diagnostics, saved settings or original extracted assets in the archive.
