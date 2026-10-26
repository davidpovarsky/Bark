#!/usr/bin/env python3
"""Fail CI if generated cleanup could erase unrelated Bark notifications."""
from pathlib import Path

root = Path(__file__).resolve().parents[2]
callback = (root / "Bark" / "DeflectorAutomationDetect.generated.swift").read_text(encoding="utf-8")
service = (root / "Widget" / "DeflectionService.upstream.generated.swift").read_text(encoding="utf-8")
cleanup = (root / "Bark" / "HubNotificationCleanup.generated.swift").read_text(encoding="utf-8")
ack = (root / "Bark" / "HubControlIntents.generated.swift").read_text(encoding="utf-8")

assert "removeAllDeliveredNotifications" not in callback, "Unsafe upstream deletion remains"
assert "HubNotificationCleanup.removeDeflection()" in callback
assert 'content.userInfo[ "shortcutsHub.origin" ] = "Deflector"' in service
assert 'notification.request.content.userInfo[originKey] as? String == originValue' in cleanup
assert 'notification.request.content.title == "Deflection"' in cleanup
assert 'eligible.first(where: { $0.request.identifier == requested })' in cleanup
assert "eligible.max" in cleanup
assert "removeDeliveredNotifications(withIdentifiers: [chosenID])" in cleanup
assert "removeAllDeliveredNotifications" not in cleanup
assert "removeDeflection(identifier: notificationIdentifier)" in ack
print("PASS: selective Deflector cleanup overlay; unrelated Bark alerts are not targeted")
