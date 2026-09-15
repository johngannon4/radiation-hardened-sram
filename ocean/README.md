# OCEAN simulation scripts

OCEAN (Cadence's SKILL-based batch interface to Spectre) is what made the 18,000-simulation
PVT study tractable. Every script here drives the `12T_DICE_Bitcell_SEU` testbench from
[`../cadence/`](../cadence/), which carries the design variables the scripts overwrite:
`wn_store`, `wp_store`, `wn_access`, `Vdd`, and the four `Qinj`/`Ipeak` injection variables.

Run them from a Cadence environment with `ocean -nograph -restore run_full_sim.ocn`, or from
the CIW with `load("run_full_sim.ocn")`.

The scripts are committed exactly as they were run, which means **the file paths inside them
are absolute paths into the original Penn compute environment**
(`/lcars/home/g/gannon1/...`). Reusing them elsewhere means editing the `design`,
`resultsDir`, `modelFile`, and CSV output paths, and the `base` variable in the drivers.

## Structure

Each sweep is a driver script that sets global variables and `load()`s a per-corner worker
script once per point. OCEAN has no function-scoped parameter passing here, so the workers
read globals (`g_wn_store`, `g_temp`, `g_vdd`, `g_polarity`, …) and append one CSV row per
run. Appending per run rather than accumulating in memory is what made the sweeps resumable
after a crash partway through a multi-day batch.

The three directories are three generations of the same study, kept because the analysis
notebook consumes the output of all three.

### `pvt_sweep/` — the final study (paper Table I)

`run_full_sim.ocn` drives the full space: 6 × 6 sizing grid × 5 temperatures × 5 supply
voltages × 5 process corners, plus both storage polarities for SEU.

- SEU: 6 × 6 × 5 × 5 × 5 × 2 = **9,000** bisection runs
- Leakage power: 4,500 runs
- SNM: 4,500 runs

Critical charge is extracted by **bisection inside the OCEAN script itself**: each worker
brackets Q<sub>crit</sub> on [2, 50] fC and runs 8 transient simulations, halving the interval
each time based on whether the struck node sits on the wrong side of V<sub>DD</sub>/2 at
t = 5 ns. Eight iterations converge to ±0.19 fC, which is why a 9,000-point sweep is 72,000
Spectre transients rather than a coarse voltage grid.

| File | Role |
|---|---|
| `run_full_sim.ocn` | Driver: three sweep loops (SEU → power → SNM), writes CSV headers |
| `seu/dice_seu_single_<corner>_full.ocn` | 8-iteration Q<sub>crit</sub> bisection, one per process corner |
| `power/dice_power_single_<corner>_full.ocn` | DC operating point, P<sub>leak</sub> = \|I<sub>VDD</sub>\| · V<sub>DD</sub> |
| `snm/dice_snm_single_<corner>_full.ocn` | DC butterfly sweep, 221 points, `hysteresis` enabled |

### `corner_sweep/` — process corners at nominal V<sub>DD</sub>

The preceding generation: sizing × temperature × corner, with V<sub>DD</sub> fixed at 1.1 V.
SEU here uses a **coarse bracketing** search over a fixed charge list rather than bisection,
recording a `flipped` flag per injected charge instead of a converged Q<sub>crit</sub>. That
flip-rate formulation is what the notebook's three-way power/SEU/SNM trade-off plot uses.

### `nominal_sweep/` — TT corner only

The first generation: sizing × temperature at the TT corner, nominal supply. Superseded for
the paper, but its CSVs are still loaded by the notebook's corner-comparison section.

## Injection model

SEU strikes are modeled as a double-exponential current source on the struck node:

```
I(t) = Ipeak · (e^(-(t-td)/τ2) - e^(-(t-td)/τ1))
```

with τ<sub>1</sub> = 10 ps (rise), τ<sub>2</sub> = 150 ps (fall), t<sub>d</sub> = 1 ns, and
I<sub>peak</sub> = Q<sub>inj</sub> / 140 ps. All runs are in hold mode — wordline low, both
bitlines precharged — so the access transistors stay off and cannot influence the result.
Initial state is forced with Spectre nodesets, and solver tolerances are tightened
(`reltol=1e-4`, `vabstol=1e-7`, `iabstol=1e-13`) so the bisection does not chase numerical
noise near the threshold.

Dual-node injection is performed by driving two sources with equal magnitude simultaneously:
for the DICE cell, the same-polarity pairs Q1 + Q2 and Q1B + Q2B, which are the only pairs
with no independent restoring path.
