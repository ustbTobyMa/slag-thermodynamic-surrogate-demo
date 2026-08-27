"""Run one public-demo surrogate prediction.

This is a lightweight inference example. It does not invoke Thermo-Calc.
"""
from pathlib import Path
import argparse

import joblib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
FEATURE_NAMES = ["Al2O3_wt_pct", "MgO_wt_pct", "FeO_wt_pct", "basicity_CaO_SiO2"]


def predict(al2o3: float, mgo: float, feo: float, basicity: float) -> dict:
    x = np.array([[al2o3, mgo, feo, basicity]], dtype=float)
    liquidus = joblib.load(ROOT / "models/liquidus_histgb.joblib")
    range_model = joblib.load(ROOT / "models/range_status_svc_rbf.joblib")
    phase_model = joblib.load(ROOT / "models/primary_phase_svc_rbf.joblib")
    phase_prob = phase_model.predict_proba(x)[0]
    return {
        "predicted_liquidus_K": float(liquidus.predict(x)[0]),
        "above_range_probability": float(range_model.predict_proba(x)[0, 1]),
        "primary_phase": str(phase_model.classes_[int(phase_prob.argmax())]),
        "phase_probability_max": float(phase_prob.max()),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--al2o3", type=float, required=True)
    parser.add_argument("--mgo", type=float, required=True)
    parser.add_argument("--feo", type=float, required=True)
    parser.add_argument("--basicity", type=float, required=True)
    args = parser.parse_args()
    print(predict(args.al2o3, args.mgo, args.feo, args.basicity))
