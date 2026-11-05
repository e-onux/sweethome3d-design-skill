# Installation and MCP connection

Tested baseline: macOS, Homebrew Sweet Home 3D 7.6.1, grimashevich MCP plugin 1.2.0, Python 3.10+. App versions from Homebrew may change. The app and plugin are separate upstream projects; this skill does not redistribute their binaries.

- Official app: https://www.sweethome3d.com/download/
- Upstream plugin: https://github.com/grimashevich/sweethome3d-mcp-server
- Pinned plugin release: https://github.com/grimashevich/sweethome3d-mcp-server/releases/tag/v1.2.0

## Install

On macOS with Homebrew, `python3 scripts/setup.py --install-app --apply` installs the app if absent, verifies the plugin checksum and copies the plugin to the standard folder. Without `--apply`, nothing changes. Without `--install-app`, the helper installs only the plugin.

On Windows or Linux, install Sweet Home 3D from the official vendor first, then use `python3 scripts/setup.py --apply`. Automatic app installation is implemented only for macOS. Those other operating systems are not live-tested by this repository.

Standard plugin folders:

- macOS: `~/Library/Application Support/eTeks/Sweet Home 3D/plugins/`
- Windows: `%APPDATA%/eTeks/Sweet Home 3D/plugins/`
- Linux: `~/.eteks/sweethome3d/plugins/`

Save open work before restarting through the available desktop UI tool. The Mac App Store build may lack permission to open a listening socket; use the official standalone build when affected. Wait for the app's actual startup state; onboarding screens can delay the main window. Verify `/health`, initialize MCP, then list tools. A health response alone does not prove that authenticated tool calls work.

## Client

The service listens on `http://127.0.0.1:9877/mcp`. The helper reads `sh3d-mcp.token` from the plugin folder (or `--token-file`), initializes a fresh in-memory session, sends the initialized notification and uses the returned session header. It supports JSON and SSE responses, never forwards bearer headers through redirects, and does not automatically repeat a mutation.

```sh
python3 scripts/mcp_client.py health
python3 scripts/mcp_client.py --output work/tools.json tools
python3 scripts/mcp_client.py call get_state
python3 scripts/mcp_client.py call checkpoint --args '{"description":"Before room changes"}'
python3 scripts/mcp_client.py call create_wall --args-file work/wall.json
```

Use `--output` for full responses with image data. Prefer render `filePath` arguments to receiving large base64 blocks. Tool errors cause a nonzero exit status. For a timeout, check state before retrying; rendering can still be active after the client exits. Use a small low-quality preview first, then request larger renders when justified.

Optional persistent Codex registration uses the documented `codex mcp add NAME --url URL` route. Token-enabled servers require current supported authentication configuration. Consult current official Codex MCP docs before changing user configuration; do not paste token values into a repository or disable authentication to simplify registration. This skill works through the local helper without persistent registration.

Official Codex MCP setup reference: https://developers.openai.com/learn/docs-mcp

## Troubleshooting

- Connection refused: app not started, plugin not loaded, wrong port, or unsupported sandboxed build.
- HTTP 401: wrong/missing token, token rotation, or another plugin directory.
- HTTP 400 after a successful initialize: missing session header or missing initialized notification. Use the bundled client rather than standalone requests without session tracking.
- Different plugin version already present: inspect it; do not install duplicate server plugins on the same port.
- Do not terminate an app to repair a connection until current work is saved. Never claim installation or restart succeeded without checking the app and endpoint.
