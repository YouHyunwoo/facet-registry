#!/usr/bin/env python3
"""Validates one submitted package and adds it to index.json. Never runs anything inside the package.

Mirrors impls/Facet/Packages.cs and Design/ExternalSkins.cs; the app checks everything again when installing.
Input comes from the environment because issue text is untrusted: ISSUE_BODY, AUTHOR, REPOSITORY, GITHUB_OUTPUT.
"""
import hashlib
import json
import os
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

ATTACHMENT = re.compile(r"https://github\.com/user-attachments/files/\d+/[A-Za-z0-9._-]+\.zip")
VALID_ID = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")
VALID_VERSION = re.compile(r"[0-9A-Za-z][0-9A-Za-z.-]{0,31}")
VALID_COLOR = re.compile(r"#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})")
VALID_ASSET = re.compile(r"[a-z0-9_-]{1,64}\.png")
RESERVED = re.compile(r"(con|prn|aux|nul|com\d|lpt\d)(\..*)?", re.IGNORECASE)
COLOR_TOKENS = {"Bg", "OverlayBackdrop", "ModalBackdrop", "DangerSoft", "Panel", "Edge", "Ink", "Muted", "ScheduleNow",
                "Mint", "Danger", "CalendarSunday", "CalendarSaturday", "Input", "Selected", "Hover", "OnAccent"}
BUILT_IN_SKINS = {"default", "midnight", "space"}
SKIN_EXTENSIONS = {".json", ".png", ".txt", ".md"}
MAX_PLUGIN = 1 << 30
MAX_SKIN = 64 << 20
MAX_ENTRIES = 5000


class Rejected(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


def check_paths(names):
    require(len(names) <= MAX_ENTRIES, "too many files")
    for name in names:
        require("\\" not in name and not name.startswith("/"), f"unsafe path: {name}")
        for part in name.rstrip("/").split("/"):
            require(part and part != ".." and ":" not in part and not part.endswith((".", " "))
                    and not RESERVED.fullmatch(part), f"unsafe path: {name}")


def inspect(path):
    """Returns (kind, manifest) or raises Rejected."""
    try:
        with zipfile.ZipFile(path) as package:
            infos = package.infolist()
            names = [info.filename for info in infos]
            check_paths(names)
            total = sum(info.file_size for info in infos)
            has_plugin, has_skin = "plugin.json" in names, "skin.json" in names
            require(has_plugin != has_skin, "the zip root needs exactly one of plugin.json and skin.json")
            manifest = json.loads(package.read("plugin.json" if has_plugin else "skin.json"))
    except (zipfile.BadZipFile, ValueError, OSError) as error:
        raise Rejected(f"unreadable package: {error}")
    require(isinstance(manifest, dict), "the manifest must be an object")
    package_id, version, name = manifest.get("id"), manifest.get("version"), manifest.get("name")
    require(isinstance(package_id, str) and VALID_ID.fullmatch(package_id) and not package_id.endswith(".")
            and not RESERVED.fullmatch(package_id), "invalid id")
    require(isinstance(version, str) and VALID_VERSION.fullmatch(version), "invalid version")
    require(isinstance(name, str) and name.strip() and len(name) <= 64, "invalid name")
    if has_plugin:
        assembly = manifest.get("assembly")
        require(total <= MAX_PLUGIN, "package too large")
        require(isinstance(assembly, str) and "/" not in assembly and "\\" not in assembly and assembly in names, "assembly missing")
        return "plugin", manifest
    require(total <= MAX_SKIN, "package too large")
    require(package_id not in BUILT_IN_SKINS, "reserved skin id")
    for file in names:
        require(file.endswith("/") or Path(file).suffix.lower() in SKIN_EXTENSIONS, f"file not allowed in a skin: {file}")
    colors = manifest.get("colors", {})
    require(isinstance(colors, dict), "colors must be an object")
    for token, color in colors.items():
        require(token in COLOR_TOKENS and isinstance(color, str) and VALID_COLOR.fullmatch(color), f"invalid color: {token}")
    theme = manifest.get("theme", {})
    require(isinstance(theme, dict), "theme must be an object")
    lowered = {key.lower(): value for key, value in theme.items()}
    for slot in ("background", "frame"):
        asset = lowered.get(slot)
        if asset is not None:
            require(isinstance(asset, str) and VALID_ASSET.fullmatch(asset) and asset in names, f"invalid {slot} image")
    return "skin", manifest


def add_to_index(index, kind, manifest, author, repository, sha256):
    """Returns the release tag, or raises Rejected when the id belongs to someone else or the version exists."""
    package_id, version = manifest["id"], manifest["version"]
    for row in index["packages"]:
        if row["id"] == package_id and row["kind"] == kind:
            require(row["author"] == author, "this id belongs to another author")
            require(row["version"] != version, "this version is already published")
    tag = f"{kind}-{package_id}-{version}"
    index["packages"] = [row for row in index["packages"] if not (row["id"] == package_id and row["kind"] == kind)]
    index["packages"].append({
        "kind": kind, "id": package_id, "name": manifest["name"].strip(), "version": version, "author": author,
        "description": str(manifest.get("description", ""))[:200],
        "url": f"https://github.com/{repository}/releases/download/{tag}/{package_id}-{version}.zip", "sha256": sha256,
    })
    index["packages"].sort(key=lambda row: (row["kind"], row["id"]))
    return tag


def main():
    found = ATTACHMENT.findall(os.environ["ISSUE_BODY"])
    require(len(set(found)) == 1, "attach exactly one .zip file")
    work = Path(os.environ.get("RUNNER_TEMP", "."))
    download = work / "package.zip"
    with urllib.request.urlopen(found[0], timeout=120) as response, download.open("wb") as output:
        copied = 0
        while chunk := response.read(1 << 20):
            copied += len(chunk)
            require(copied <= MAX_PLUGIN, "package too large")
            output.write(chunk)
    kind, manifest = inspect(download)
    sha256 = hashlib.sha256(download.read_bytes()).hexdigest()
    index_path = Path("index.json")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    tag = add_to_index(index, kind, manifest, os.environ["AUTHOR"], os.environ["REPOSITORY"], sha256)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    asset = work / f"{manifest['id']}-{manifest['version']}.zip"
    download.replace(asset)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"kind={kind}\ntag={tag}\nasset={asset}\nsha256={sha256}\n")


if __name__ == "__main__":
    try:
        main()
    except Rejected as error:
        print(f"::error::{error}")
        sys.exit(1)
