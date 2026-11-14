"""Generate a static JSON snapshot of `teraqube.evaluate(...)` across every
(code, material) cell, used by /demo to animate a "decision trace" without
needing a live Python backend at request time.

Run from repo root:  python scripts/build_engine_snapshot.py
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from teraqube import evaluate, tier_of, phys_qubits  # noqa: E402
from teraqube.catalogs import QEC, MAT  # noqa: E402

QUBIT = "transmon"
DOPANT = "none"
DISTANCE = 5
ENV = {"substrate": "sapphire", "geom": "planar_std"}
TARGET = 1e-6


def safe(value):
    """Replace NaN/inf with None so the JSON stays valid."""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def main() -> None:
    cells = []
    failures = 0
    t0 = time.time()

    qubits = phys_qubits("surface", DISTANCE)  # baseline for the page

    for code in QEC.keys():
        for material in MAT.keys():
            try:
                r = evaluate(QUBIT, material, DOPANT, code, DISTANCE, ENV)
                verdict = tier_of(r, target=TARGET)
                cells.append({
                    "code": code,
                    "material": material,
                    "T1": safe(r.get("T1")),
                    "T2": safe(r.get("T2")),
                    "pL": safe(r.get("pL_gnn")),
                    "lambda35": safe(r.get("lambda35")),
                    "verdict": verdict,
                })
            except Exception as e:
                failures += 1
                cells.append({
                    "code": code,
                    "material": material,
                    "T1": None, "T2": None, "pL": None, "lambda35": None,
                    "verdict": "ERROR",
                    "error": str(e)[:120],
                })

    elapsed = time.time() - t0

    snapshot = {
        "schema": 1,
        "generated_at": int(time.time()),
        "engine_version": "teraqube/9.0.0",
        "config": {
            "qubit": QUBIT,
            "dopant": DOPANT,
            "distance": DISTANCE,
            "env": ENV,
            "target_pL": TARGET,
        },
        "totals": {
            "codes": len(QEC),
            "materials": len(MAT),
            "cells": len(cells),
            "failures": failures,
            "build_seconds": round(elapsed, 2),
            "physical_qubits_baseline": qubits,
        },
        "cells": cells,
    }

    out_dir = ROOT / "public"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "engine-snapshot.json"
    out_path.write_text(json.dumps(snapshot, separators=(",", ":")))

    size_kb = out_path.stat().st_size / 1024
    print(f"Wrote {out_path} — {len(cells)} cells, "
          f"{failures} failures, {size_kb:.1f} KB, {elapsed:.1f}s")


if __name__ == "__main__":
    main()
