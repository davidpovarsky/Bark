#!/usr/bin/env python3
"""Build-time personal Apple Developer identity overlay (vendor sources untouched)."""
import os
import plistlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
team = "NA6HPWARQ2"
bundle = "com.davidpovarsky.bark"
group = "group.com.davidpovarsky.bark"
roles = {
    "me.fin.bark.NotificationServiceExtension": (bundle + ".NotificationServiceExtension", "SERVICE"),
    "me.fin.bark.NotificationContent": (bundle + ".NotificationContent", "CONTENT"),
    "me.fin.bark.Widget": (bundle + ".Widget", "WIDGET"),
    "me.fin.bark": (bundle, "APP"),
}
pbx_path = root / "Bark.xcodeproj" / "project.pbxproj"
pbx = pbx_path.read_text(encoding="utf-8")
assert pbx.count("5U8LBRXG3A") >= 4, "Unexpected upstream team configuration"
pbx = pbx.replace("5U8LBRXG3A", team)
pbx = pbx.replace('DEVELOPMENT_TEAM = "";', f"DEVELOPMENT_TEAM = {team};")
for original, (new, role) in roles.items():
    assert pbx.count(f"PRODUCT_BUNDLE_IDENTIFIER = {original};") == 2, original
    name = os.environ.get(f"BARK_PROFILE_{role}_NAME", "").strip()
    if os.environ.get("BARK_REQUIRE_PROFILES") == "1":
        assert name, f"Missing provisioning profile name for {role}"
    name = name or f"Bark-Personal-{role}"
    assert all(c not in name for c in ('"', "\n", "\r")), "Invalid profile name"
    for kind in ("Development", "AppStore"):
        pbx = pbx.replace(f"match {kind} {original}", name)
    pbx = pbx.replace(f"PRODUCT_BUNDLE_IDENTIFIER = {original};", f"PRODUCT_BUNDLE_IDENTIFIER = {new};")
assert "5U8LBRXG3A" not in pbx
pbx_path.write_text(pbx, encoding="utf-8")

main = root / "Bark" / "Bark.entitlements"
with main.open("rb") as f:
    ent = plistlib.load(f)
for restricted in (
    "com.apple.developer.usernotifications.communication",
    "com.apple.developer.usernotifications.critical-alerts",
    "com.apple.developer.usernotifications.time-sensitive",
):
    ent.pop(restricted, None)
ent["aps-environment"] = "production"
ent["com.apple.security.application-groups"] = [group]
with main.open("wb") as f:
    plistlib.dump(ent, f, sort_keys=False)
for path in (
    "Widget/Widget.entitlements",
    "NotificationServiceExtension/NotificationServiceExtension.entitlements",
    "NotificationContentExtension/NotificationContentExtension.entitlements",
):
    file = root / path
    with file.open("rb") as f:
        data = plistlib.load(f)
    assert "group.bark" in data.get("com.apple.security.application-groups", []), path
    data["com.apple.security.application-groups"] = [group]
    with file.open("wb") as f:
        plistlib.dump(data, f, sort_keys=False)

replaced = 0
for directory in ("Bark", "Widget", "NotificationServiceExtension", "NotificationContentExtension", "Common", "Controller", "Model", "View"):
    folder = root / directory
    if not folder.exists():
        continue
    for file in folder.rglob("*.swift"):
        content = file.read_text(encoding="utf-8")
        if "group.bark" in content:
            replaced += content.count("group.bark")
            file.write_text(content.replace("group.bark", group), encoding="utf-8")
assert replaced >= 3, f"Expected shared storage references: {replaced}"
print(f"Configured {bundle}, {team}, four targets, shared group {group}")
