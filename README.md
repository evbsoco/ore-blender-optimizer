# Ore Blending Optimizer

A Python-based ore blending optimization tool that automatically selects ore piles from an inventory to create a vessel blend while satisfying **Ni, Fe, and tonnage requirements**.

The optimizer uses a **Mixed-Integer Linear Programming (MILP)** model formulated with **PuLP** and solved using the **CBC (COIN-OR Branch and Cut) solver**.

## Features

* Import ore inventory data from Excel.
* Automatically select ore piles for vessel blending.
* Enforce vessel capacity requirements.
* Enforce Ni and Fe grade requirements.
* Optimize the selected blend based on grade compliance.
* Minimize the total selected tonnage after satisfying grade objectives.
* Calculate the resulting blend tonnage.
* Calculate weighted-average Ni and Fe grades.
* Evaluate the final blend against vessel specifications.

## How It Works

The optimizer takes an inventory of available ore piles and the target vessel specifications as inputs.

The general workflow is:

```text

Input Vessel Specifications
		↓
Inventory Excel File
		↓
Validate Inventory
		↓
Load Ore Piles
		↓
Build MILP Optimization Model
		↓
Solve Using CBC
		↓
Validate Optimized Blend
		↓
Display Selected Piles
		↓
Calculate Final Blend Grades and Tonnage
```

Each pile is treated as a binary decision:

```text
x_i = 1  → pile i is selected
x_i = 0  → pile i is not selected
```

The optimizer searches for a combination of available piles that satisfies the vessel requirements while optimizing the blending objectives.

## Optimization Objectives

The optimizer uses a prioritized optimization approach.

1. Optimize Grade Compliance

The first objective is to minimize the normalized deviation/excess associated with the Ni and Fe requirements. This prioritizes finding a blend that best satisfies the required vessel specifications.

2. Minimize Selected Tonnage

After determining the best achievable grade compliance, the optimizer minimizes the total WMT of the selected piles while maintaining the required conditions.

This results in a blend that is both **ore grade compliant and operationally efficient in terms of selected tonnage**.

## Input Requirements

The application accepts an Excel inventory file with a specific worksheet and column format. The required inventory structure, column names, data types, and formatting requirements are documented separately in: [**INVENTORY-REQUIREMENTS.md**](https://github.com/evbsoco/ore-blender-optimizer/blob/master/INVENTORY-REQUIREMENTS.txt)

The inventory must contain the required information for each available ore pile, including relevant:

* Pile identification
* Contractor
* Stockyard/location
* WMT
* Ni grade
* Fe grade
* Other required inventory attributes

## Vessel Inputs

The optimizer requires vessel-specific specifications, including parameters such as:

* Vessel name
* Material type
* Target capacity
* Capacity threshold
* Ni requirement
* Fe requirement

These specifications define the constraints and optimization targets for the blending problem.

## Output

The optimizer produces an optimized pile selection and provides information such as:

* Selected piles
* Total selected WMT
* Weighted-average Ni grade
* Weighted-average Fe grade
* Vessel requirements
* Optimization result/status

The resulting blend can then be evaluated against the vessel specifications.

## Optimization Solver

The optimization model is formulated using **PuLP**, a Python optimization modeling library, and solved using **CBC (COIN-OR Branch and Cut)**.

PuLP is used to define the:

* Decision variables
* Objective functions
* Constraints
* MILP model

CBC performs the actual mathematical optimization and searches for the best feasible combination of piles.

The relationship between the application, PuLP, and CBC is:

```text

Python Application
	↓
PuLP
	↓
MILP Model
	↓
CBC
	↓
Optimized Pile Selection
```

## Project Structure

```text

Ore-Blender-Optimizer/
│
├── main.py
├── app/
│   ├───── interface.py
│   └───── loader.py
│
├── config/
│   └───── config.py
│
├── models/
│   ├───── inventory.py
│   ├───── orepile.py
│   └───── vessel.py
│
├── optimizer/
│   └───── optimizer.py
│
├── INVENTORY-REQUIREMENTS.md
└── README.md
```

## Current Status

The project has progressed from a manual ore blending calculator to an **automated ore blending optimization tool**. The current optimizer can automatically determine a pile combination based on vessel capacity and Ni/Fe requirements.

## Limitations

The current optimization model may not yet account for all real-world operational considerations. Potential limitations include:

* Operational accessibility of piles
* Equipment availability
* Stockyard location constraints
* Contractor-specific restrictions
* Blending sequence
* Expected assay/grade variability
* Partial pile consumption

## Planned Features

Future development will focus on expanding the optimizer from a single-vessel blending tool into a more comprehensive inventory and operational planning system.

* Excel export of optimized blending plans
* Desktop graphical user interface (GUI)
* Operational constraints
* Improved infeasibility handling
* Stockyard management integration
* Multi-vessel optimization
* Inventory optimization

## Future Vision

The long-term goal is to develop an **intelligent ore blending optimization system** that does not only determine the mathematically optimal blend, but also considers real-world mining and stockyard operations. The system is intended to eventually integrate:

**Ore Quality + Inventory + Vessel Requirements + Operational Constraints**

to generate blending plans that are both **ore grade compliant and operationally practical**.

