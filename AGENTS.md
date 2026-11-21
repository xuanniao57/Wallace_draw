# Wallace Draw maintenance

After completing a requested change to these scientific drawing skills, synchronize and publish it in the same task. The personal source is ~/.claude/skills and the discovery mirror is ~/.agents/skills. Use the indexed skills/ paths in this checkout to limit publication to the reviewed files.

1. Run `git status --short --branch` and fetch origin. Check divergent remote changes before publishing, and preserve unrelated local work.
2. Run `python scripts/sync_skills.py check`. Exit 0 means aligned, 1 means planned copies, and 2 means an unmanaged file or a conflict. Review newly added files in full. Copy intended additions into the corresponding checkout directory and use path-specific `git add`. For an intentional removal, reconcile the exact file in all three roots and the index. Preserve conflicting local edits before resolving them.
3. Run `python scripts/sync_skills.py apply`. Inspect the actual diff, validate the edited SKILL.md and rerun the affected renderer or example. If publication assets change, check the final-size image. Run `check` again.
4. Stage only the reviewed task paths, review the staged list, and commit. Push normally to `origin/main`; verify that `git rev-parse HEAD` matches `git ls-remote origin refs/heads/main`. Finish with the published commit or report the specific blocker. Reference links, package locks and reusable examples may be part of a skill. Keep credentials, manuscript inputs, local account paths, caches and machine configuration out of the public repo.
