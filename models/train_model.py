import os
import sys
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# ---------------------------------------------------------
# Make project root available to Python
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, PROJECT_ROOT)


# ---------------------------------------------------------
# Load database connection
# ---------------------------------------------------------

from backend.db import conn


# ---------------------------------------------------------
# Load training data
# ---------------------------------------------------------

query = """
SELECT
    latency,
    jitter,
    packet_loss,
    bandwidth,
    cpu_usage,
    memory_usage,
    link_status,
    traffic,
    scenario
FROM network_metrics
WHERE scenario IS NOT NULL
"""

df = pd.read_sql(query, conn)


print("\n========================================")
print("AI MODEL TRAINING")
print("========================================")

print(f"Total database records: {len(df)}")


# ---------------------------------------------------------
# Check whether data exists
# ---------------------------------------------------------

if df.empty:

    print("\n❌ No training data found.")

    print(
        "Generate network data before training "
        "the model."
    )

    sys.exit(1)


# ---------------------------------------------------------
# Clean scenario labels
# ---------------------------------------------------------

df["scenario"] = (
    df["scenario"]
    .astype(str)
    .str.strip()
    .str.upper()
)


# ---------------------------------------------------------
# Label mapping
# ---------------------------------------------------------

label_map = {

    "NORMAL": 0,

    "CONGESTION": 1,

    "HARDWARE_FAILURE": 2,

    "FIBRE_CUT": 3,

    "LINK_DOWN": 4

}


df["scenario"] = df["scenario"].map(
    label_map
)


# ---------------------------------------------------------
# Remove unknown scenarios
# ---------------------------------------------------------

df = df.dropna(
    subset=["scenario"]
).copy()


# ---------------------------------------------------------
# Convert label to integer
# ---------------------------------------------------------

df["scenario"] = df[
    "scenario"
].astype(int)


# ---------------------------------------------------------
# Display class distribution
# ---------------------------------------------------------

print("\nClass distribution:")

print(
    df["scenario"]
    .value_counts()
    .sort_index()
)


# ---------------------------------------------------------
# Feature columns
# ---------------------------------------------------------

features = [

    "latency",

    "jitter",

    "packet_loss",

    "bandwidth",

    "cpu_usage",

    "memory_usage",

    "link_status",

    "traffic"

]


# ---------------------------------------------------------
# Remove records with missing feature values
# ---------------------------------------------------------

df = df.dropna(
    subset=features
).copy()


# ---------------------------------------------------------
# Create X and y AFTER cleaning the data
# ---------------------------------------------------------

X = df[features]

y = df["scenario"]


print("\nFeatures used by model:")

for feature in features:

    print(
        f"  ✓ {feature}"
    )


print(
    f"\nTraining samples: {len(X)}"
)


# ---------------------------------------------------------
# Make sure all five classes exist
# ---------------------------------------------------------

required_classes = {
    0,
    1,
    2,
    3,
    4
}


available_classes = set(
    y.unique()
)


missing_classes = (
    required_classes -
    available_classes
)


if missing_classes:

    print(
        "\n⚠️ WARNING: Missing classes:"
    )

    reverse_map = {

        0: "NORMAL",
        1: "CONGESTION",
        2: "HARDWARE_FAILURE",
        3: "FIBRE_CUT",
        4: "LINK_DOWN"

    }

    for class_id in sorted(
        missing_classes
    ):

        print(
            f"  - {reverse_map[class_id]}"
        )

    print(
        "\nThe model cannot properly learn "
        "all five fault types until training "
        "data exists for each class."
    )

    sys.exit(1)


# ---------------------------------------------------------
# Train / Test split
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y

)


print(
    f"\nTraining set: {len(X_train)} samples"
)

print(
    f"Testing set:  {len(X_test)} samples"
)


# ---------------------------------------------------------
# Create Random Forest model
# ---------------------------------------------------------

model = RandomForestClassifier(

    n_estimators=200,

    random_state=42,

    class_weight="balanced",

    n_jobs=-1

)


# ---------------------------------------------------------
# Train model
# ---------------------------------------------------------

print(
    "\n🔄 Training Random Forest..."
)


model.fit(
    X_train,
    y_train
)


print(
    "✅ Model training completed."
)


# ---------------------------------------------------------
# Evaluate model
# ---------------------------------------------------------

y_pred = model.predict(
    X_test
)


accuracy = accuracy_score(
    y_test,
    y_pred
)


print(
    f"\nModel accuracy: "
    f"{accuracy * 100:.2f}%"
)


print(
    "\nClassification report:"
)


print(

    classification_report(

        y_test,

        y_pred,

        labels=[
            0,
            1,
            2,
            3,
            4
        ],

        target_names=[

            "NORMAL",

            "CONGESTION",

            "HARDWARE_FAILURE",

            "FIBRE_CUT",

            "LINK_DOWN"

        ],

        zero_division=0

    )

)


# ---------------------------------------------------------
# Save trained model
# ---------------------------------------------------------

model_path = os.path.join(

    PROJECT_ROOT,

    "models",

    "model.pkl"

)


joblib.dump(
    model,
    model_path
)


print(
    "\n========================================"
)

print(
    "✅ MODEL SAVED"
)

print(
    f"Location: {model_path}"
)

print(
    "========================================\n"
)