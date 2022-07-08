import sys
from google.protobuf.json_format import MessageToJson

sys.path.append("../")
from graphnote.proto.classes import graph_pb2


# Create cells
cell_root = graph_pb2.Cell()
cell_root.uid = "cell_root"
cell_root.code = """
import matplotlib.pyplot as plt
# Import datasets, classifiers and performance metrics
from sklearn import datasets, metrics, svm
from sklearn.model_selection import train_test_split
"""

cell_data = graph_pb2.Cell()
cell_data.uid = "cell_data"
cell_data.code = """
digits = datasets.load_digits()

graphnote.out({"digits__different_name": digits})
"""
cell_data.out_ports.extend(
    [graph_pb2.Port(uid="1", name="digits__different_name")]
)  # can connect out-in with different names

cell_trainer = graph_pb2.Cell()
cell_trainer.uid = "cell_trainer"
cell_trainer.code = """
# flatten the images
n_samples = len(INPUT["digits"].images)
data = digits.images.reshape((n_samples, -1))

# Create a classifier: a support vector classifier
clf = svm.SVC(gamma=0.001)

# Split data into 50% train and 50% test subsets
X_train, X_test, y_train, y_test = train_test_split(
    data, digits.target, test_size=0.5, shuffle=False
)

# Learn the digits on the train subset
clf.fit(X_train, y_train)

# Predict the value of the digit on the test subset
predicted = clf.predict(X_test)

graphnote.out(
    {
        "predicted": predicted,
        "clf": clf,
        "X_test": X_test,
        "y_test": y_test,
    }
)
"""
cell_trainer.in_ports.extend([graph_pb2.Port(uid="2", name="digits")])
cell_trainer.out_ports.extend(
    [
        graph_pb2.Port(uid="3", name="X_test"),
        graph_pb2.Port(uid="4", name="predicted"),
        graph_pb2.Port(uid="5", name="y_test"),
        graph_pb2.Port(uid="6", name="clf"),
    ]
)
cell_trainer.output = "This is the output for the trainer cell."

cell_visualize = graph_pb2.Cell()
cell_visualize.uid = "cell_visualize"
cell_visualize.code = """
# Below we visualize the first 4 test samples and show their predicted digit value in the title.

_, axes = plt.subplots(nrows=1, ncols=4, figsize=(10, 3))
for ax, image, prediction in zip(axes, INPUT["X_test"], INPUT["predicted"]):
    ax.set_axis_off()
    image = image.reshape(8, 8)
    ax.imshow(image, cmap=plt.cm.gray_r, interpolation="nearest")
    ax.set_title(f"Prediction: {prediction}")

print(
    f'Classification report for classifier {INPUT["clf"]}:\n'
    f'{metrics.classification_report(INPUT["y_test"], INPUT["predicted"])}\n'
)
"""
cell_visualize.in_ports.extend(
    [
        graph_pb2.Port(uid="7", name="X_test"),
        graph_pb2.Port(uid="8", name="predicted"),
        graph_pb2.Port(uid="9", name="y_test"),
        graph_pb2.Port(uid="10", name="clf"),
    ]
)

# Create connections
connections = [
    graph_pb2.Connection(
        from_port=cell_data.out_ports[0], to_port=cell_trainer.in_ports[0]
    ),
]
for from_, to_ in zip(cell_trainer.out_ports, cell_visualize.in_ports):
    connections.append(graph_pb2.Connection(from_port=from_, to_port=to_))

# Create dag
dag = graph_pb2.Graph()
dag.cells.extend([cell_data, cell_trainer, cell_visualize])
dag.root.CopyFrom(cell_root)
dag.connections.extend(connections)

# Write the new dag back to disk.
f = open("test_dag.gnote", "wb")
f.write(dag.SerializeToString())
f.close()

# For debugging purposes, save as json also

json_obj = MessageToJson(dag)
f = open("test_dag.json", "w")
f.write(json_obj)
f.close()
