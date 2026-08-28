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

**A path says how the engine loads it.** Two things that both read as "a Godot
C++ project" are built and shipped in ways that share nothing: an engine module
is `config.py` and `SCsub` dropped into `godot/modules/` and compiled into the
binary, and a GDExtension is `godot-cpp` and a `.gdextension` file loaded by a
stock binary at runtime. Which one a repository is decides whether a change to
it needs an engine rebuild, so the path carries it:

| Suffix | Means | Look for |
| --- | --- | --- |
| `-module` | Godot engine C++ module | `config.py` + `SCsub` at the repo root, `register_types.cpp` |
| `-gdextension` | Godot GDExtension | `godot-cpp` checkout, a `*.gdextension` file |
| neither | Not a thing the engine compiles in or loads | GDScript addon, standalone library, service, asset bank, and any repository that is itself a Godot project |

`godot_openvr` and `godot_openvr_module` are the same feature written both ways,
and `godot-motion-matching` and `godot_motion_matching` likewise; without the
suffix the two checkouts sit side by side saying nothing about the difference.
The engine forks themselves — `3-interactor/godot`, `world-godot`, `world-grid`
— take no suffix: they are what modules are built into.

A `project.godot` at the root outranks both suffixes. `3-interactor/sketch`
builds the cassie GDExtension and carries a Godot project that loads it, and
the project is what somebody opens, so it is placed as one. A repository with
no project of its own is what the suffixes are for.

One repository is genuinely both. `godot-wasm` ships a module build and a
GDExtension build of the same source, and its readme calls the addon the normal
install, so it is placed at `godot-wasm-gdextension`. The module build is still
there in the checkout.

**Every project carries an explicit `revision`.** V-Sekai's default branches are
not uniform — `master`, `godot3`, `godot-4.3`, `colliders`, `vsekai`, `flux2`,
`4.0` and others all appear — so the manifest names each one rather than letting
a `<default revision=>` decide silently. `<default>` sets the remote and the
job count only.

Archived repositories are not listed. Placement is what a live manifest says.

**Private repositories are not listed either.** This manifest is public, and a
`<project>` nobody outside the organisation can fetch fails their `repo sync`
at a line they cannot read or fix. Two are private today, `v-sekai-design` and
`godot-avatar-project`, and neither appears above. That makes the drift check
`repo list` against the org's **public** non-archived set.

## Gates

Each fails the check run. None warns.

- `check_manifest_comments.py` — `default.xml` carries no XML comments.
- `check_manifest_root.py` — every `<linkfile>` resolves; `<copyfile>` is
  blocked. Needs a workspace, so CI runs its self-test only; the full run is
  `python check_manifest_root.py <workspace>`.
- `check_pr_description.py` — the pull request body must say what changed.
