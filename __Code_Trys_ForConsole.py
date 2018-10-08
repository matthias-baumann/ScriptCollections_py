from sklearn.datasets import make_classification
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import shuffle
import numpy as np

X, y1 = make_classification(n_samples=5, n_features=6, n_informative=2, n_classes=2, random_state=1)



y2 = shuffle(y1, random_state=1)
#Y = np.vstack((y1, y2)).T


print(y2)
print("")

forest = RandomForestClassifier(n_estimators=10, random_state=1).fit(X, y2)
X_pred = forest.predict(X)

print(X)
print("")
print(X_pred)
print("")

X_prob = forest.predict_proba(X)
print(X_prob)
print("")
X_pob_c1 = X_prob[:,0]
print(X_pob_c1)
