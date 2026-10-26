# Shortcuts Hub integration

## Goal
Combine Bark push notifications with Deflector's shortcut launcher, Live Activity, App Intents, and widget UI in one iPad app, retaining Bark-Worker as an independent GPL-3.0 server.

## Current verified state
- Forks: davidpovarsky/Bark, davidpovarsky/Deflector, davidpovarsky/bark-worker.
- Original source trees are checked out alongside one another under Code/ShortcutsHub.
- Deflector's DeflectionService and SendDeflectionNotificationIntent have been copied to Common as reference integration sources. They are NOT yet included in Bark Xcode target and are NOT build-ready. Do not present as a functioning integration.
- Original Deflector code is MIT; retain its attribution. Bark is MIT; bark-worker is GPL-3.0 and stays separate.

## Required engineering sequence
1. Audit Xcode project structure, existing Bark Widget and NotificationService targets, app groups, bundle IDs, signing, ActivityKit, and minimum OS versions. Avoid breaking Bark's APNs registration and message handling.
2. Integrate Deflector's shared models, notification trigger, settings, Live Activity lifecycle and widget extension into Bark's targets; adapt module and app group references, and preserve attribution.
3. Replace Deflector-specific assumptions in onboarding and notification trigger filters with the new combined app identity; ensure user-controlled authorization and an explicit trusted command allowlist.
4. Add a regular interactive widget launcher with App Intents; investigate SystemShortcut picker/input limitations separately, do not claim dynamic arbitrary shortcut execution without device tests.
5. Connect Bark-Worker with authenticated Push requests; do not deploy public unauthenticated endpoints or expose keys.
6. Add tests and GitHub Actions iOS build; verify on iPadOS 27 with real APNs, notification automations, Live Activity, and widgets. Windows alone cannot compile Xcode projects.

## Known integration hazards
- The copied DeflectionService references UserNotificationSupport from Deflector, which is not yet imported.
- Both source files require explicit Xcode target membership and dependencies.
- APNs entitlements and ActivityKit require Apple provisioning; unsigned IPA cannot prove push delivery.
- No live Cloudflare deployment or on-device verification has been performed.
