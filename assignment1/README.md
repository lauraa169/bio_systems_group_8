# # Epidemiological Model Assignment — Parameter Exploration

**Course**: KEN3170 — Multi-scale modeling of biological systems
**Group number**: [8]

---

## 1. Repository overview
- `analysis.ipynb` — main notebook containing all required sections (Setup, Part 1–3, Conclusions)
- `requirements.txt` — Python dependencies (numpy, matplotlib, pandas, scipy, seaborn)
- `README.md` — this file

**How to run**:

- `pip install -r requirements.txt` 
- open and run `analysis.ipynb` top to bottom

---

## 2. Part 1 — Parameter analysis function

### Function
`analyze_recovery_rates(beta, mu, N, I0, simulation_days)`

This function investigates how different recovery rates ($\gamma$) affect the outcome of the SIRD epidemic model. It runs a separate simulation for each recovery rate from **0.05 to 0.25** in increments of 0.05, while keeping the other model parameters fixed.


For each value of $\gamma$, the function calculates:
- the peak number of infected individuals,
- the day on which the infection peaks,
- the total number of deaths at the end of the simulation, and
- the basic reproduction number, $R_0 = \frac{\beta}{\gamma}$

The function also generates an epidemic curve for each recovery rate and returns the results as a pandas DataFrame.


For the SIRD simulation we reused the `run_sird_simulation(beta, gamma, mu, N=1000, I0=10, days=150, plot=False)` function from the Practical notebook, while also implementing an optional flag for plotting to avoid redundancy.


### Output
The resulting DataFrame contains one row for each recovery rate:

| Recovery Rate ($\gamma$) | Peak Infected | Peak Infected Day | Total Deaths | R₀ |
|---|---:|---:|---:|---:|
| 0.05 | ... | ... | ... | ... |
| 0.10 | ... | ... | ... | ... |
| 0.15 | ... | ... | ... | ... |
| 0.20 | ... | ... | ... | ... |
| 0.25 | ... | ... | ... | ... |
---

## 3. Part 2 — Scenario comparison
### Results
**Scenario A (High Transmission)**
| Recovery Rate ($\gamma$) | Peak Infected | Peak Infected Day | Total Deaths | $R_0$ |
| -----------------------: | ------------: | ----------------: | -----------: | ----: |
|                     0.05 |           521 |                21 |          285 |  8.00 |
|                     0.10 |           340 |                22 |          160 |  4.00 |
|                     0.15 |           213 |                24 |          103 |  2.67 |
|                     0.20 |           124 |                27 |           67 |  2.00 |
|                     0.25 |            63 |                30 |           43 |  1.60 |

**Scenario B (Low Transmission)**
| Recovery Rate ($\gamma$) | Peak Infected | Peak Infected Day | Total Deaths | $R_0$ |
| -----------------------: | ------------: | ----------------: | -----------: | ----: |
|                     0.05 |           284 |                46 |          266 |  4.00 |
|                     0.10 |            97 |                56 |          113 |  2.00 |
|                     0.15 |            16 |                70 |           35 |  1.33 |
|                     0.20 |             5 |                 0 |            4 |  1.00 |
|                     0.25 |             5 |                 0 |            1 |  0.80 |

---
---
### TODO:
- Which scenario is worse for public health, and why

---

## 4. Part 3 — Policy recommendations
- 4.1 Parameter impact analysis
- 4.2 Intervention analysis
- 4.3 Real-world application

---

## 5. Conclusions
