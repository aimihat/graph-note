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