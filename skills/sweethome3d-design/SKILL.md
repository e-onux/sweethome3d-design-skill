---
name: sweethome3d-design
description: Install Sweet Home 3D with its local MCP plugin, then create or edit editable home and interior models from dimensions, floor plans, or room photographs. Use for Sweet Home 3D setup, attic rooms, window and furniture placement, model corrections, and saved .sh3d delivery.
---

# Sweet Home 3D design

Deliver an editable .sh3d model, verified in the actual desktop application. Prefer the installed Sweet Home 3D MCP tools. If the current chat has no registered tools, the bundled Python client can call the same local MCP endpoint without changing the user's assistant configuration.

## Setup or connection repair

Read [references/setup.md](references/setup.md). Inspect the existing app, plugin and current open model before installing or restarting. Preserve unsaved work. The setup helper prints a plan unless `--apply` is specified. It downloads a pinned upstream release with a pinned SHA256, enables local token authentication and preserves unrelated settings. It does not restart apps or register a new Codex server automatically.

```sh
python3 scripts/setup.py --install-app
python3 scripts/setup.py --install-app --apply
python3 scripts/mcp_client.py health
python3 scripts/mcp_client.py tools
```

Run paths relative to this skill directory or use absolute paths. Inspect the returned live tool schemas; do not invent tool names, catalog IDs or properties. The MCP service exists only while the desktop app is running. Do not upload room photographs to a remote modeling service unless the user requests that destination.

## Modeling

Read [references/modeling.md](references/modeling.md) for sloped ceilings, coordinate conversions, custom models and save verification.

1. For an existing model, call `get_state`, save a recoverable file or snapshot, and call `checkpoint` before a change block. Do not reload a disk copy over live edits without inspecting their difference.
2. Establish one coordinate frame in centimeters: X right, Y front to back, Z above floor. Record the origin and which wall the user calls front, back, left and right. Keep a concise project measurement note, distinguishing measurements from photo estimates.
3. Use the newest explicit measurements. Ask about genuinely unresolved reference points while progressing on independent geometry. A slope length and its horizontal projection are different measurements. Do not sum them as collinear distances or silently distort the whole room to fit a local opening.
4. Build native connected walls, floors and wall windows first. Browse catalog categories and IDs before placing furniture. Use custom shapes only where native tools cannot express the requested geometry. Custom architectural pieces should be separate from movable furniture and independent door leaves.
5. Infer furniture positions and colors from photographs, but label estimated dimensions. Include principal visible items, retain known rug or furniture dimensions, and check passage widths, collisions and objects protruding through the ceiling.
6. Make corrections narrowly. If the user reports accidental movement, compare every object's ID, position, rotation, size and elevation against the last accepted snapshot. Restore only accidental changes. Lock the base plan when useful and verify the lock in the application, not just in an XML flag.
7. Compare final state to intended measurements and inspect at least the useful interior views in the app. A successful API call alone is not visual verification. Save viewpoints for both sides of the room if useful.
8. Save to the user's project directory, then verify a reopened or isolated copy preserves geometry, materials and assets. Do not replace the live scene with a verification copy while the user is editing. Leave the accepted model open. Give a spoken notification only when requested and after the intended model is visible.

Prefer targeted tools over rebuilding the full file for every correction. Before large or destructive tool calls, read state and preserve a recoverable copy. Never automatically retry a timed-out mutation: read state to determine whether it already completed.

## Delivery

Report what changed, the saved model location, and remaining estimates. Do not call an estimated photo reconstruction exact. Keep credentials, authentication files, personal photographs and private home models out of a skill repository. Follow the user's project-root and writing conventions when present.
