#!/usr/bin/env python3
"""Generate build-time integration outputs without editing tracked upstream sources."""
from pathlib import Path
import plistlib
import shutil

root = Path(__file__).resolve().parents[2]
widget = root / 'Widget'
source = root / 'Integration' / 'Widget' / 'ShortcutsHubWidgets.swift'
shutil.copyfile(source, widget / 'ShortcutsHubWidgets.generated.swift')

bundle = widget / 'WidgetBundle.swift'
original = bundle.read_text(encoding='utf-8')
needle = '        RecentMessagesWidget()'
assert original.count(needle) == 1, 'Bark WidgetBundle structure changed: inspect upstream before applying overlay'
if 'HubLiveActivityWidget()' not in original:
    original = original.replace(needle, needle + '\n        if #available(iOS 17.0, *) {\n            HubShortcutWidget()\n            HubLiveActivityWidget()\n        }')
    bundle.write_text(original, encoding='utf-8')

info = root / 'Bark' / 'Info.plist'
with info.open('rb') as f:
    data = plistlib.load(f)
data['NSSupportsLiveActivities'] = True
with info.open('wb') as f:
    plistlib.dump(data, f, sort_keys=False)
print('Shortcuts Hub overlay applied; upstream changes are generated working-tree modifications only.')
