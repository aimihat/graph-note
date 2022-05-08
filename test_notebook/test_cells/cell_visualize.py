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
