# vsk-world-manifest

The goal manifest for the V-Sekai world. `default.xml` is the one place that
says which repositories are in play and where each of them sits.

```
repo init -u https://github.com/V-Sekai/vsk-world-manifest.git -b main
repo sync
```

## Sides

Every repository sits on a side of the hexagon, and this manifest is what
decides which. There is **one live goal manifest** — this one. A repository is
placed when it is added to it, not later: an unplaced project is the drift the
six words exist to stop. `repo list` and the org's archived set are the two
things to read, and they disagree loudly when this rots.

| Side | Holds |
| --- | --- |
| `1-transport` | Driving adapters — the client and launcher, editor and viewer tools, XR and input managers, network and HTTP transports, Blender-side authoring addons. |
| `2-contract` | Manuals, specifications, formats and protocols. What the other sides agree to, written down. |
| `3-interactor` | Use cases and engine work — the Godot fork, IK and retargeting, mesh and cloth algorithms, importers and format conversion, ML. |
| `4-entities` | The domain objects themselves — avatars, maps, entity frameworks, and the demo and test projects that embody them. |
| `5-repository` | Persisted artifacts: model and asset stores. |
| `6-datasource` | Where data comes from — asset banks, corpora, casync seeds, databases and their drivers. |
| `7-service` | Backend services and everything that ships them: Uro, deployment, packaging, build orchestration. |

Local paths are normalised — lowercase, hyphenated, prefixes like `TOOL_` and
`V-Sekai.` dropped. **The GitHub names are untouched.** A `<project name=>` is
the repository as the org has it and a `<project path=>` is what it is called in
a checkout; renaming happens locally, in this file, and nowhere else.

**Every project carries an explicit `revision`.** V-Sekai's default branches are
not uniform — `master`, `godot3`, `godot-4.3`, `colliders`, `vsekai`, `flux2`,
`4.0` and others all appear — so the manifest names each one rather than letting
a `<default revision=>` decide silently. `<default>` sets the remote and the
job count only.

Archived repositories are not listed. Placement is what a live manifest says.

## The workspace root

Two files reach the root of a synced workspace from `2-contract/manuals-vsk`:

```xml
<linkfile src="CLAUDE.md" dest="CLAUDE.md" />
<linkfile src="CITATION.cff" dest="CITATION.cff" />
```

`CLAUDE.md` is the working agreements every project here is written against;
`CITATION.cff` names the record and its license. Both are links, never copies —
see the `check_manifest_root.py` note below for why. `AGENTS.md` sits beside
them in `manuals` and is deliberately **not** linked: it is guidance for working
inside that repository rather than across the workspace.

## Gates

Both fail the check run. Neither warns.

- `check_manifest_comments.py` — `default.xml` carries no XML comments. A
  comment beside an entry is a claim that nothing verifies and that outlives the
  entry it described. Ships with five negative controls.
- `check_manifest_root.py` — every `<linkfile>` resolves, and `<copyfile>` is
  blocked outright. A copy is re-made on `repo sync` and drifts silently in
  between; a symlink has no in-between state to lose. Needs a workspace, so CI
  runs its self-test only — the full run is
  `python check_manifest_root.py <workspace>` and it belongs on a desk.
- `check_pr_description.py` — the pull request body is read from the API, which
  is the same text the reviewer sees.
