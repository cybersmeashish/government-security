"""Verify pinned upstream source bytes before importing the shared research controls."""
import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def check_reference(path):
    path = Path(path).resolve()
    lock = json.loads((ROOT / "references/upstream-lock.json").read_text())
    for relative, expected in lock["source_manifest"].items():
        file = path / relative
        if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != expected:
            raise ValueError(f"pinned reference source mismatch: {relative}")
    return lock


def load_reference(path):
    lock = check_reference(path)
    path = Path(path).resolve()
    for name, module in tuple(sys.modules.items()):
        if name == "assurance" or name.startswith("assurance."):
            module_file = getattr(module, "__file__", None)
            if module_file is None or not Path(module_file).resolve().is_relative_to(path):
                raise ValueError("different assurance module already loaded")
    sys.path.insert(0, str(path))
    modules = {name: importlib.import_module("assurance." + name)
               for name in ("crypto", "admission", "recovery", "updates")}
    for module in modules.values():
        if not Path(module.__file__).resolve().is_relative_to(path):
            raise ValueError("reference module origin mismatch")
    return lock, modules
