# Sweet Home 3D Design Skill

A reusable Codex skill for installing Sweet Home 3D with a local authenticated MCP plugin and creating editable home interiors from measurements, plans and photographs. Includes attic geometry, roof windows, furniture placement and recovery from accidental movement.

## Install the skill

Copy `skills/sweethome3d-design` into your Codex skills directory, normally `~/.codex/skills/`. The skill is available on your next turn. Invoke it with `$sweethome3d-design` or ask for a Sweet Home 3D model.

Using Codex's skill-installer helper, install from this repository with path `skills/sweethome3d-design`.

## Set up the application

Python 3.10+ is required. From the skill directory:

```sh
python3 scripts/setup.py --install-app
python3 scripts/setup.py --install-app --apply
python3 scripts/mcp_client.py health
python3 scripts/mcp_client.py tools
```

The first command is a dry run. Automatic application installation requires macOS and an existing Homebrew installation. Plugin installation also supports standard Windows and Linux paths, but those platforms have not been live-tested. Save current work before restarting the app. The helper never restarts it or changes Codex MCP configuration.

The plugin is pinned to upstream v1.2.0 with a verified SHA256. Authentication is enabled locally. Token files remain outside this repository. Read [setup details](skills/sweethome3d-design/references/setup.md) and [modeling guidance](skills/sweethome3d-design/references/modeling.md).

## Validation

```sh
python3 -m unittest discover -s tests -v
python3 skills/sweethome3d-design/scripts/setup.py
python3 skills/sweethome3d-design/scripts/mcp_client.py health
python3 skills/sweethome3d-design/scripts/mcp_client.py tools
```

Unit tests use a fake local MCP server and do not edit an open home. Read-only live checks were performed against the installed application. This repository contains no private room photos, home models, tokens or copied upstream binaries.

## Sources and ownership

- [Sweet Home 3D official downloads](https://www.sweethome3d.com/download/)
- [Sweet Home 3D MCP plugin](https://github.com/grimashevich/sweethome3d-mcp-server), GPL-2.0, installed separately
- [Official Codex MCP setup](https://developers.openai.com/learn/docs-mcp)

This repository supplies original instructions and helper scripts, not Sweet Home 3D or the upstream MCP plugin. No upstream affiliation is implied.
