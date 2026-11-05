# Geometry and editable model reliability

## Measurements and directions

Keep the room outline, wall centerlines, wall thickness and clear interior dimensions distinct. An offset is to the opening edge unless the user explicitly says center. For a wall running along Y from front 0 to back L, a window with width w starting d from the back has center `Y = L - d - w/2`. For a horizontal front wall, windows starting at a from the left with widths w and gap g occupy `[a,a+w]` and `[a+w+g,a+2*w+g]`.

For an attic with front low height h0, flat ceiling h1 and slope horizontal run R, `height(y) = h0 + (h1-h0)*y/R` inside the sloped segment. A roof window of length s along that surface has plan depth `s / sqrt(1 + ((h1-h0)/R)^2)`. State whether the supplied length describes the glass, frame or reveal when it matters. Preserve unknown sill positions as estimates rather than inventing a measured height.

A local opening may have an upper contour different from the main roof. If the floor width is W, the horizontal top portion is A and the inclined portion is S, its remaining horizontal run is B=W-A and its drop is `sqrt(S*S-B*B)`, provided `0 <= B <= S`. Example: W=180, A=150, S=50 gives B=30 and drop=40. This can imply a local soffit. Explain that inferred contour rather than silently changing the room's main slope. If physical interpretation remains unclear, ask a focused question.

When heights change, also inspect pendant suspension lengths, ceiling fixtures, curtains, tall cupboards and window tops. Preserve accepted furniture placement except where the new geometry causes a collision.

## Tools and custom assets

Use live `tools/list` schemas. Native MCP tools expose coordinates in centimeters and angles in degrees. Native Home.xml angle fields use radians. Wavefront OBJ uses X horizontal, Y vertical and Z depth; MCP mesh vertices use X/Y plan coordinates and Z height. Do not mix them.

Prefer native `place_door_or_window` for vertical wall openings. A roof window requires a genuine hole in the roof mesh plus frame/glass, not a blue rectangle pasted on an opaque roof. Use separate editable architectural objects and separate furniture objects. Avoid grouping the roof, doorway and all lintels into one piece: accidental movement then displaces unrelated geometry.

Two-sided roof visibility must be checked from inside and outside. Correct winding or explicit double-sided geometry is more dependable than guessing the effect of a back-face setting. Shared vertices and manifold solids are preferable when custom meshes require reliable normals or ray tracing.

## File save and materials

Native application saves are preferred, but verify their actual output. In the tested plugin/app combination, loading a hand-written ZIP with OBJ files and sibling MTL files could display correctly from the loaded cache, while a later native save stored numbered OBJ entries without the sibling MTL files. A currently colored viewport is therefore not proof that the saved model is portable.

Use imported multi-file model bundles or native generated shapes when possible. Audit each model reference and its OBJ `mtllib` / MTL texture dependencies in the output ZIP. Validate a saved copy in an isolated application session or after ensuring no concurrent edits. Do not overwrite a known-good colored artifact with a native save that lost dependencies. Preserve the original and repair a working copy using the authoritative XML and all referenced assets. A package with both serialized `Home` and `Home.xml` can have competing representations; do not edit only XML while retaining stale serialized state and assume every reader will prefer it.

When editing XML-only .sh3d packages, use XML parsing and ZIP libraries, preserve existing referenced assets and write atomically through a temporary file. Check the upstream format and loader behavior instead of treating an archive that merely opens through one MCP tool as universally validated.

## Acceptance

- Compare stored and live IDs, X/Y, elevation, angle, width/depth/height and wall endpoints.
- Check the actual user-requested invariants: opening widths and offsets, roof-window gap, ceiling height, floor-level window elevation, and latest door alignment.
- Check furniture/door clearance, clipping and ceiling collisions in useful interior views.
- Verify saved assets and reopen a safe copy. Separate API-state verification, UI verification and saved-file verification in the report; state any verification that could not be completed.
- Keep a recoverable snapshot before updates. If the user moves an object while the agent works, re-read state before saving and reconcile only the authorized correction.
