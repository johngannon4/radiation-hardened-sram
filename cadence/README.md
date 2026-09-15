# Cadence library

- **`MemoryDesignFinalProject/`** — a Cadence OpenAccess library holding every schematic and
  symbol used in the paper. It is committed as a single library directory because that is what
  Virtuoso expects: cells have to stay as direct children of the library folder, so they are
  grouped by naming convention here rather than by subdirectory.
- **`ade_states/`** — the saved ADE L simulation states, collected into one
  `<lib>/<cell>/spectre/<state>/` tree.

The states were originally saved into each cell's own folder, which left thirty near-identical
state trees nested inside the library and three byte-identical copies of the same state. They
are consolidated here into the single shared tree that ADE expects, which also keeps every path
short enough to clone on Windows without long-path support.

## Opening it

The library needs a `cds.lib` entry pointing at the library directory. `cds.lib` is deliberately
not committed, since the rest of its contents are site-specific:

```
DEFINE MemoryDesignFinalProject ./cadence/MemoryDesignFinalProject
```

Load a saved state from ADE with *Session → Load State*, set **From: Directory**, and point it at
`cadence/ade_states`. ADE resolves the state for the open cellview from there.

**The PDK is not included.** Every schematic instantiates devices from Cadence's GPDK045
(`g45n1svt` / `g45p1svt`), and the OCEAN scripts reference the model file
`gpdk045/models/spectre/gpdk045.scs`. Without a GPDK045 installation the schematics will open
but will not netlist or simulate.

## Cells

**Bitcells** — the four topologies under comparison. Each has a schematic and a symbol, so it
can be instantiated in the testbenches below.

| Cell | Topology |
|---|---|
| `6T_SRAM_Bitcell` | Standard 6T, unhardened baseline |
| `12T_DICE_Bitcell` | 12T DICE, dual interlocked storage |
| `RSP_14T_Bitcell` | 14T RSP, 3:1 driver-to-pull-up sizing on N0–N3 |
| `10T_Quattro` | 10T Quatro, N2/N4 upsized to 240 nm for write-ability |

Note the spelling: the cell is named `10T_Quattro` in the library, while the paper and the
literature call the topology *Quatro*. The cell name is left alone because the testbenches
instantiate it by name.

**Periphery**

| Cell | Purpose |
|---|---|
| `Write_Driver` | Bitline write driver |
| `Bitline_Conditioning` | Precharge / equalization |
| `Latch_Comparator_Amp` | Latch-type sense amplifier used in the read-access testbenches |

**Testbenches** — one per metric, per topology. Saved states live in
`ade_states/MemoryDesignFinalProject/<cell>/spectre/<state_name>/`. A dash means the schematic is
committed without a saved state, so the analyses have to be set up by hand.

| Metric | Cell | Saved ADE states |
|---|---|---|
| SEU / critical charge | `6T_SRAM_Bitcell_SEU` | `SEU` |
| | `12T_DICE_Bitcell_SEU` | `SEU_Testbench`, `SEU_Nodes`, `SEU_Double_Node`, `Automation_Testbench` |
| | `RSP_14T_Bitcell_SEU` | `Single_Node_SEU`, `Double_Node_SEU` |
| | `10T_Quattro_SEU` | `Single_node_D`, `Dual_Node` |
| Static noise margin | `12T_DICE_Bitcell_SNM` | `SNM` |
| | `10T_Quattro_SNM` | `SNM` |
| | `6T_SRAM_SNM`, `RSP_14T_SNM` | — |
| Leakage power | `6T_SRAM_Bitcell_Power`, `12T_DICE_Bitcell_Power`, `RSP_14T_Bitcell_Power`, `10T_Quattro_Power` | `Static_Power` |
| Read access time | `6T_Read_Access`, `RSP_14T_Read_Access` | `Read1`, `50mV_Read` |
| | `12T_DICE_Read_Access` | `Read0`, `Read1`, `50mV_Read` |
| | `10T_Quatro_Read_Access` | `Read0`, `50mV_Read` |
| Functional verification | `6T_Bitcell_Functional_Verification_Testbench` | `Functional_Verification_Sim_Setup` |
| | `12T_DICE_Bitcell_Functional_Verification_Testbench` | `12T_DICE_Verification` |
| | `10T_Quattro_Bitcell_Functional_Verification_Testbench` | `Verification`, `12T_DICE_Verification` |
| | `14T_Bitcell_Functional_Verification_Testbench` | — |
| Dynamic power | `Bitcell_Dynamic_Power_Testbench` | `Dynamic_Power`, `12T_DICE_Verification` |

The `50mV_Read` states are the read-access measurement from the paper: wordline assertion to a
50 mV bitline differential, with both bitlines precharged to V<sub>DD</sub> and a 10 fF load.

Two states had been saved against cell names that were later renamed —
`Bitcell_Functional_Verification_Testbench` and `Bitcell_Power_Testbench`. Their `ADE_state.info`
now names the cells those testbenches became (`6T_Bitcell_Functional_Verification_Testbench` and
`Bitcell_Dynamic_Power_Testbench`), so they resolve against cells that exist in the library.

`12T_DICE_Bitcell_SEU` is the cell driven by the OCEAN sweeps in [`../ocean/`](../ocean/): its
`Automation_Testbench` state defines the `wn_store` / `wp_store` / `wn_access` design variables
and the four `Qinj`/`Ipeak` injection variables that the scripts overwrite on each run.
