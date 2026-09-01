# CALPHAD-to-thermodynamic-atlas surrogate — public demonstration

This repository is a compact public demonstration of the framework described in the manuscript **“From discrete CALPHAD calculations to continuous thermodynamic design maps: A reliability-aware surrogate framework for multicomponent slags.”** It shows how discrete thermodynamic anchors can be reconstructed as a continuous, queryable design atlas while keeping local-support diagnostics visible.

## What is included

- `data/anchor_thermodynamic_sample_319.csv`: a trace-free, compact table of 319 thermodynamic anchor compositions and labels.
- `data/candidate_confirmation_top6.csv`: the six representative candidate rechecks reported in the manuscript.
- `models/`: the locked demonstration models: HGB for liquidus temperature and RBF-SVC models for range status and primary phase.
- `data/demo_grid.json`: precomputed predictions on a 31,680-point four-dimensional grid for the browser demo.
- `docs/index.html`: a dependency-free interactive page suitable for GitHub Pages, with a ready-to-view default preview, an explicit **Start calculation** action, and linked Al₂O₃–MgO liquidus-temperature and primary-phase slice maps.
- `src/predict.py`: a compact command-line inference interface for the released models.

## Public release scope

This repository intentionally provides the key computational artifacts needed to inspect and use the surrogate:
the anchor table, locked models, precomputed grid, interactive page, and a lightweight inference interface. The
full private Thermo-Calc batch-generation and model-development workflow is not redistributed. This keeps the
public release focused on the transferable method and avoids coupling the demonstration to local project paths or
software-specific automation.

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

## Interactive demo

Live demo: https://ustbtobyma.github.io/slag-thermodynamic-surrogate-demo/

The page opens with a precomputed preview. After changing the composition controls, click **Start calculation** to update the nearest-grid prediction and the two linked slice maps. The liquidus field is smoothly interpolated, while the categorical phase field is displayed as spatially weighted phase regions.

The page is a lightweight surrogate-model demonstration; full method details are provided in the associated manuscript.

## Citation

Please cite the associated manuscript and this repository when using the demonstration. This repository is archived as release **v1.1.0** for submission. If the associated article is accepted, the final article DOI will be added here.

The Thermo-Calc software/database files are not redistributed. The released tables, scripts, locked models, and precomputed grid are provided for inspection and reuse of the surrogate workflow.
