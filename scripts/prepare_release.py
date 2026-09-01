from __future__ import annotations

import json
import shutil
from itertools import product
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
DATA_DIR = ROOT / "data"
WEB_DATA_DIR = ROOT / "docs/data"
MODEL_DIR = ROOT / "models"

ANCHOR_SRC = PROJECT / "data/generated/continuous_4d_v1/all_calculations_combined_319_v1.csv"
CANDIDATE_SRC = PROJECT / "artifacts/validation/candidate_thermocalc_confirmation_FINAL_319_v1/candidate_top_rank6_comparison.csv"
LOCKED_MODELS = PROJECT / "artifacts/validation/continuous_4d_v1_FINAL_319_targeted_confirmation_24_v1/locked_selected_models"

FEATURES = ["Al2O3_wt_pct", "MgO_wt_pct", "FeO_wt_pct", "basicity_CaO_SiO2"]
ANCHOR_COLUMNS = [
    "composition_id", "CaO_wt_pct", "SiO2_wt_pct", "Al2O3_wt_pct", "MgO_wt_pct", "FeO_wt_pct",
    "status", "liquidus_temperature_K", "primary_phase_family", "basicity_CaO_SiO2",
]
CANDIDATE_COLUMNS = [
    "composition_id_design", "slice_rank", "basicity_CaO_SiO2", "FeO_wt_pct", "Al2O3_wt_pct",
    "MgO_wt_pct", "CaO_wt_pct", "SiO2_wt_pct", "predicted_liquidus_K", "predicted_primary_phase",
    "predicted_above_range_probability", "phase_probability_max", "nearest_training_distance_4d",
    "candidate_score", "liquidus_temperature_K", "primary_phase_family", "delta_T_K",
]


def make_public_tables() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # The script can be rerun from the original project or from a clean clone
    # of this public repository.  In the latter case, reuse the released table.
    anchor_source = ANCHOR_SRC if ANCHOR_SRC.exists() else DATA_DIR / "anchor_thermodynamic_sample_319.csv"
    anchors = pd.read_csv(anchor_source)[ANCHOR_COLUMNS].copy()
    anchors.to_csv(DATA_DIR / "anchor_thermodynamic_sample_319.csv", index=False, float_format="%.6f")

    candidate_source = CANDIDATE_SRC if CANDIDATE_SRC.exists() else DATA_DIR / "candidate_confirmation_top6.csv"
    candidates = pd.read_csv(candidate_source)[CANDIDATE_COLUMNS].copy()
    candidates.to_csv(DATA_DIR / "candidate_confirmation_top6.csv", index=False, float_format="%.6f")


def nearest_distance(points: np.ndarray, anchors: np.ndarray, ranges: np.ndarray) -> np.ndarray:
    scaled_points = points / ranges
    scaled_anchors = anchors / ranges
    result = np.empty(len(points), dtype=float)
    for start in range(0, len(points), 2048):
        block = scaled_points[start:start + 2048]
        dist2 = ((block[:, None, :] - scaled_anchors[None, :, :]) ** 2).sum(axis=2)
        result[start:start + len(block)] = np.sqrt(dist2.min(axis=1))
    return result


def leave_one_out_d95(anchors: np.ndarray, ranges: np.ndarray) -> float:
    scaled = anchors / ranges
    dist2 = ((scaled[:, None, :] - scaled[None, :, :]) ** 2).sum(axis=2)
    np.fill_diagonal(dist2, np.inf)
    nearest = np.sqrt(dist2.min(axis=1))
    return float(np.quantile(nearest, 0.95))


def make_demo_grid() -> None:
    model_dir = LOCKED_MODELS if LOCKED_MODELS.exists() else MODEL_DIR
    required_models = ["liquidus_histgb.joblib", "range_status_svc_rbf.joblib", "primary_phase_svc_rbf.joblib"]
    missing = [name for name in required_models if not (model_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing released model files: " + ", ".join(missing) +
            ". Place them in models/ or run this script from the source project."
        )
    liquidus = joblib.load(model_dir / "liquidus_histgb.joblib")
    range_model = joblib.load(model_dir / "range_status_svc_rbf.joblib")
    phase_model = joblib.load(model_dir / "primary_phase_svc_rbf.joblib")
    anchors = pd.read_csv(DATA_DIR / "anchor_thermodynamic_sample_319.csv")

    axes = [
        np.linspace(8.0, 25.0, 24),
        np.linspace(0.0, 15.0, 22),
        np.linspace(5.0, 20.0, 20),
        np.array([1.1, 1.3, 1.5]),
    ]
    points = np.array(list(product(*axes)), dtype=float)
    frame = pd.DataFrame(points, columns=FEATURES)
    x = frame[FEATURES].to_numpy()
    frame["predicted_liquidus_K"] = liquidus.predict(x)
    frame["predicted_above_range_probability"] = range_model.predict_proba(x)[:, list(range_model.classes_).index(1)]
    phase_prob = phase_model.predict_proba(x)
    frame["predicted_primary_phase"] = phase_model.classes_[phase_prob.argmax(axis=1)]
    frame["phase_probability_max"] = phase_prob.max(axis=1)

    ranges = np.array([17.0, 15.0, 15.0, 0.5], dtype=float)
    anchor_x = anchors[FEATURES].to_numpy()
    d95 = leave_one_out_d95(anchor_x, ranges)
    frame["nearest_training_distance_4d"] = nearest_distance(x, anchor_x, ranges)
    frame["trusted_interpolation"] = (
        (frame["predicted_above_range_probability"] <= 0.20)
        & (frame["phase_probability_max"] >= 0.50)
        & (frame["nearest_training_distance_4d"] <= d95)
    )
    frame["coverage_score"] = np.maximum(0.0, 1.0 - frame["nearest_training_distance_4d"] / d95)

    columns = [
        "Al2O3_wt_pct", "MgO_wt_pct", "FeO_wt_pct", "basicity_CaO_SiO2",
        "predicted_liquidus_K", "predicted_above_range_probability", "predicted_primary_phase",
        "phase_probability_max", "nearest_training_distance_4d", "trusted_interpolation", "coverage_score",
    ]
    rows = []
    for row in frame[columns].itertuples(index=False, name=None):
        rows.append([
            *[round(float(v), 5) for v in row[:6]], row[6],
            *[round(float(v), 5) for v in row[7:9]], bool(row[9]), round(float(row[10]), 5),
        ])
    payload = {
        "columns": columns,
        "rows": rows,
        "metadata": {
            "n_points": len(rows),
            "d95": round(d95, 6),
            "model_release": "locked HGB liquidus + RBF-SVC range/phase",
            "purpose": "interactive demonstration; nearest precomputed surrogate-grid lookup",
        },
    }
    encoded = json.dumps(payload, separators=(",", ":"))
    (DATA_DIR / "demo_grid.json").write_text(encoded, encoding="utf-8")
    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    (WEB_DATA_DIR / "demo_grid.json").write_text(encoded, encoding="utf-8")


def copy_locked_models() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for name in ["liquidus_histgb.joblib", "range_status_svc_rbf.joblib", "primary_phase_svc_rbf.joblib"]:
        source = LOCKED_MODELS / name
        if source.exists():
            shutil.copy2(source, MODEL_DIR / name)
        elif not (MODEL_DIR / name).exists():
            raise FileNotFoundError(
                f"Missing {name}. Place the released model in models/ or run this script from the source project."
            )


if __name__ == "__main__":
    make_public_tables()
    copy_locked_models()
    make_demo_grid()
    print("Prepared public demo release")
