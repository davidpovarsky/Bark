#!/usr/bin/env python3
"""Integrate Deflector's original SwiftUI screens into Bark at build time.

Vendor files are never edited. The original @main App wrapper is removed only
from the generated copy, since Bark already owns the UIApplication lifecycle.
"""
from pathlib import Path
import hashlib
import re

root = Path(__file__).resolve().parents[2]
vendor = root / "Vendor" / "Deflector" / "Deflector"
app = root / "Bark"
project = root / "Bark.xcodeproj" / "project.pbxproj"
pbx = project.read_text(encoding="utf-8")
tab_path = root / "Controller" / "BarkTabBarController.swift"
ipad_controller = root / "Controller" / "SectionViewController-iPad.swift"
ipad_model = root / "Controller" / "SectionViewModel-iPad.swift"

# Preserve original Deflector MainView and settings screens; only strip
# its application entry point in the generated copy.
sources = list((vendor / "Deflector").rglob("*.swift"))
sources += list((vendor / "Shared").rglob("*.swift"))
skip = {"SystemAutomationDetectIntent.swift", "SendDeflectionNotificationIntent.swift", "DeflectionService.swift", "UserNotificationSupport.swift"}
sources = [p for p in sources if p.name not in skip]
sources.append(root / "Integration" / "App" / "ShortcutsHubNavigation.swift")
for source in sources:
    relative = source.relative_to(vendor).as_posix() if source.is_relative_to(vendor) else "Integration/ShortcutsHubNavigation.swift"
    name = "DeflectorUI_" + hashlib.sha256(relative.encode()).hexdigest()[:16] + ".generated.swift"
    dest = app / name
    content = source.read_text(encoding="utf-8")
    if relative == "Deflector/Views/MainView.swift":
        match = re.search(r"@main\s+struct Deflector: App\s*\{", content)
        assert match, "Deflector app entry changed upstream"
        depth, end = 1, match.end()
        while depth:
            if content[end] == "{": depth += 1
            if content[end] == "}": depth -= 1
            end += 1
        content = content[:match.start()] + content[end:]
    dest.write_text(content, encoding="utf-8")
    file_id = hashlib.sha256(("file:" + relative).encode()).hexdigest()[:24].upper()
    build_id = hashlib.sha256(("build:" + relative).encode()).hexdigest()[:24].upper()
    if file_id in pbx: continue
    pbx = pbx.replace("/* End PBXFileReference section */", f'\t\t{file_id} /* {name} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = {name}; sourceTree = "<group>"; }};\n/* End PBXFileReference section */')
    pbx = pbx.replace("/* End PBXBuildFile section */", f'\t\t{build_id} /* {name} in Sources */ = {{isa = PBXBuildFile; fileRef = {file_id} /* {name} */; }};\n/* End PBXBuildFile section */')
    needle = '0661A542204FDA4100965E4E /* AppDelegate.swift */,'
    assert pbx.count(needle) == 1
    pbx = pbx.replace(needle, needle + f'\n\t\t\t\t{file_id} /* {name} */,')
    needle = '0661A543204FDA4100965E4E /* AppDelegate.swift in Sources */,'
    assert pbx.count(needle) == 1
    pbx = pbx.replace(needle, needle + f'\n\t\t\t\t{build_id} /* {name} in Sources */,')
project.write_text(pbx, encoding="utf-8")

tab = tab_path.read_text(encoding="utf-8")
needle = '            BarkNavigationController(rootViewController: MessageSettingsViewController(viewModel: MessageSettingsViewModel()))'
assert tab.count(needle) == 1
tab = tab.replace(needle, needle + ',\n            ShortcutsHubNavigation.makeController()')
needle = 'UITabBarItem(title: "settings".localized, image: UIImage(named: "baseline_manage_accounts_black_24pt"), tag: 2)'
assert tab.count(needle) == 1
tab = tab.replace(needle, needle + ',\n                           UITabBarItem(title: "קיצורים", image: UIImage(systemName: "square.grid.2x2"), tag: 3)')
tab_path.write_text(tab, encoding="utf-8")

ipad = ipad_controller.read_text(encoding="utf-8")
needle = '    let settingsController = BarkNavigationController(rootViewController: MessageSettingsViewController(viewModel: MessageSettingsViewModel()))'
assert ipad.count(needle) == 1
ipad = ipad.replace(needle, needle + '\n    let shortcutsHubController = ShortcutsHubNavigation.makeController()')
needle = '            settingsController\n'
assert ipad.count(needle) == 1
ipad = ipad.replace(needle, '            settingsController,\n            shortcutsHubController\n')
ipad_controller.write_text(ipad, encoding="utf-8")

model = ipad_model.read_text(encoding="utf-8")
needle = '            SectionItem(image: UIImage(named: "baseline_manage_accounts_black_24pt"), title: "settings".localized)'
assert model.count(needle) == 1
model = model.replace(needle, needle + ',\n            SectionItem(image: UIImage(systemName: "square.grid.2x2"), title: "קיצורים")')
ipad_model.write_text(model, encoding="utf-8")
print(f"Integrated {len(sources)} original Deflector UI/dependency Swift files and Bark phone/iPad navigation overlays")
