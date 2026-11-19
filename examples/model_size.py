"""Model-size advisor: which variant gives the same quality for less water?

    python examples/model_size.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))   # run from a clone

from sklearn.datasets import make_classification  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402

from watttowater import compare  # noqa: E402

X, y = make_classification(n_samples=20000, n_features=20, n_informative=10, random_state=42)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)


def forest(trees):
    def job():
        m = RandomForestClassifier(n_estimators=trees, n_jobs=-1, random_state=42)
        return m.fit(X_tr, y_tr).score(X_te, y_te)      # test accuracy
    return job


compare({f"{t} trees": forest(t) for t in (25, 50, 100, 200)}, region="Virginia")
