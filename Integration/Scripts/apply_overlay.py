#!/usr/bin/env python3
"""Generate build-time overlays; do not commit generated upstream modifications."""
from pathlib import Path
import plistlib
import shutil

root = Path(__file__).resolve().parents[2]
widget = root / 'Widget'
app = root / 'Bark'
integration = root / 'Integration'
shutil.copyfile(integration / 'Widget' / 'ShortcutsHubWidgets.swift', widget / 'ShortcutsHubWidgets.generated.swift')
shutil.copyfile(integration / 'App' / 'HubSharedActivity.swift', widget / 'HubSharedActivity.generated.swift')

bundle = widget / 'WidgetBundle.swift'
original = bundle.read_text(encoding='utf-8')
needle = '        RecentMessagesWidget()'
assert original.count(needle) == 1, 'Upstream widget changed'
if 'HubLiveActivityWidget()' not in original:
    original = original.replace(needle, needle + '\n        if #available(iOS 17.0, *) {\n            HubShortcutWidget()\n            HubLiveActivityWidget()\n        }')
    bundle.write_text(original, encoding='utf-8')

info = app / 'Info.plist'
with info.open('rb') as f:
    data = plistlib.load(f)
data['NSSupportsLiveActivities'] = True
with info.open('wb') as f:
    plistlib.dump(data, f, sort_keys=False)

# The Bark app uses explicit PBX groups, unlike the filesystem-synced Widget target.
# Inject generated app source references at build time only.
project = root / 'Bark.xcodeproj' / 'project.pbxproj'
pbx = project.read_text(encoding='utf-8')
marker = '0661A543204FDA4100965E4E /* AppDelegate.swift in Sources */'
assert pbx.count(marker) >= 2, 'AppDelegate source reference changed'
files = [
    ('HubSharedActivity', 'A1B2C3D4E5F607182930AB01', 'A1B2C3D4E5F607182930AC01'),
    ('HubActivityManager', 'A1B2C3D4E5F607182930AB02', 'A1B2C3D4E5F607182930AC02'),
    ('HubControlIntents', 'A1B2C3D4E5F607182930AB03', 'A1B2C3D4E5F607182930AC03'),
    ('DeflectorAutomationDetect', 'A1B2C3D4E5F607182930AB04', 'A1B2C3D4E5F607182930AC04'),
]
original_automation = root / 'Vendor' / 'Deflector' / 'Deflector' / 'Deflector' / 'AppIntents' / 'SystemIntents' / 'SystemAutomationDetectIntent.swift'
assert original_automation.exists(), 'Deflector automation callback moved upstream'
# Keep vendor code byte-for-byte identical; materialize only into generated app source.

for name, file_id, build_id in files:
    generated = app / (name + '.generated.swift')
    source = original_automation if name == 'DeflectorAutomationDetect' else integration / 'App' / (name + '.swift')
    shutil.copyfile(source, generated)
    if file_id in pbx:
        continue
    # Add to PBXFileReference and PBXBuildFile sections, Bark group and Bark target Sources.
    pbx = pbx.replace('/* End PBXFileReference section */', f'\t\t{file_id} /* {name}.generated.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = {name}.generated.swift; sourceTree = "<group>"; }};\n/* End PBXFileReference section */')
    pbx = pbx.replace('/* End PBXBuildFile section */', f'\t\t{build_id} /* {name}.generated.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {file_id} /* {name}.generated.swift */; }};\n/* End PBXBuildFile section */')
    group_needle = '0661A542204FDA4100965E4E /* AppDelegate.swift */,'
    assert pbx.count(group_needle) == 1
    pbx = pbx.replace(group_needle, group_needle + f'\n\t\t\t\t{file_id} /* {name}.generated.swift */,')
    sources_needle = marker + ','
    assert pbx.count(sources_needle) == 1
    pbx = pbx.replace(sources_needle, sources_needle + f'\n\t\t\t\t{build_id} /* {name}.generated.swift in Sources */,')
project.write_text(pbx, encoding='utf-8')

# Compile selected original Deflector files, not reimplemented copies.
# The widget target uses Xcode's filesystem-synchronized Widget directory.
originals = {
    'DeflectionService': 'Shared/Models/Services/DeflectionService.swift',
    'SendDeflectionNotificationIntent': 'Shared/AppIntents/SendDeflectionNotificationIntent.swift',
    'UserNotificationSupport': 'Shared/Models/Supports/UserNotificationSupport.swift',
}
for name, relative in originals.items():
    upstream = root / 'Vendor' / 'Deflector' / 'Deflector' / relative
    assert upstream.exists(), f'Deflector upstream path changed: {relative}'
    shutil.copyfile(upstream, widget / (name + '.upstream.generated.swift'))

print('Generated app, widget, ActivityKit, intent and original Deflector source overlays.')
