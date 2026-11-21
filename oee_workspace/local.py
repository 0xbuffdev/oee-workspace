"""No-clobber local workspace publication shared by the current Python CLI.

This is a learner-owned filesystem protocol, not a sandbox for concurrently
malicious processes. Every operation builds off-path and never edits existing
notes, evidence attempts or published project directories.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile

class PublicationError(Exception):
    pass

def exists(path: Path) -> bool:
    return os.path.lexists(path)

def real_directory(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_dir():
        raise PublicationError(f"{label} is not a real directory: {path}")

def workspace_root(directory: Path) -> Path:
    directory = Path(directory).expanduser()
    if directory.is_symlink() or not directory.is_dir():
        raise PublicationError(f"learner destination must exist and not be a symlink: {directory}")
    root = directory.resolve(strict=True)
    return root

def safe_parents(root: Path, relative: Path) -> None:
    """Make missing parent directories, rejecting a symlink at every component."""
    current = root
    for name in relative.parts[:-1]:
        if name in ("", ".", ".."):
            raise PublicationError("unsafe relative publication destination")
        current = current / name
        if exists(current):
            real_directory(current, "destination parent")
        else:
            current.mkdir()
            real_directory(current, "destination parent")

def publish(root: Path, stage: Path, destinations: list[Path]) -> list[Path]:
    """Publish fully staged course/project directories without touching existing ones.

    Multiple top-level directories cannot be renamed atomically together.
    If a normal late error occurs, newly owned published directories are
    rolled back when they still match their staged file bytes. If another
    process has modified them, preserve them rather than deleting learner work.
    OS process termination/power loss can leave a partially published tree.
    """
    root, stage = Path(root), Path(stage)
    real_directory(root, "workspace root")
    real_directory(stage, "staging directory")
    if stage.parent != root or not stage.name.startswith(".oee-stage-"):
        raise PublicationError("stage must be directly inside workspace")
    if not destinations or len(set(destinations)) != len(destinations):
        raise PublicationError("empty or repeated destinations")
    for rel in destinations:
        if rel.is_absolute() or any(part in ("", ".", "..") for part in rel.parts):
            raise PublicationError("invalid relative destination")
        source, target = stage / rel, root / rel
        real_directory(source, "staged output")
        if exists(target):
            raise PublicationError(f"destination already exists; nothing overwritten: {target}")
        current = root
        for part in rel.parts[:-1]:
            current /= part
            if exists(current):
                real_directory(current, "destination parent")

    # Record exactly what belongs to the new staged output for safe rollback.
    import hashlib
    def fingerprint(directory: Path) -> tuple:
        result = []
        for path in sorted(directory.rglob("*")):
            rel = path.relative_to(directory).as_posix()
            if path.is_symlink():
                raise PublicationError("symlink found inside generated output")
            if path.is_file():
                result.append((rel, "file", hashlib.sha256(path.read_bytes()).hexdigest()))
            elif path.is_dir():
                result.append((rel, "dir", None))
            else:
                raise PublicationError("unsupported generated entry type")
        return tuple(result)

    staged_fingerprints = {rel: fingerprint(stage / rel) for rel in destinations}
    installed: list[Path] = []
    try:
        for rel in destinations:
            safe_parents(root, rel)
            target = root / rel
            if exists(target):
                raise PublicationError(f"destination appeared during publication: {target}")
            os.rename(stage / rel, target)
            installed.append(target)
    except (OSError, PublicationError) as exc:
        retained = []
        for target in reversed(installed):
            rel = target.relative_to(root)
            try:
                if (target.is_symlink() or not target.is_dir() or
                        fingerprint(target) != staged_fingerprints[rel]):
                    retained.append(str(rel))
                else:
                    shutil.rmtree(target)
            except OSError:
                retained.append(str(rel))
        if retained:
            raise PublicationError(
                f"publication failed; changed/generated directories were preserved: {retained}; {exc}"
            ) from exc
        raise PublicationError(f"publication failed, new files rolled back: {exc}") from exc
    return installed

def publish_file_new(root: Path, rel: Path, data: bytes) -> Path:
    """Write a private temporary file and atomically link it into an absent path.

    A hard link is intentionally used instead of os.replace/os.rename, which
    would silently overwrite an existing file on some supported platforms.
    Unsupported hard-link filesystems fail safely, never fall back to clobber.
    """
    real_directory(root, "workspace root")
    if rel.is_absolute() or not rel.parts or any(part in ("", ".", "..") for part in rel.parts):
        raise PublicationError("output must be a confined relative workspace path")
    safe_parents(root, rel)
    target = root / rel
    if exists(target):
        raise PublicationError(f"output already exists: {rel.as_posix()}")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=target.parent, prefix=f".{target.name}.", suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if exists(target):
            raise PublicationError(f"output appeared during staging: {rel.as_posix()}")
        os.link(temporary, target)
    except OSError as exc:
        raise PublicationError(f"cannot safely publish new file {rel.as_posix()}: {exc}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return target
