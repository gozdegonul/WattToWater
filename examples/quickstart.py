"""Quickstart: add ONE line to your code and see its water footprint.

    python examples/quickstart.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))   # run from a clone

from sklearn.datasets import make_classification  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402

from watttowater import track_water  # noqa: E402

X, y = make_classification(n_samples=20000, n_features=20, n_informative=10, random_state=42)


@track_water(region="Virginia")          # <- the one line
def train():
    model = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42)
    model.fit(X, y)
    return model


train()

# Any block of code works too:
with track_water("predict", region="Virginia"):
    RandomForestClassifier(n_estimators=50, n_jobs=-1, random_state=0).fit(X, y).predict(X)

print("\nEvery run was also appended to water_log.csv. Summarise it with:")
print("    python -m watttowater report water_log.csv --region Virginia")
