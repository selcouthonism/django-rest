#!/usr/bin/env python3
from pathlib import Path
import re
import sys


def update_installed_apps(settings_path: Path, app_name: str) -> None:
    text = settings_path.read_text()
    pattern = re.compile(r"(INSTALLED_APPS\s*=\s*\[)(.*?)(^\])", re.S | re.M)
    match = pattern.search(text)
    if not match:
        raise SystemExit('Could not find INSTALLED_APPS in settings.py')

    prefix, block, suffix = match.groups()
    lines = [line for line in block.splitlines()]
    existing = {line.strip().strip(',') for line in lines if line.strip()}
    insertions = []
    if f"'{app_name}'" not in existing:
        insertions.append(f"    '{app_name}',")
    if "'rest_framework'" not in existing:
        insertions.append("    'rest_framework',")

    if insertions:
        if lines and lines[-1].strip():
            lines.append('')
        lines.extend(insertions)
        new_block = '\n'.join(lines)
        new_text = text[:match.start(2)] + new_block + text[match.end(2):]
        settings_path.write_text(new_text)
        print(f"Added {', '.join(insertions)} to {settings_path}")
    else:
        print('No changes needed to INSTALLED_APPS')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: update_settings_installed_apps.py <settings.py> <app_name>')

    settings_path = Path(sys.argv[1])
    app_name = sys.argv[2]
    update_installed_apps(settings_path, app_name)
