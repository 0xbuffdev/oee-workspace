#!/usr/bin/env python3
"""Explicit, offline verification and no-clobber install of OEE 2026.11.1.

Download files separately from the published OEE GitHub Releases. This script
never fetches network data, accesses Git, imports learner data or writes keys.
A reviewed project lock plus an independently pinned steward-key fingerprint
are required before the Toolkit can install the signed curriculum.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from pathlib import Path
import sys

RELEASE_ID = "2026.11.1"
MANIFEST_SHA256 = "57441494eb69c2ff9cb3f6029c8adc3c6a56f8c6ecabc43196c9b686e5959a6c"
# Independently reviewed values from the official GitHub Release and steward
# publication evidence. Do not accept a moving tag, remote "latest", or
# arbitrary file of the same name if these bytes do not match.
CURRICULUM_ASSETS = {
    "oee-curriculum-2026.11.1.tar":
        (3768320, "931b30209a2727717af331f4fd46bfc8e637c94c4d1d95d08d6ffeee753c78d2"),
    "oee-curriculum-2026.11.1.attestation.json":
        (216, "03399b3a7b1f049ff2e09481d59dc58cc239e29130aace248e3358487d922203"),
    "oee-curriculum-2026.11.1.sig":
        (64, "8e2230b570ef555892bd387c141a7d948b4ca9f94179d0db2f6b4587befc3b47"),
    "oee-steward-ed25519-public.pem":
        (113, "e1b726c8978bc9c1fed44baa099074d35260e17826628af483668bb45e83989f"),
}


def require(condition: bool, description: str) -> None:
    if not condition:
        raise ValueError(description)


def _unique_keys(pairs: list[tuple[str, object]]) -> dict:
    data = {}
    for key, value in pairs:
        require(key not in data, "duplicate curriculum lock property: " + key)
        data[key] = value
    return data


def validate_lock(path: Path) -> None:
    require(path.is_file() and not path.is_symlink(),
            "workspace lock is missing or symlinked")
    require(path.stat().st_size <= 4096, "workspace lock too large")
    data = json.loads(path.read_bytes().decode("utf-8", "strict"),
                      object_pairs_hook=_unique_keys)
    require(type(data) is dict and type(data.get("formatVersion")) is int and data == {
        "formatVersion": 1, "releaseId": RELEASE_ID,
        "manifestSha256": MANIFEST_SHA256,
    }, "workspace lock does not identify approved OEE 2026.11.1; never auto-repin")


def software_selection():
    return runpy.run_path(str(Path(__file__).with_name("run-pinned-toolkit.py")))


def asset_specs():
    identity = software_selection()
    return {**identity["software_assets"](identity["selection"]()), **CURRICULUM_ASSETS}


def read_and_hash_assets(folder: Path) -> dict[str, bytes]:
    require(folder.is_dir() and not folder.is_symlink(),
            "artifact directory must be a real directory")
    result = {}
    for name, (size, expected_sha) in asset_specs().items():
        file = folder / name
        require(file.is_file() and not file.is_symlink(),
                f"missing or symlinked official asset: {name}")
        require(file.stat().st_size == size, f"incorrect official asset size: {name}")
        data = file.read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected_sha,
                f"official SHA-256 mismatch (do not install): {name}")
        result[name] = data
    return result


def fingerprint_key(pem: bytes) -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    key = serialization.load_pem_public_key(pem)
    require(isinstance(key, Ed25519PublicKey), "official key must be Ed25519")
    der = key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()


def verify_official_signature(assets: dict[str, bytes]) -> None:
    from oee_toolkit.release_archive import verify_attestation
    pin = software_selection()["selection"]()
    archive = assets["oee-curriculum-2026.11.1.tar"]
    attestation = assets["oee-curriculum-2026.11.1.attestation.json"]
    signature = assets["oee-curriculum-2026.11.1.sig"]
    public_pem = assets["oee-steward-ed25519-public.pem"]
    require(fingerprint_key(public_pem) == pin["stewardKeySha256"],
            "steward public key differs from separately approved fingerprint")
    manifest = verify_attestation(
        archive, MANIFEST_SHA256, attestation, signature, public_pem,
    )
    require(manifest["releaseId"] == RELEASE_ID and
            manifest["source"]["commit"] == "f2afed3e36f6ae0495e2b44a8d9337661defeda1",
            "signed official release identity disagrees with approved source")


def install(assets: dict[str, bytes], lock: Path, store: Path | None) -> Path:
    from oee_toolkit.release_archive import install_verified_archive
    from oee_toolkit.release_source import default_store, resolve_release
    store = store if store is not None else default_store()
    # The official installer is offline and refuses overwrites; never make
    # an existing symlink store appear trustworthy by following it.
    require(not store.is_symlink(), "trusted store must not be a symlink")
    store.mkdir(mode=0o700, parents=True, exist_ok=True)
    require(store.is_dir() and not store.is_symlink(),
            "trusted store must be an existing real directory")
    if not (store / MANIFEST_SHA256).exists() and not (store / MANIFEST_SHA256).is_symlink():
        install_verified_archive(
            assets["oee-curriculum-2026.11.1.tar"], MANIFEST_SHA256,
            assets["oee-curriculum-2026.11.1.attestation.json"],
            assets["oee-curriculum-2026.11.1.sig"],
            assets["oee-steward-ed25519-public.pem"], store,
        )
    source = resolve_release(lock, store)
    require(source.release_id == RELEASE_ID and
            source.manifest_sha256 == MANIFEST_SHA256,
            "installed release disagrees with the reviewed workspace lock")
    return store / MANIFEST_SHA256


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True,
                        help="directory containing downloaded official Release assets")
    parser.add_argument("--lock", type=Path, default=Path("oee-curriculum.lock.json"))
    parser.add_argument("--store", type=Path, default=None,
                        help="override default user cache; must be a trusted directory")
    parser.add_argument("--verify-only", action="store_true",
                        help="check published asset SHA-256 and lock without importing Toolkit")
    args = parser.parse_args()
    try:
        identity = software_selection()
        identity["selection"]()
        validate_lock(args.lock)
        assets = read_and_hash_assets(args.artifacts)
        print("All six official assets have exact approved sizes and SHA-256 hashes.")
        if args.verify_only:
            return 0
        identity["verify_toolkit"]()
        verify_official_signature(assets)
        print("Official steward Ed25519 signature and independently pinned fingerprint: valid.")
        installed = install(assets, args.lock, args.store)
        print(f"Installed trusted OEE {RELEASE_ID} at {installed}")
        print("Offline Toolkit and Workspace commands now use the project lock.")
        return 0
    except (ValueError, OSError, ImportError, TypeError, KeyError) as exc:
        print("Official OEE install rejected: " + str(exc), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
