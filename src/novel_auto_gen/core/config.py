from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import re

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


DEFAULT_CONFIG_PATH = "configs/default.toml"


@dataclass
class AppConfig:
    raw: dict[str, Any]

    @property
    def project(self) -> dict[str, Any]:
        return self.raw.get("project", {})

    @property
    def generation(self) -> dict[str, Any]:
        return self.raw.get("generation", {})

    @property
    def evaluation(self) -> dict[str, Any]:
        return self.raw.get("evaluation", {})

    @property
    def paths(self) -> dict[str, Any]:
        return self.raw.get("paths", {})


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    if raw in {"true", "false"}:
        return raw == "true"
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw)
    if raw.startswith("[") and raw.endswith("]"):
        inside = raw[1:-1].strip()
        if not inside:
            return []
        parts = [p.strip() for p in inside.split(",")]
        return [_parse_value(p) for p in parts]
    if raw.startswith("{") and raw.endswith("}"):
        inside = raw[1:-1].strip()
        out = {}
        if inside:
            for part in inside.split(","):
                k, v = part.split("=", 1)
                out[k.strip()] = _parse_value(v)
        return out
    return raw


def _simple_toml_loads(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    section: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].split(".")
            cursor = data
            for sec in section:
                cursor = cursor.setdefault(sec, {})
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            value = _parse_value(v)
            cursor = data
            for sec in section:
                cursor = cursor.setdefault(sec, {})
            cursor[k] = value
    return data


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    config_path = Path(path)
    suffix = config_path.suffix.lower()
    if suffix == ".toml":
        text = config_path.read_text(encoding="utf-8")
        data = tomllib.loads(text) if tomllib else _simple_toml_loads(text)
    elif suffix == ".json":
        data = json.loads(config_path.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"unsupported config format: {suffix}, use .toml or .json")
    return AppConfig(raw=data or {})
