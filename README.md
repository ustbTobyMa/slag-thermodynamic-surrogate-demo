# Reliability-aware slag surrogate — public demonstration

This repository is a compact public demonstration of the workflow described in the manuscript **“A reliability-aware four-dimensional thermodynamic surrogate for continuous design of Fe-saturated blast-furnace slags.”** It is designed to communicate the method through a quick interactive experience.

## What is included

- `data/anchor_thermodynamic_sample_319.csv`: a trace-free, compact table of 319 thermodynamic anchor compositions and labels.
- `data/candidate_confirmation_top6.csv`: the six representative candidate rechecks reported in the manuscript.
- `models/`: the locked demonstration models: HGB for liquidus temperature and RBF-SVC models for range status and primary phase.
- `data/demo_grid.json`: precomputed predictions on a 31,680-point four-dimensional grid for the browser demo.
- `docs/index.html`: a dependency-free interactive page suitable for GitHub Pages, with a ready-to-view default preview, an explicit **Start calculation** action, and linked Al₂O₃–MgO liquidus-temperature and primary-phase slice maps.
- `scripts/prepare_release.py`: the transparent preparation script used to select the public tables and generate the demo grid.

## Command-line inference

The released models can also be queried locally without Thermo-Calc:

```bash
python src/predict.py --al2o3 12 --mgo 4 --feo 10 --basicity 1.3
```

The JSON output reports the predicted liquidus, above-range probability, primary-phase confidence, nearest-anchor
distance, and the trusted-interpolation flag. Inputs are checked against the published composition bounds before
inference. The example environment is pinned in `requirements.txt` and was tested with Python 3.7–3.10. The browser
page uses the nearest precomputed grid state for instant interaction, whereas this command performs direct model
inference.

`scripts/prepare_release.py` can be rerun either from the original project tree or from a clean clone. In a clean
clone it reuses the released tables and model files and regenerates the precomputed grid deterministically.

## Interactive demo

Live demo: https://ustbtobyma.github.io/slag-thermodynamic-surrogate-demo/

The page opens with a precomputed preview. After changing the composition controls, click **Start calculation** to update the nearest-grid prediction and the two linked slice maps. The liquidus field is smoothly interpolated, while the categorical phase field is displayed as spatially weighted phase regions.

The page is a lightweight surrogate-model demonstration; full method details are provided in the associated manuscript.

## Citation

Please cite the associated manuscript and this repository when using the demonstration. This repository is archived as release **v1.0.1** for submission. If the associated article is accepted, the final article DOI will be added here.

The Thermo-Calc software/database files are not redistributed. The released tables, scripts, locked models, and precomputed grid are provided for inspection and reuse of the surrogate workflow.
