## Graphical Jupyter notebooks / Interactive DAGs / Interactive Airflow

Sub tagline: Interactive python DAGs (for ML and data pipelines, but could be sample data and send email or call api)

#### Problems we’re trying to solve
- Airflow can run production dags, but hard to develop the dag - edit a single component need to rerun. If you use Jupiter that works, but you lack the dag structure and it’s annoying to have two distinct environments and need to go back and forth.
- Airflow too slow for toying around bc need to run full pipeline, but structure is nice. Jupiter can run code interactively
- Everyone uses Jupyter notebooks, and yet the underlying tech hasn’t change in years.
- Notebook cells can be run in various orders, which is messy. Hard to make sure the current state of runtime variables is as intended.
- More often ML workflow have specific steps/stages that can be run independently of each other.
    - Notebook has the advantage that we can run them independently, but this makes it hard to keep track of what has been run & what was the state of the input variable at that time

#### Our solution
- Dev notebook style cells, that can use all the outputs… -> convert to cell that uses only the outputs that are used.
- Cells as graph nodes
    - Each cell defines input/output variables (e.g. @minput, @output)
    - Can connect individual inputs/outputs to individual (e.g. Audi software)
    - A cell knows whether it was run with the current version of its input or if it can be re-run.
        - Re-run only relevant parts or re-run all.
- Library of standard cells or tools, e.g. for visualisation.
- Imports at a root node

#### Difference with Orchest
- Think of it as a DAG Jupyter where nodes are cells, not notebooks
- Individual outputs surfaced?
    - Enables library of standard cells, based on standard outputs