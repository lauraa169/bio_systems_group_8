Assignment
# 1. Open pathogen_infection model and run for a duration of 2h. Screenshot initial and every 30 min. Describe how the infected region spreads and how the tissue deforms.

walls become less stiff -> Cells become rounder

# 2. In the model files (Github repo – Models – Infection – infection.cpp9: Read CellHouseKeeping. In your own words: how is a cell's wall stiffness reduced as a function of its chemical level? What does the pathogen do differently?

- The chemical level is first scaled by dividing it by 0.5. It is then capped at 1.2. 
- if chem level is >0.1 wall stiffness is reduceed linearly based on the chem level `stiffness_inf = 3 - (patho_chem_level)`
- cell type 2 is not affected
	-> they enlarge and divide

# 3. In the model files (Github repo – Models – Infection – infection.cpp9: Read CelltoCellTransport. How is the diffusion coefficient defined? Explain the feedback loop this creates and sketch it: chemical lowers stiffness, lower stiffness raises diffusion, faster diffusion spreads the chemical. Is this positive or negative feedback?

`diffusionCoef = 0.00001 / stiffness` -> lower stiffness produces higher diffusion coeff.

1. Chemical lowers stiffness
2. diffusion coeff. increases
3. chemical spreads faster to neighbours
4. more cells receive the pathogen chemical
5. more walls weaken
6. more spreading -> positive feedback

# 4. Raise and lower rel_cell_div_threshold. How does it change how fast the pathogen population expands? Document two runs.

The relevant code is the following:
`if (c->Area() > par->rel_cell_div_threshold * c->BaseArea()) { c->Divide(); }`

`rel_cell_div_threshold` determines how large a cell has to become relative to its original ('base') area before it divides.

The documented runs and conclusions are summed up in the table below, relative to the base case `rel_cell_div_threshold = 2`.

| Run | Threshold | Observation                                                                 |
| --- | --------: | --------------------------------------------------------------------------- |
| 1   |       Low | More frequent cell division and faster expansion of the infected population |
| 2   |      High | Less frequent division and slower population expansion                      |

## Experiment Results

## Experiment Results

### Initial state

<p align="center">
  <img src="assignment5/imgs/00_base.png" width="400">
</p>

### High division threshold

| 30 min | 60 min | 90 min | 120 min |
|:------:|:------:|:------:|:-------:|
| <img src="assignment5/imgs/high_30.png" width="180"> | <img src="assignment5/imgs/high_60.png" width="180"> | <img src="assignment5/imgs/high_90.png" width="180"> | <img src="assignment5/imgs/high_120.png" width="180"> |

### Low division threshold

| 30 min | 60 min | 90 min | 120 min |
|:------:|:------:|:------:|:-------:|
| <img src="assignment5/imgs/low_30.png" width="180"> | <img src="assignment5/imgs/low_60.png" width="180"> | <img src="assignment5/imgs/low_90.png" width="180"> | <img src="assignment5/imgs/low_120.png" width="180"> |


# 5. What is a fundamental difference regarding cell neighbours in this model compared to all other models that you have worked with so far? 

# 6. The plant evolves a defense: cells above a chemical threshold stiffen their walls. Describe in pseudocode where in CellHouseKeeping this would go and what sign of feedback it adds. Do not implement it. Pseudocode for the different sections is enough!
