# Shortcuts Hub integration boundary

This branch starts from Bark master and vendors the complete Deflector Git history under Vendor/Deflector using git subtree add without --squash. Do not edit vendor sources for app-specific changes.

## Source ownership
- Bark upstream: master branch and original Git history.
- Deflector upstream: Vendor/Deflector/** is read-only. Retain upstream MIT license and attribution.
- Integration: Integration/**, integration-specific CI and generated project overlays.
- Bark-Worker: separate GPL-3.0 server repository.

## Update Deflector
```
git fetch deflector-upstream main
git subtree pull --prefix=Vendor/Deflector deflector-upstream main -m "Merge Deflector upstream update"
```
The subtree commit records its upstream split SHA and preserves full ancestry. Review updates and build/test after each merge.

## Current integration state
Deflector source and Git history are now vendored but NOT yet linked into Bark Xcode targets. Do not confuse source inclusion with a working Live Activity or App Intent. Build an integration-owned bridge/target overlay for notification automation, App Intents, ActivityKit, widget extension, app groups and signing. Keep original vendor files unchanged. Do not duplicate Swift type definitions across targets.

Deflector's SystemAutomationDetectIntent removes all delivered Deflector notifications when invoked by an automation. A Bark bridge should instead correlate and delete the specific notification where feasible.
