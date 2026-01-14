# ai/train_model.py

import random
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from ai.features import extract_features


def generate_synthetic_sample():
    # Generate tighter, more realistic market
    mid = random.uniform(95, 105)

    buy_orders = [
        {"price": round(mid - random.uniform(0, 3), 2), "quantity": random.randint(5, 80)}
        for _ in range(6)
    ]

    sell_orders = [
        {"price": round(mid + random.uniform(0, 3), 2), "quantity": random.randint(5, 80)}
        for _ in range(6)
    ]

    orderbook = {"buy_orders": buy_orders, "sell_orders": sell_orders}

    # Simulate real user order
    order = {
        "price": round(mid + random.uniform(-2, 2), 2),
        "quantity": random.randint(1, 40)
    }

    features = extract_features(orderbook, order)
    spread, imbalance, size, price_dist = features

    # Label logic now strongly reflects intuitive market behavior
    score = (
        -spread * 1.2 +
        imbalance * 1.5 -
        price_dist * 0.8 -
        size * 0.02 +
        random.gauss(0, 0.4)
    )

    label = 1 if score > 0 else 0
    return features, label



def main():
    X, y = [], []

    for _ in range(15000):
        features, label = generate_synthetic_sample()
        X.append(features)
        y.append(label)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"Model accuracy: {acc:.3f}")

    joblib.dump(model, "ai/model.pkl")
    print("Model saved to ai/model.pkl")


if __name__ == "__main__":
    main()
