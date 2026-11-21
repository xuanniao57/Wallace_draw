"""Reconcile reviewed skill files in the checkout, canonical tree and discovery mirror."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
ROOTS = [REPO / "skills", Path.home() / ".claude/skills", Path.home() / ".agents/skills"]


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args])


def read(path):
    if path.is_symlink():
        raise ValueError(f"Refusing a symbolic link at {path}")
    return path.read_bytes() if path.is_file() else None


def digest(data):
    if data is None:
        return None
    # Git normalizes text line endings at checkout. Keep binary content exact.
    if b"\x00" not in data:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        handle.write(data)
    try:
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def sync(mode):
    gitdir = Path(os.fsdecode(git("rev-parse", "--absolute-git-dir").strip()))
    state_path = gitdir / "wallace-skill-baseline.json"
    # Serialize simultaneous mirror updates; the OS releases the lock on exit.
    with (gitdir / "wallace-skill-sync.lock").open("a+b") as lock:
        if os.name == "nt":
            import msvcrt
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return reconcile(mode, state_path)


def reconcile(mode, state_path):
    prior = json.loads(state_path.read_text("utf-8")) if state_path.exists() else {}
    tracked = git("ls-files", "-z", "--", "skills/").decode("utf-8").split("\0")
    baseline = {}
    actions = []
    issues = []
    seen = set()
    for entry in filter(None, tracked):
        rel = Path(entry).relative_to("skills")
        key = rel.as_posix()
        seen.add(key)
        paths = [root / rel for root in ROOTS]
        if any(not p.resolve().is_relative_to(root.resolve()) for p, root in zip(paths, ROOTS)):
            raise ValueError(f"Path escapes its skills root: {rel}")
        data = [read(p) for p in paths]
        hashes = [digest(d) for d in data]
        if key not in prior:
            if hashes[0] is None or any(h not in (None, hashes[0]) for h in hashes):
                issues.append(f"New file conflicts with installed content: {rel}")
                continue
            source = 0
        else:
            changes = {h for h in hashes if h != prior[key]}
            if len(changes) > 1 or None in hashes:
                issues.append(f"Conflicting edits or deletion; reconcile explicitly: {rel}")
                continue
            source = hashes.index(changes.pop()) if changes else 0
        baseline[key] = hashes[source]
        for i, h in enumerate(hashes):
            if h != hashes[source]:
                actions.append((paths[i], data[source], h))
    for key in prior.keys() - seen:
        if any((root / key).exists() for root in ROOTS):
            issues.append(f"Untracked former file still exists; review removal: {key}")
    if not seen:
        issues.append("No Git-indexed skill files in this checkout")
    # Only indexed files can be copied; announce new local resources for review.
    for name in sorted({Path(k).parts[0] for k in seen}):
        for root in ROOTS:
            for folder, dirs, files in os.walk(root / name):
                dirs[:] = [d for d in dirs if d not in {"node_modules", "__pycache__", ".git", "rendered"}]
                for file in files:
                    p = Path(folder) / file
                    if p.relative_to(root).as_posix() not in seen and not file.endswith(".pyc"):
                        issues.append(f"Unmanaged file, review before adding to Git or relocating: {p}")
    for issue in issues:
        print(issue, file=sys.stderr)
    if issues:
        return 2
    for path, _, _ in actions:
        print(f"Update {path}")
    if mode == "apply":
        for path, data, old in actions:
            if digest(read(path)) != old:
                raise ValueError(f"Content changed during sync: {path}")
            atomic_write(path, data)
        atomic_write(state_path, json.dumps(baseline, sort_keys=True, indent=2).encode())
    print(f"{len(seen)} managed files; {len(actions)} copies " +
          ("written" if mode == "apply" else "pending"))
    return int(mode == "check" and bool(actions))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["check", "apply"])
    sys.exit(sync(parser.parse_args().mode))
