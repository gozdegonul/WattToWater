# ml_job.py - Gerçek bir makine öğrenmesi işinin su ayak izi (Adım 5)
#
# Gerekli: py -m pip install scikit-learn

from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from aquameter import measure, report

# Veri: scikit-learn'in ürettiği yapay veri (internetten indirmiyoruz).
# Ölçümün dışında hazırlıyoruz, sadece EĞİTİMİN suyunu ölçeceğiz.
X, y = make_classification(
    n_samples=20000, n_features=20, n_informative=10, random_state=42
)
# Eğitim ve test verisini baştan ayırıyoruz; model test verisini eğitimde görmez.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


def job():
    model = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)
    return model.score(X_test, y_test)    # test doğruluğu


if __name__ == "__main__":
    m = measure(job)
    print(f"Test doğruluğu   : {m['result']:.3f}")
    report(m)
