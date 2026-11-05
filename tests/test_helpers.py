import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/sweethome3d-design/scripts'
sys.path.insert(0, str(SCRIPTS))
from mcp_client import Client
spec = importlib.util.spec_from_file_location('skill_setup', SCRIPTS / 'setup.py')
setup = importlib.util.module_from_spec(spec); spec.loader.exec_module(setup)


class Handler(BaseHTTPRequestHandler):
    calls = []
    def log_message(self, *a): pass
    def do_POST(self):
        p = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.calls.append(p['method'])
        if self.headers.get('Authorization') != 'Bearer test-secret':
            self.send_error(401); return
        if p['method'] != 'initialize' and self.headers.get('Mcp-Session-Id') != 'test-session':
            self.send_error(400); return
        if p['method'] == 'notifications/initialized':
            self.send_response(202); self.end_headers(); return
        result = {'ok': True}
        if p['method'] == 'tools/call' and p['params']['name'] == 'failure':
            result = {'isError': True, 'content': [{'type': 'text', 'text': 'Expected error'}]}
        data = json.dumps({'jsonrpc': '2.0', 'id': p['id'], 'result': result})
        self.send_response(200)
        self.send_header('Mcp-Session-Id', 'test-session')
        sse = p['method'] == 'tools/call'
        self.send_header('Content-Type', 'text/event-stream' if sse else 'application/json')
        self.end_headers()
        self.wfile.write((f'data: {data}\n\n' if sse else data).encode())


class Helpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()
    def client(self, folder, secret='test-secret'):
        token = Path(folder) / 'token'; token.write_text(secret)
        return Client(self.server.server_port, token, timeout=2)
    def test_session_and_sse(self):
        with tempfile.TemporaryDirectory() as d:
            c = self.client(d); c.initialize()
            self.assertEqual(c.session, 'test-session')
            self.assertEqual(c.call('get_state', {}), {'ok': True})
    def test_failure_not_retried(self):
        with tempfile.TemporaryDirectory() as d:
            c = self.client(d); c.initialize(); start = len(Handler.calls)
            self.assertTrue(c.call('failure', {})['isError'])
            self.assertEqual(Handler.calls[start:], ['tools/call'])
    def test_auth_error_redacted(self):
        with tempfile.TemporaryDirectory() as d:
            c = self.client(d, 'wrong-secret')
            with self.assertRaisesRegex(RuntimeError, 'HTTP 401') as e: c.initialize()
            self.assertNotIn('wrong-secret', str(e.exception))
    def test_checksum_rejects_corrupt_download(self):
        with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'): setup.verified(b'corrupt')
    def test_config_idempotent_preserves_other_settings(self):
        original = '# local\nport=9999\nsh3d.mcp.requireToken=false\n'
        updated = setup.enable_auth(original)
        self.assertIn('port=9999', updated)
        self.assertIn('sh3d.mcp.requireToken=true', updated)
        self.assertEqual(updated, setup.enable_auth(updated))
    def test_dry_run_has_no_filesystem_side_effects(self):
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'not-created'
            subprocess.run([sys.executable, str(SCRIPTS / 'setup.py'), '--plugins-dir', str(target)],
                           capture_output=True, check=True)
            self.assertFalse(target.exists())


if __name__ == '__main__': unittest.main()
