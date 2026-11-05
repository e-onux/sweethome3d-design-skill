#!/usr/bin/env python3
"""Install the pinned MCP plugin; optionally install the macOS app with Homebrew."""
import argparse
import hashlib
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from mcp_client import plugin_dir

VERSION = '1.2.0'
SHA256 = '0a47aac9854cf229362701fa06d36b77ea883f386a5201705803231493426a6f'
URL = f'https://github.com/grimashevich/sweethome3d-mcp-server/releases/download/v{VERSION}/sh3d-mcp-plugin-{VERSION}.sh3p'


def verified(data):
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise RuntimeError('Plugin checksum mismatch; no files installed')
    return data


def enable_auth(text):
    lines = text.splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith('sh3d.mcp.requireToken='):
            lines[i] = 'sh3d.mcp.requireToken=true'; found = True
    if not found:
        lines.append('sh3d.mcp.requireToken=true')
    return '\n'.join(lines) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--install-app', action='store_true', help='macOS only: brew install --cask sweet-home3d')
    p.add_argument('--apply', action='store_true', help='Without this, print plan only')
    p.add_argument('--plugins-dir', type=Path, default=plugin_dir())
    args = p.parse_args()
    target = args.plugins_dir / f'sh3d-mcp-plugin-{VERSION}.sh3p'
    print('App: Homebrew cask on macOS' if args.install_app else 'App: keep current installation')
    print(f'Plugin: {target}\nSource: {URL}\nSHA256: {SHA256}\nAuthentication: token required')
    if not args.apply:
        print('Dry run. Add --apply to perform installation.'); return
    if args.install_app:
        if platform.system() != 'Darwin':
            raise RuntimeError('Automatic app installation supports macOS only; use official installer on this OS')
        brew = shutil.which('brew')
        if not brew:
            raise RuntimeError('Homebrew is missing; install the app from the official vendor instead')
        if not Path('/Applications/Sweet Home 3D.app').exists():
            subprocess.run([brew, 'install', '--cask', 'sweet-home3d'], check=True)
    conflicts = [x for x in args.plugins_dir.glob('*mcp*.sh3p') if x.name != target.name]
    if conflicts:
        raise RuntimeError('Another MCP plugin exists; inspect versions before installing alongside it')
    if target.exists():
        data = verified(target.read_bytes())
    else:
        with urllib.request.urlopen(URL, timeout=60) as response:
            data = verified(response.read(10 * 1024 * 1024 + 1))
        # Validate archive before writing a plugin that will run on restart.
        with tempfile.TemporaryFile() as tmp:
            tmp.write(data); tmp.seek(0)
            with zipfile.ZipFile(tmp) as z:
                if 'ApplicationPlugin.properties' not in z.namelist():
                    raise RuntimeError('Not a Sweet Home 3D plugin archive')
    args.plugins_dir.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        fd, tmp = tempfile.mkstemp(dir=args.plugins_dir, suffix='.tmp')
        try:
            with os.fdopen(fd, 'wb') as f: f.write(data)
            os.replace(tmp, target)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    config = args.plugins_dir / 'sh3d-mcp.properties'
    old = config.read_text() if config.exists() else ''
    new = enable_auth(old)
    if old != new:
        if config.exists():
            backup = config.with_suffix('.properties.before-skill')
            if not backup.exists(): shutil.copy2(config, backup)
        config.write_text(new)
    print('Plugin ready. Save current work, then restart Sweet Home 3D using the UI.')
    print('After restart, run mcp_client.py health and tools. Token values are never printed.')


if __name__ == '__main__':
    try: main()
    except (RuntimeError, OSError, ValueError, zipfile.BadZipFile) as e: raise SystemExit(str(e))
