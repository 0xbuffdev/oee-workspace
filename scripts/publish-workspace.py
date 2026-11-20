#!/usr/bin/env python3
"""Install fully staged learner workspaces without overwriting learner files.

WS-I04 transaction seam for the existing Bash generators. This is not an
OEE parser, a public CLI, or a migration interface.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys

COURSE = re.compile(r"(SEF|APP|SYS|AI|SEC)[1-9][0-9]*\Z")
PROGRAMS = {"SEF", "APP", "SYS", "AI", "SEC"}


class PublishError(Exception):
    """Unsafe or incomplete workspace publication."""


def lexists(path: Path) -> bool:
    return os.path.lexists(path)


def require_real_directory(path: Path, description: str) -> None:
    if path.is_symlink() or not path.is_dir():
        raise PublishError(f"{description} is not a real directory: {path}")


def checked_parents(root: Path, relative: Path) -> None:
    """Create only missing containing directories, rejecting symlink traversal."""
    current = root
    for name in relative.parts[:-1]:
        if name in ("", ".", ".."):
            raise PublishError("invalid workspace path component")
        current = current / name
        if lexists(current):
            require_real_directory(current, "workspace path")
        else:
            current.mkdir()
            require_real_directory(current, "workspace path")


def publish(root: Path, stage: Path, destinations: list[Path]) -> list[Path]:
    """Install each staged directory with a same-filesystem rename.

    The three course roots are separate directories and cannot be installed
    as one atomic filesystem operation. Validate *all* inputs first, stage
    completely, then rename each subtree without copying or truncating files.
    If a later rename fails, keep earlier published learner data intact.
    """
    require_real_directory(root, "workspace root")
    require_real_directory(stage, "staging directory")
    if stage.parent != root or not stage.name.startswith(".oee-stage-"):
        raise PublishError("staging directory must be directly inside workspace")
    if not destinations or len(set(destinations)) != len(destinations):
        raise PublishError("duplicate or empty publication targets")

    # Fail before mutating the workspace if any target already exists.
    for rel in destinations:
        if rel.is_absolute() or any(part in ("", ".", "..") for part in rel.parts):
            raise PublishError("publication paths must be relative and confined")
        source = stage / rel
        require_real_directory(source, "staged output")
        target = root / rel
        if lexists(target):
            raise PublishError(f"destination already exists; nothing overwritten: {target}")
        parent = root
        for part in rel.parts[:-1]:
            parent /= part
            if lexists(parent):
                require_real_directory(parent, "workspace path")

    installed: list[Path] = []
    try:
        for rel in destinations:
            checked_parents(root, rel)
            target = root / rel
            if lexists(target):
                raise PublishError(f"destination appeared during publication: {target}")
            os.rename(stage / rel, target)
            installed.append(target)
    except OSError as exc:
        raise PublishError(f"publishing stopped after {len(installed)} directories: "
                           f"{type(exc).__name__}: {exc}") from exc
    except PublishError as exc:
        if installed:
            raise PublishError(f"{exc}; {len(installed)} directories already published "
                               "and deliberately preserved") from exc
        raise
    return installed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--stage", required=True, type=Path)
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--course", nargs=2, metavar=("PROGRAM", "CODE"))
    selector.add_argument("--project", metavar="CODE")
    args = parser.parse_args(argv)
    try:
        # Refuse symlinked paths rather than accidentally publishing elsewhere.
        if args.workspace.is_symlink() or args.stage.is_symlink():
            raise PublishError("workspace and stage paths must not be symlinks")
        root = args.workspace.resolve(strict=True)
        stage = args.stage.resolve(strict=True)
        if args.course:
            program, code = args.course
            if program not in PROGRAMS or not COURSE.fullmatch(code) or not code.startswith(program):
                raise PublishError("course code does not match canonical program")
            destinations = [
                Path(parent) / program / code
                for parent in ("labs", "exercises", "notes")
            ]
        else:
            code = args.project
            if not COURSE.fullmatch(code):
                raise PublishError("invalid canonical project course code")
            destinations = [Path("projects") / code]
        publish(root, stage, destinations)
    except (PublishError, OSError) as exc:
        print(f"workspace_publish_error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
