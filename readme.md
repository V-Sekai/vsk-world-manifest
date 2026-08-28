# vsk-world-manifest

V-Sekai is spread across roughly two hundred GitHub repositories. This one
lists them, so you can check out all of them at once and keep them updated
together, instead of cloning them one at a time.

## Requirements

Git, Python 3, and Google's [`repo`](https://gerrit.googlesource.com/git-repo)
tool. `repo` is a single Python script you put on your `PATH`:

```
mkdir -p ~/bin
curl -o ~/bin/repo https://storage.googleapis.com/git-repo-downloads/repo
chmod a+x ~/bin/repo
```

On Windows, run that from Git Bash. Some package managers ship `repo` as well.

## Get a workspace

```
mkdir vsk-world && cd vsk-world
repo init -u https://github.com/V-Sekai/vsk-world-manifest.git -b main
repo sync
```

Expect a large download and a long first run. What you end up with is one
folder per repository, grouped into seven numbered directories by what the code
does — the game client and its tools, the engine work, the avatars and maps,
the backend services.

## Work in it

Run these from the top of the workspace.

| Command | What it does |
| --- | --- |
| `repo sync` | Pull the latest of everything |
| `repo status` | Show your uncommitted work across every repository |
| `repo start <branch> <project>` | Start a branch in one repository |
| `repo list` | Show every repository and its folder |

Inside any folder, it is an ordinary git checkout: `git commit`, `git push`,
and open a pull request against that repository as usual.

## Change what is listed

Adding, moving, or removing a repository is an edit to `default.xml` in this
repository, followed by a pull request. Before you open it, run the checks:

```
python check_manifest_comments.py default.xml
python check_readme_index.py readme.md
python check_manifest_root.py <path to your workspace>
```

Each check explains itself when it fails, and each one's docstring says why the
rule exists.
