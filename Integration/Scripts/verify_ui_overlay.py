#!/usr/bin/env python3
"""Validate generated Bark navigation and original Deflector screen integration."""
from pathlib import Path
import hashlib
root = Path(__file__).resolve().parents[2]
vendor = root / "Vendor" / "Deflector" / "Deflector"
app = root / "Bark"
tab = (root / "Controller" / "BarkTabBarController.swift").read_text(encoding="utf-8")
ipad = (root / "Controller" / "SectionViewController-iPad.swift").read_text(encoding="utf-8")
model = (root / "Controller" / "SectionViewModel-iPad.swift").read_text(encoding="utf-8")
project = (root / "Bark.xcodeproj" / "project.pbxproj").read_text(encoding="utf-8")
assert "ShortcutsHubNavigation.makeController()" in tab
assert "ShortcutsHubNavigation.makeController()" in ipad
assert 'title: "קיצורים"' in tab
assert 'title: "קיצורים"' in model
relative = "Deflector/Views/MainView.swift"
name = "DeflectorUI_" + hashlib.sha256(relative.encode()).hexdigest()[:16] + ".generated.swift"
generated = (app / name).read_text(encoding="utf-8")
original = (vendor / relative).read_text(encoding="utf-8")
assert "struct MainView: View" in original and "struct MainView: View" in generated
assert "@main struct Deflector: App" not in generated
assert name in project
navigation_relative = "Integration/ShortcutsHubNavigation.swift"
navigation_name = "DeflectorUI_" + hashlib.sha256(navigation_relative.encode()).hexdigest()[:16] + ".generated.swift"
navigation = (app / navigation_name).read_text(encoding="utf-8")
assert "UIHostingController(rootView: MainView())" in navigation
assert navigation_name in project
assert "ShortcutsHubNavigation.makeController()" in tab and "ShortcutsHubNavigation.makeController()" in ipad
print("PASS: original Deflector MainView included in Bark target and accessible from phone tab and iPad sidebar")
