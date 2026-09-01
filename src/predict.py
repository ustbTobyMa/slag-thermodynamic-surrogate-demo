"""Run one public-demo surrogate prediction.

The released models are used for inference only; Thermo-Calc is not invoked.
The returned dictionary includes the same local-support and confidence checks
used by the interactive demonstration.
"""
from functools import lru_cache
from pathlib import Path
import argparse
import json

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FEATURE_NAMES = ["Al2O3_wt_pct", "MgO_wt_pct", "FeO_wt_pct", "basicity_CaO_SiO2"]
FEATURE_RANGES = np.array([17.0, 15.0, 15.0, 0.5], dtype=float)
BOUNDS = ((8.0, 25.0), (0.0, 15.0), (5.0, 20.0), (1.0, 1.5))


@lru_cache(maxsize=1)
def load_models():
    """Load the locked models once per process."""
    return (
        joblib.load(ROOT / "models/liquidus_histgb.joblib"),
        joblib.load(ROOT / "models/range_status_svc_rbf.joblib"),
        joblib.load(ROOT / "models/primary_phase_svc_rbf.joblib"),
    )


@lru_cache(maxsize=1)
def load_anchor_features() -> np.ndarray:
    anchors = pd.read_csv(ROOT / "data/anchor_thermodynamic_sample_319.csv")
    return anchors[FEATURE_NAMES].to_numpy(dtype=float)


@lru_cache(maxsize=1)
def leave_one_out_d95() -> float:
    anchors = load_anchor_features() / FEATURE_RANGES
    distances = np.sqrt(((anchors[:, None, :] - anchors[None, :, :]) ** 2).sum(axis=2))
    np.fill_diagonal(distances, np.inf)
    return float(np.quantile(distances.min(axis=1), 0.95))


def _validate(values) -> None:
    for name, value, (lower, upper) in zip(FEATURE_NAMES, values, BOUNDS):
        if not np.isfinite(value):
            raise ValueError(f"{name} must be finite")
        if not lower <= value <= upper:
            raise ValueError(f"{name} must be within [{lower}, {upper}]")


def predict(al2o3: float, mgo: float, feo: float, basicity: float) -> dict:
    values = (float(al2o3), float(mgo), float(feo), float(basicity))
    _validate(values)
    x = np.array([values], dtype=float)
    liquidus, range_model, phase_model = load_models()
    range_probabilities = range_model.predict_proba(x)[0]
    above_range_probability = float(range_probabilities[list(range_model.classes_).index(1)])
    phase_prob = phase_model.predict_proba(x)[0]
    phase_confidence = float(phase_prob.max())
    anchor_scaled = load_anchor_features() / FEATURE_RANGES
    point_scaled = x[0] / FEATURE_RANGES
    nearest_distance = float(np.sqrt(((anchor_scaled - point_scaled) ** 2).sum(axis=1).min()))
    d95 = leave_one_out_d95()
    return {
        "predicted_liquidus_K": float(liquidus.predict(x)[0]),
        "above_range_probability": above_range_probability,
        "primary_phase": str(phase_model.classes_[int(phase_prob.argmax())]),
        "phase_probability_max": phase_confidence,
        "nearest_training_distance_4d": nearest_distance,
        "d95_support_cutoff": d95,
        "trusted_interpolation": bool(
            above_range_probability <= 0.20
            and phase_confidence >= 0.50
            and nearest_distance <= d95
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--al2o3", type=float, required=True)
    parser.add_argument("--mgo", type=float, required=True)
    parser.add_argument("--feo", type=float, required=True)
    parser.add_argument("--basicity", type=float, required=True)
    args = parser.parse_args()
    try:
        result = predict(args.al2o3, args.mgo, args.feo, args.basicity)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
