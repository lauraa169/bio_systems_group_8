# Assignment 2 — Metabolic Modeling

**Course**: KEN3170 — Multi-scale modeling of biological systems  
**Assignment**: Assignment 2 — Metabolic Modeling
**Group number**: [8]

---

## 1. Repository overview

- `analysis.ipynb` — main notebook containing the metabolic modeling analysis and COBRApy implementation
- `requirements.txt` — Python dependency required to run the notebook
- `e_coli_core-1.json` — E. coli core metabolic model used in the notebook
- `KEN3170_Assignment_2026_e_coli_core_expression.csv` — reaction maximal activity data used to constrain the model
- `README.md` — this file

**How to run**:

```bash
pip install -r requirements.txt
```

Then open `analysis.ipynb` in Jupyter Notebook, JupyterLab, or another compatible notebook environment and run the cells from top to bottom.

---

## 2. Part 1 — Visualizing reaction maximal activity data
a) No, in the case of E.Coli, we are looking at a complex system with branching, cyclic, converging pathways. Additionally flux values are not required to be equal, because sume reactions (e.g. PGI) can also carry flux in the reverse direction oir receive metabolites through alternate routes. Therefore one molecule can be sent into several different pathways. For example the g6p_c from the reaction GLCpts (21.1) can be sent to either PGI (11.1) or G6PDH2r (6.5) or both. Another example would be the reactions around Pyruvate (pyr_c), which can be used in several reactions (PYK, PDH, PPS, LDH_D, etc) depending on the system's needs.

b) The two possible values that the grey arrows can have are 0.00 or n.d. The difference is that 0.00 means that data for this reaction was collected and it was 0.00, which might mean that that gene is not expressed in the cell. While n.d. means "no data", which moight mean that the data for this reaction is not in the loaded dataset.

## 3. Part 2 — Adjusting upper and lower flux bounds

This part establishes activity constraints in the E. coli core metabolic model using COBRApy.

### Loading the model

The E. coli core model is loaded using:

```python
model = cobra.io.load_json_model("e_coli_core-1.json")
```

The reaction activity data is read from:

```text
KEN3170_Assignment_2026_e_coli_core_expression.csv
```

The reaction IDs and their corresponding maximal activities are stored in the `activity_constraints` dictionary.

### Applying the activity constraints

For each reaction with available activity data:

- **ATPM** has its lower flux unchanged. (upper doesn't change either do to the fact that maximal activity for ATPM is not mentioned)
- **Reversible reactions** have their lower and upper bounds set to `-value` and `+value`.
- **Irreversible reactions** have their upper bound set to `+value`, while their lower bound remains unchanged.
- **Reactions without activity data** retain their default constraints.

The code identifies reversible reactions by checking whether their existing lower bound is below zero:

```python
elif reaction.lower_bound < 0:
    reaction.lower_bound = -value
    reaction.upper_bound = value
```

For irreversible reactions, only the upper bound is changed:

```python
else:
    reaction.upper_bound = value
```

### Glucose exchange reaction

The glucose exchange reaction `EX_glc__D_e` is treated separately. Its pre-existing maximal absolute flux constraint is removed by setting:

```python
reaction.lower_bound = -1000
reaction.upper_bound = 1000
```

This allows the glucose exchange reaction to use the high absolute default flux bound.

### Output

The notebook prints a table containing the lower and upper flux bounds for every reaction:

| Reaction ID | Lower Bound | Upper Bound |
|---|---:|---:|
| ... | ... | ... |

---

## 4. Part 3 — Flux Balance Analysis

a) First, we optimizes the model using FBA with the `model.optimize()` function, which computes the optimal flux distribution that maximizes the objective function (biomass production). Then we print the maximal biomass production value, which is: 0.8732862458582367


b) for part b, we set the absolute flux of the glucose exchange reaction to 5, but keeping in mind that in cobrapy the intake in the cell is defined using a negative sign, so it's -5. 
This constraint describes a hard upper limit for the intake rate of glucose into the cell (extracellular). Whereas the other expression-based constraints decribe bounds on the internal reaction rates of the metabolites in the cell (intracellular).


c) We then reoptimize the model with the new glucose exchange constraint and get the follwoing new biomass production value: 0.41559777509290663.
The reason for this is that the model in this case has less substrate and energy available for the biomass reaction.

---

## 5. Part 4 - Glucose Uptake and Maximal Biomass

a) The code iterates through glucose uptake rates from 1 to 15.1 mmol/gDW/h in steps of 0.1. For each rate:

The lower bound of EX_glc__D_e is set to -rate (negative because uptake is modeled as a negative flux).

The model is optimized using:
```python
model.optimize()
``` 

The resulting objective value (maximal biomass production) is stored.

The collected values are then plotted with:

- X-axis: Glucose Uptake Rate (mmol/gDW/h)

- Y-axis: Maximal Biomass Production (1/h)

The plot shows linear growth until the glucose uptake rate reaches approximately 10 mmol/gDW/h. Beyond this point, the curve begins to flatten and becomes constant.

b)No. The growth rate does not increase indefinitely with increasing glucose exchange reaction flux bound.

Maximal biomass production increases linearly (dB=0.009166) with glucose uptake until the rate reaches 9.4mmol/gDW/h then increases again (dB=0.004591) until it reaches 10.8 mmol/gDW/h. After that, the curve flattens, meaning that additional glucose does not translate into additional biomass.

c) To determine why the growth curve changes, the model is optimized at the glucose uptake rate around 9.4mmol/gDW/h, and the fluxes of all exchange reactions are outputed.

Two observations:

- EX_o2_e equals -20.55, meaning that the oxygen uptake has hit its upper bound and the cell cannot take up any more oxygen.

- EX_ac_e secretion begins at 9.4mmol, meaning the carbon is being being rerouted to acetate formation, slowing the biomass production. Later, at 10.7mmol glucose uptake, the acetate exchange plateaus at 2.5 due to the optimal stochiometric balance of reactions PTAr, ACKr and EX_ac_e

Together, these two facts show that the growth limitation at high glucose uptake rates is caused by the oxygen uptake constraint and limitations of acetate secretion, not by glucose availability.

---

## 6. Requirements

The notebook uses:

- **Python**
- **COBRApy**
- Python's built-in `csv` module

Install the required dependency with:

```bash
pip install -r requirements.txt
```

---

## 7. Files required

Make sure the following files are located in the same directory as the notebook:

```text
analysis.ipynb
e_coli_core-1.json
KEN3170_Assignment_2026_e_coli_core_expression.csv
requirements.txt
README.md
```

The notebook will not be able to load the metabolic model or activity data if the corresponding files are moved to a different directory without updating the file paths in the notebook.
