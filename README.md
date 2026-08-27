# Reliability-aware slag surrogate — public demonstration

This repository is a compact public demonstration of the workflow described in the manuscript **“A reliability-aware four-dimensional thermodynamic surrogate for continuous design of Fe-saturated blast-furnace slags.”** It is intentionally designed to communicate the method and provide a quick interactive experience; it is **not** a full reproduction package.

## What is included

- `data/anchor_thermodynamic_sample_319.csv`: a trace-free, compact table of 319 thermodynamic anchor compositions and labels.
- `data/candidate_confirmation_top6.csv`: the six representative candidate rechecks reported in the manuscript.
- `models/`: the locked demonstration models: HGB for liquidus temperature and RBF-SVC models for range status and primary phase.
- `data/demo_grid.json`: precomputed predictions on a 31,680-point four-dimensional grid for the browser demo.
- `docs/index.html`: a dependency-free interactive page suitable for GitHub Pages.
- `scripts/prepare_release.py`: the transparent preparation script used to select the public tables and generate the demo grid.

## Interactive demo

Live demo: https://ustbtobyma.github.io/slag-thermodynamic-surrogate-demo/

The sliders return the closest point in the precomputed surrogate grid and report liquidus temperature, above-range probability, primary phase, phase confidence, and the trusted-interpolation status.

The demo does not call Thermo-Calc in the browser and should not be interpreted as an independent thermodynamic calculation. The Thermo-Calc database and proprietary software are not redistributed here.

No blanket software/data license is asserted in this demonstration release. Please contact the authors before redistributing the derived data or models, and cite the manuscript and repository in any use.

## Scope and caveats

The public package keeps the evidence-layer concept visible while omitting private calculation traces, intermediate artifacts, local machine paths, and obsolete model releases. The displayed predictions are surrogate outputs under the stated composition bounds and redox/database context. For scientific use, consult the manuscript and perform an explicit Thermo-Calc recheck for any new composition.

## Citation

Please cite the associated manuscript and this repository when using the demonstration. The repository is intended to be updated with the final DOI and version tag after publication.
