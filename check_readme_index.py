# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Gate: the readme does not index the manifest. `default.xml` says what is placed where and
the readme says the rules, so no block of the readme enumerates sides or projects.

WHY THIS EXISTS. The readme carried a `## Sides` table: seven rows, one per side directory,
each with a sentence about what that side holds. Every row was derived from `default.xml`
and none of it was checked, so every change to the layout needed a second edit in a second
file, and a reader who found only one of the two had no way to tell which was current. The
anchor that table published, `#sides`, is the shape of the problem rather than an aside: it
invited other documents to cite the copy instead of the source.

That failure has a name here already. It is the manifest comment, the blocked `<copyfile>`
and the submodule blocklist again - a fact in a second place, visible to nothing that
checks. An index is the largest version of it, because it restates the one file in this
repository whose whole job is to be machine-read.

WHY NOT GENERATE THE INDEX INSTEAD. Because that is tooling nobody has written, and a
generator is a thing to maintain, run and check in its own right. Until it exists the honest
arrangement is no index at all, and a reader is sent to `default.xml`, which is short,
sorted, and cannot be out of date with itself. The rule is written so that a later generator
is a change to this gate rather than an argument with it.

WHAT COUNTS AS AN INDEX. Any single block naming three or more distinct things the manifest
declares - a side directory, a `<project name=>`, or a `<project path=>`. The vocabulary is
read out of `default.xml` at run time rather than listed here, because a gate that hardcoded
the seven side names would be an index of the manifest sitting inside the check against
indexes of the manifest.

THREE, AND WHY NOT TWO OR FOUR. Two names is a comparison - `godot_openvr` beside
`godot_openvr_module` is the argument for the suffix rule, and prose that cannot show a pair
cannot make a point. Three is where a listing stops illustrating and starts enumerating, and
enumeration is what has to be re-edited when the layout moves. The number is stated here so
that a reader can disagree with it.

MEASURED PER BLOCK, AT EVERY DEPTH. Tables, lists, headings and paragraphs alike. Prose that
names three projects in three sentences needs exactly the hand edit a table of three rows
does, and exempting it would leave the rule enforcing a formatting preference rather than the
thing it is about. Every container block is measured rather than only the top-level ones, so
an index nested inside a list item fails with the list that holds it.

WHAT IS NOT MEASURED, NAMED RATHER THAN OMITTED. Fenced and indented code blocks. They carry
the `repo init` line and other commands, which are copied and run rather than read as a
listing, and a command that names a path is not claiming to describe the layout.

DETECTION FLOOR. None: every block of the file is enumerated and counted, and the largest
count is printed beside the limit whether or not anything failed. One shape is out of reach
and is named rather than left to be discovered - two adjacent paragraphs of two names each
are four names that no single block holds, so a determined author can still spread an index
across blocks. What this catches is the shape people actually write, which is the table.

An unparseable manifest is a FAIL and never a skip. Without it there is no vocabulary, and a
check with an empty vocabulary passes everything it is given.

Run:  python check_readme_index.py [readme ...] [--manifest PATH] [--self-test]
"""

import argparse
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

try:
    from markdown_it import MarkdownIt
except ImportError:  # reported as a FAIL by main(), never as a clean run
    MarkdownIt = None

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE / "default.xml"
DEFAULT_README = HERE / "readme.md"

MAX_NAMES_PER_BLOCK = 2  # three is an enumeration; see the docstring for the argument

# A token is a bare word or a slashed path. Matching is whole-token and case-sensitive, so
# `Godot` the English word is not the project `godot`, and neither is `godot-cpp`.
TOKEN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./+-]*")
SIDE = re.compile(r"^\d-[a-z]+$")


def vocabulary(manifest):
    """Every name the manifest declares: project names, project paths, side directories.

    Read rather than listed. A hardcoded copy of the seven sides would be the very thing this
    gate rejects, one file further in.
    """
    root = ET.parse(manifest).getroot()
    names, sides = set(), set()
    for project in root.iter("project"):
        name = project.get("name")
        path = project.get("path") or name
        if name:
            names.add(name)
        if path:
            names.add(path.rstrip("/"))
            head = path.split("/")[0]
            if SIDE.match(head):
                sides.add(head)
    if not names:
        raise ValueError("declares no projects, so the vocabulary would be empty")
    return names | sides, sides


def code_lines(tokens):
    """Line numbers inside fenced or indented code, which are copied rather than read."""
    out = set()
    for token in tokens:
        if token.type in ("fence", "code_block") and token.map:
            out.update(range(*token.map))
    return out


def blocks(text):
    """(kind, span) for every container block at every depth, in document order.

    A block's own parts are dropped - list items, table bodies and rows - so that one index
    is reported once rather than once per row of itself. Nesting between blocks is still
    reached: a list's span covers its items, and a table inside an item is measured on its
    own span as well as within the list's.
    """
    parts = {"list_item_open", "thead_open", "tbody_open", "tr_open", "th_open", "td_open"}
    tokens = MarkdownIt("commonmark").enable("table").parse(text)
    found = [(t.type[:-5], t.map) for t in tokens
             if t.type.endswith("_open") and t.map and t.type not in parts]
    return found, code_lines(tokens)


def names_in(text, span, skip, vocab):
    """Distinct manifest names on a block's lines, ignoring lines inside code."""
    lines = text.splitlines()
    hits = {}
    for n in range(*span):
        if n in skip or n >= len(lines):
            continue
        for match in TOKEN.finditer(lines[n]):
            token = match.group(0).rstrip(".,;:")
            if token in vocab:
                hits.setdefault(token, n + 1)
    return hits


def check(readmes, manifest, verbose=True):
    """0 when no block of any readme indexes the manifest. Every failure prints a line."""
    if MarkdownIt is None:
        print("  FAIL markdown-it-py is not installed, so nothing was parsed. An unmet "
              "precondition is a failure, never a skip.")
        return 1
    if not readmes:
        print("  FAIL no readme given and none found. A gate over nothing certifies nothing.")
        return 1

    try:
        vocab, sides = vocabulary(manifest)
    except (ET.ParseError, ValueError, OSError) as exc:
        print(f"  FAIL {pathlib.Path(manifest).name}: no vocabulary could be read ({exc}). "
              f"A check with an empty vocabulary passes everything.")
        return 1

    failures = []
    for path in readmes:
        if not path.exists():
            failures.append(f"{path}: does not exist")
            continue
        text = path.read_text(encoding="utf-8")
        found, skip = blocks(text)

        worst, offenders = 0, []
        for kind, span in found:
            hits = names_in(text, span, skip, vocab)
            worst = max(worst, len(hits))
            if len(hits) > MAX_NAMES_PER_BLOCK:
                listed = ", ".join(sorted(hits)[:6])
                more = "" if len(hits) <= 6 else f", and {len(hits) - 6} more"
                offenders.append(f"{path.name}:{span[0] + 1}: this {kind} names {len(hits)} "
                                 f"things the manifest declares ({listed}{more})")

        if offenders:
            failures.extend(offenders)
            failures.append(
                f"{path.name}: at most {MAX_NAMES_PER_BLOCK} per block. Send the reader to "
                f"default.xml, which is sorted, short, and cannot be out of date with itself.")
        elif verbose:
            print(f"  ok   {path.name}: {len(found)} blocks enumerated against {len(vocab)} "
                  f"names and {len(sides)} sides, largest block names {worst} "
                  f"(at most {MAX_NAMES_PER_BLOCK})")

    for failure in failures:
        print(f"  FAIL {failure}")
    return 1 if failures else 0


# --- negative controls ------------------------------------------------------------------
#
# The readme passing proves the readme is clean. It does not prove this would notice one
# that is not, which is the only claim worth making. Six must fail and three must pass, and
# the first of the six is the table this gate was written to remove.


SIDES_TABLE = """# vsk-world-manifest

## Sides

| Side | Holds |
| --- | --- |
| `1-transport` | Driving adapters. |
| `2-contract` | What the other sides agree to. |
| `3-interactor` | Use cases and engine work. |
| `4-entities` | Avatars, maps, entity frameworks. |
| `5-repository` | Persisted artifacts. |
| `6-datasource` | Where data comes from. |
| `7-service` | Backend services. |
"""

MANIFEST = """<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <remote name="v-sekai" fetch="https://github.com/V-Sekai" />
  <default remote="v-sekai" sync-j="16" />
  <project name="manuals" path="2-contract/manuals-vsk" revision="main" />
  <project name="godot" path="3-interactor/godot" revision="master" />
  <project name="godot_openvr" path="1-transport/godot-openvr-gdextension" revision="master" />
  <project name="godot_openvr_module" path="1-transport/godot-openvr-module" revision="master-rd" />
  <project name="uro" path="7-service/uro" revision="master" />
</manifest>
"""


def self_test():
    import contextlib
    import io
    import tempfile

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="readme-gate-"))
    manifest = tmp / "default.xml"
    manifest.write_text(MANIFEST, encoding="utf-8")
    broken = tmp / "broken.xml"
    broken.write_text(MANIFEST.replace("</manifest>", ""), encoding="utf-8")

    cases = [
        ("the sides table this gate removed", False, SIDES_TABLE, manifest),
        ("a bullet list of three paths", False,
         "# r\n\n- `1-transport/godot-openvr-gdextension`\n- `7-service/uro`\n"
         "- `3-interactor/godot`\n", manifest),
        # Prose is measured too. A rule that only read tables would enforce a formatting
        # preference rather than the thing it is about, and this is the case that says so.
        ("a paragraph naming three projects", False,
         "# r\n\nThe fork is godot, the service is uro, and the manuals live at\n"
         "2-contract/manuals-vsk.\n", manifest),
        # Top-level-only measurement would wave this through, which is why nesting has its
        # own control rather than a sentence in the docstring.
        ("an index nested inside a list item", False,
         "# r\n\n- placed so far:\n\n  | Side | Holds |\n  | --- | --- |\n"
         "  | `1-transport` | adapters |\n  | `3-interactor` | engine work |\n"
         "  | `7-service` | services |\n", manifest),
        ("a heading that is itself a listing", False,
         "# r\n\n## 1-transport, 3-interactor and 7-service\n\nProse.\n", manifest),
        # Without a vocabulary every readme passes, so the unparseable manifest must fail
        # here rather than be skipped.
        ("a manifest that does not parse", False, SIDES_TABLE.replace("## Sides", "## R"),
         broken),
        ("a pair, which is a comparison rather than a listing", True,
         "# r\n\n`godot_openvr` and `godot_openvr_module` are one feature written both\n"
         "ways, and the suffix is what says so.\n", manifest),
        # The exemption, stated as a control so that it is a decision rather than a hole.
        ("paths inside a fenced command", True,
         "# r\n\n```\nrepo sync 1-transport/godot-openvr-gdextension 7-service/uro \\\n"
         "  3-interactor/godot\n```\n", manifest),
        ("a readme that names nothing the manifest declares", True,
         "# r\n\nThe rules live here and the placements live in the manifest.\n\n"
         "| Suffix | Means |\n| --- | --- |\n| `-module` | compiled in |\n"
         "| `-gdextension` | loaded at runtime |\n", manifest),
    ]

    print("controls:")
    bad = []
    for i, (label, should_pass, text, xml) in enumerate(cases):
        # A distinct filename per case. Reusing one would hand a case its predecessor's
        # file, which is how a control ends up firing for somebody else's defect.
        dst = tmp / f"case{i}.md"
        dst.write_text(text, encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check([dst], xml)
        first = next((ln.strip() for ln in buf.getvalue().splitlines() if "FAIL" in ln), "")
        passed = rc == 0
        if passed == should_pass:
            print(f"  ok   {label}: " + ("passes, correctly" if passed
                                         else f"fails: {first[:92]}"))
        else:
            print(f"  BAD  {label}: " + ("passed and should not have" if passed
                                         else f"failed and should not have: {first[:66]}"))
            bad.append(label)
        dst.unlink()

    if bad:
        print(f"\n{len(bad)} control(s) wrong. The gate is decoration until they are not.")
        return 1
    print(f"\nAll {len(cases)} controls behaved.")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("readmes", nargs="*", help="markdown files to check")
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST),
                    help="the manifest the vocabulary is read from")
    ap.add_argument("--self-test", action="store_true",
                    help="run the negative controls")
    args = ap.parse_args(argv[1:])

    rc = 0
    if args.readmes or not args.self_test:
        paths = [pathlib.Path(r) for r in args.readmes] or (
            [DEFAULT_README] if DEFAULT_README.exists() else [])
        rc = check(paths, args.manifest)
    if args.self_test:
        if rc or args.readmes:
            print()
        rc |= self_test()
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
