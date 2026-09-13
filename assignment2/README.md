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


---

## 5. Requirements

The notebook uses:

- **Python**
- **COBRApy**
- Python's built-in `csv` module

Install the required dependency with:

```bash
pip install -r requirements.txt
```

---

## 6. Files required

Make sure the following files are located in the same directory as the notebook:

```text
analysis.ipynb
e_coli_core-1.json
KEN3170_Assignment_2026_e_coli_core_expression.csv
requirements.txt
README.md
```

The notebook will not be able to load the metabolic model or activity data if the corresponding files are moved to a different directory without updating the file paths in the notebook.
