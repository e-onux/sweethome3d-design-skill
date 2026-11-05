#!/usr/bin/env python3
"""Small authenticated loopback MCP client. Python 3.10+, standard library only."""
import argparse
import json
import os
from pathlib import Path
import platform
import urllib.request
import urllib.error


def plugin_dir():
    if platform.system() == 'Darwin':
        return Path.home() / 'Library/Application Support/eTeks/Sweet Home 3D/plugins'
    if platform.system() == 'Windows':
        base = os.environ.get('APPDATA')
        if not base:
            raise RuntimeError('APPDATA is not set')
        return Path(base) / 'eTeks/Sweet Home 3D/plugins'
    return Path.home() / '.eteks/sweethome3d/plugins'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Refusing MCP redirect')


class Client:
    def __init__(self, port=9877, token_file=None, timeout=30):
        if not 1 <= port <= 65535:
            raise ValueError('Invalid port')
        self.base = f'http://127.0.0.1:{port}'
        self.timeout = timeout
        self.token_file = Path(token_file) if token_file else plugin_dir() / 'sh3d-mcp.token'
        self.session = None
        self.counter = 0
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def health(self):
        with self.opener.open(self.base + '/health', timeout=self.timeout) as r:
            return json.load(r)

    def rpc(self, method, params=None, notification=False):
        payload = {'jsonrpc': '2.0', 'method': method, 'params': params or {}}
        if not notification:
            self.counter += 1
            payload['id'] = self.counter
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
        if self.token_file.is_file():
            headers['Authorization'] = 'Bearer ' + self.token_file.read_text().strip()
        if self.session:
            headers['Mcp-Session-Id'] = self.session
        request = urllib.request.Request(self.base + '/mcp', json.dumps(payload).encode(), headers)
        try:
            with self.opener.open(request, timeout=self.timeout) as r:
                if r.headers.get('Mcp-Session-Id'):
                    self.session = r.headers['Mcp-Session-Id']
                kind = r.headers.get('Content-Type', '')
                # Stop at our response if a server leaves an SSE stream open.
                if 'text/event-stream' in kind:
                    data = []
                    for line in r:
                        line = line.decode().rstrip('\r\n')
                        if line.startswith('data:'):
                            data.append(line[5:].lstrip())
                        elif not line and data:
                            event = json.loads('\n'.join(data)); data = []
                            if event.get('id') == payload.get('id'):
                                result = event; break
                    else:
                        raise RuntimeError('MCP stream ended without response')
                else:
                    body = r.read()
                    if notification and not body:
                        return None
                    result = json.loads(body)
        except urllib.error.HTTPError as exc:
            # Do not dump headers, bearer tokens, or server exception bodies.
            raise RuntimeError(f'MCP HTTP {exc.code}; check app, token and session') from None
        if 'error' in result:
            raise RuntimeError(f"MCP error {result['error'].get('code')}: {result['error'].get('message')}")
        return result.get('result')

    def initialize(self):
        result = self.rpc('initialize', {'protocolVersion': '2025-03-26', 'capabilities': {},
                          'clientInfo': {'name': 'sweethome3d-design-skill', 'version': '1.0.0'}})
        self.rpc('notifications/initialized', notification=True)
        return result

    def call(self, name, arguments):
        return self.rpc('tools/call', {'name': name, 'arguments': arguments})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', type=int, default=9877)
    p.add_argument('--token-file', type=Path)
    p.add_argument('--timeout', type=float, default=30)
    p.add_argument('--output', type=Path, help='Write full JSON; image base64 is omitted from console')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('health'); sub.add_parser('tools')
    c = sub.add_parser('call'); c.add_argument('name')
    g = c.add_mutually_exclusive_group()
    g.add_argument('--args', default=None, help='JSON object')
    g.add_argument('--args-file', type=Path, help='JSON object file, preferred for complex input')
    args = p.parse_args()
    client = Client(args.port, args.token_file, args.timeout)
    if args.command == 'health':
        result = client.health()
    else:
        client.initialize()
        if args.command == 'tools':
            result = client.rpc('tools/list')
        else:
            data = json.loads(args.args_file.read_text() if args.args_file else (args.args or '{}'))
            if not isinstance(data, dict):
                raise ValueError('Tool arguments must be a JSON object')
            result = client.call(args.name, data)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    display = json.loads(json.dumps(result))
    if isinstance(display, dict):
        for block in display.get('content', []):
            if block.get('type') in ('image', 'audio') and 'data' in block:
                block['data'] = '[omitted; use --output to save full JSON]'
    if args.output:
        print(json.dumps({'output': str(args.output), 'isError': bool(isinstance(result, dict) and result.get('isError'))}))
    else:
        print(json.dumps(display, indent=2, ensure_ascii=False))
    if isinstance(result, dict) and result.get('isError'):
        raise SystemExit(1)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError) as e:
        raise SystemExit(str(e))
