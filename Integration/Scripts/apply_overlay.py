#!/usr/bin/env python3
"""Generate build-time overlays; do not commit generated upstream modifications."""
from pathlib import Path
import plistlib
import shutil

root = Path(__file__).resolve().parents[2]
widget = root / 'Widget'
app = root / 'Bark'
integration = root / 'Integration'
# Select the private Cloudflare Bark server for fresh installs without changing
# existing users' saved server choices. This patch is generated at build time.
server_manager = root / 'Common' / 'ServerManager.swift'
server_code = server_manager.read_text(encoding='utf-8')
upstream_server = 'let defaultServer = "https://api.day.app"'
private_server = 'let defaultServer = "https://bark-worker.davidpovarski1.workers.dev"'
assert upstream_server in server_code or private_server in server_code, 'Upstream default server changed'
server_manager.write_text(server_code.replace(upstream_server, private_server), encoding='utf-8')
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
# Deflector uses iOS 26 IntentModes and modern SwiftUI throughout.
# The integrated app and extensions must all use iOS 26+, not Bark's iOS 15.
import re
pbx, target_count = re.subn(r'IPHONEOS_DEPLOYMENT_TARGET = (?:15[.]0|17[.]0|26[.]0|26[.]2|27[.]0);', 'IPHONEOS_DEPLOYMENT_TARGET = 26.2;', pbx)
assert target_count >= 10, f'Expected Bark deployment settings, found {target_count}'
marker = '0661A543204FDA4100965E4E /* AppDelegate.swift in Sources */'
assert pbx.count(marker) >= 2, 'AppDelegate source reference changed'
files = [
    ('HubSharedActivity', 'A1B2C3D4E5F607182930AB01', 'A1B2C3D4E5F607182930AC01'),
    ('HubActivityManager', 'A1B2C3D4E5F607182930AB02', 'A1B2C3D4E5F607182930AC02'),
    ('HubControlIntents', 'A1B2C3D4E5F607182930AB03', 'A1B2C3D4E5F607182930AC03'),
    ('DeflectorAutomationDetect', 'A1B2C3D4E5F607182930AB04', 'A1B2C3D4E5F607182930AC04'),
    ('HubNotificationCleanup', 'A1B2C3D4E5F607182930AB05', 'A1B2C3D4E5F607182930AC05'),
]
original_automation = root / 'Vendor' / 'Deflector' / 'Deflector' / 'Deflector' / 'AppIntents' / 'SystemIntents' / 'SystemAutomationDetectIntent.swift'
assert original_automation.exists(), 'Deflector automation callback moved upstream'
# Keep vendor code byte-for-byte identical; materialize only into generated app source.

for name, file_id, build_id in files:
    generated = app / (name + '.generated.swift')
    source = original_automation if name == 'DeflectorAutomationDetect' else integration / 'App' / (name + '.swift')
    shutil.copyfile(source, generated)
    if name == 'DeflectorAutomationDetect':
        content = generated.read_text(encoding='utf-8')
        content = content.replace('struct SystemAutomationDetectIntent: AppIntent {', '@available(iOS 26.0, *)\nstruct SystemAutomationDetectIntent: AppIntent {')
        old_cleanup = 'UNUserNotificationCenter.current().removeAllDeliveredNotifications()'
        assert content.count(old_cleanup) == 1, 'Deflector callback cleanup changed upstream; inspect before integration'
        content = content.replace(old_cleanup, 'await HubNotificationCleanup.removeDeflection()')
        generated.write_text(content, encoding='utf-8')
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
    output = widget / (name + '.upstream.generated.swift')
    shutil.copyfile(upstream, output)
    if name == 'DeflectionService':
        content = output.read_text(encoding='utf-8')
        needle = 'content.title = "Deflection"'
        assert content.count(needle) == 1, 'Deflector notification creation changed upstream; inspect before integration'
        content = content.replace(needle, needle + '\n        content.userInfo[ "shortcutsHub.origin" ] = "Deflector"')
        output.write_text(content, encoding='utf-8')

print('Generated app, widget, ActivityKit, intent and original Deflector source overlays.')
