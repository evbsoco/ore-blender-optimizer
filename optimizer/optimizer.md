\# Ore Blending Optimizer



This folder contains the mathematical optimization component of the Ore Blending Optimizer project.



The optimizer uses \*\*Mixed-Integer Linear Programming (MILP)\*\* to identify suitable combinations of available ore stockpiles while satisfying required blending specifications.



\## Purpose



The optimizer determines which stockpiles should be selected for a vessel or blend based on defined requirements such as:



\- Target tonnage

\- Target ore grades

\- Available inventory



Each stockpile is treated as a selectable unit, allowing the optimizer to evaluate different combinations of available stockpiles.



\## Optimization Approach



The optimizer represents each stockpile with a binary decision variable:



\\\[

x\_i \\in \\{0,1\\}

\\]



where:



\- \\(x\_i = 1\\) — the stockpile is selected

\- \\(x\_i = 0\\) — the stockpile is not selected



The selected stockpiles are evaluated together to determine the resulting blend tonnage and weighted-average grades.



The optimization problem consists of:



1\. \*\*Decision variables\*\* — determine which stockpiles are selected.

2\. \*\*Constraints\*\* — define which combinations are acceptable.

3\. \*\*Objective function\*\* — determines which feasible combination is preferred.



\## Weighted-Average Grades



For a selected set of stockpiles, the resulting grade is calculated using the weighted average:



\\\[

G =

\\frac{\\sum\_i W\_iG\_i}

{\\sum\_i W\_i}

\\]



where:



\- \\(G\\) = resulting blend grade

\- \\(W\_i\\) = tonnage of stockpile \\(i\\)

\- \\(G\_i\\) = grade of stockpile \\(i\\)



This calculation is applied independently to the relevant ore-quality parameters.



\## Constraints



The optimizer can impose constraints on the resulting blend, such as:



\### Tonnage



The total selected tonnage must satisfy the vessel's required capacity or target range.



\### Grade



The resulting grade must satisfy the specified grade limits.



For example, a maximum acceptable grade constraint can be represented as:



\\\[

G \\leq G\_{\\text{target}} + T

\\]



where:



\- \\(G\_{\\text{target}}\\) = target grade

\- \\(T\\) = permitted tolerance



\## Objective



The objective function determines which feasible blend is preferred when multiple combinations satisfy the constraints.



The optimizer can prioritize criteria such as:



\- Minimizing deviation from target grades

\- Minimizing excess grade

\- Minimizing or controlling selected tonnage



The objective and constraints are kept separate so that the optimization strategy can be modified without changing the underlying inventory and vessel models.



\## Stockpile Selection



The current optimization approach treats stockpiles as complete units.



For example:



```text

Stockpile A → Select / Do not select

Stockpile B → Select / Do not select

Stockpile C → Select / Do not select

```



The optimizer therefore searches for a combination of available stockpiles that produces a feasible blend.



\## Solver



The optimization model is implemented using \*\*PuLP\*\*, which provides the interface for defining the MILP model, variables, constraints, and objective function.



The general workflow is:



```text

Inventory

&#x20;   ↓

Available Stockpiles

&#x20;   ↓

Create Decision Variables

&#x20;   ↓

Build Grade \& Tonnage Expressions

&#x20;   ↓

Apply Constraints

&#x20;   ↓

Define Objective

&#x20;   ↓

Solve MILP

&#x20;   ↓

Retrieve Selected Stockpiles

&#x20;   ↓

Evaluate Result

```



\## Future Development



The optimizer is intended to support increasingly realistic mining and operational requirements, including:



\- Multiple vessel and additional vessel specifications

\- Stockyard restrictions

\- Material availability constraints

\- Contractor or source restrictions

\- More detailed operational constraints

\- Multiple optimization objectives

\- Improved blend selection strategies



The optimizer is designed to remain modular so that these requirements can be added as the project develops.

