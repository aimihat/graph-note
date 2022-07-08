MVP Work:

1. Isolate cell environments:
    - if running in a single IPython kernel, must wrap all cells in a function -> with inputs/outputs, to have an independent variable scope.
    - Alternatively, write output artefacts to a local store & reset kernel before each cell + add imports


original cell code:
```python
x_test, y_test = datasets
prediction = model(x_test)
error = sum(y_test - prediction)
dag.out(error, name="error")
```

converted cell code:
```python
def cell(datasets, model):
    x_test, y_test = datasets
    prediction = model(x_test)
    error = sum(y_test - prediction)
    dag.out(error, name="error")  # dag is variable store...
```


2. Detect which variables are used and not defined: cell inputs. outputs must be explicitly marked
3. Implement DAG connections and use them in runner.
