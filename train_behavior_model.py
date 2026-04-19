import os
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, classification_report
import seaborn as sns

# Ensure directories exist
os.makedirs('models', exist_ok=True)
os.makedirs('static/img', exist_ok=True)

print("1. Generating Synthetic Behavioral Data...")
np.random.seed(42)

# Generate 5,000 synthetic records
# Features: [stress_points (0-5), low_scores (0-10)]
n_samples = 5000

# Steady Class (y=0): Low stress, low amount of 'low_scores'
steady_stress = np.random.normal(loc=0.5, scale=0.8, size=n_samples//2).clip(0, 5)
steady_scores = np.random.normal(loc=1.0, scale=1.5, size=n_samples//2).clip(0, 10)
steady_X = np.column_stack((steady_stress, steady_scores))
steady_y = np.zeros(n_samples//2)

# Needs Calm Class (y=1): High stress (>=2) OR High low_scores (>=4)
calm_stress = np.random.normal(loc=3.0, scale=1.2, size=n_samples//2).clip(0, 5)
calm_scores = np.random.normal(loc=5.0, scale=2.5, size=n_samples//2).clip(0, 10)
calm_X = np.column_stack((calm_stress, calm_scores))
calm_y = np.ones(n_samples//2)

# Combine and shuffle
X = np.vstack((steady_X, calm_X))
y = np.concatenate((steady_y, calm_y))

# Split training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("2. Training RandomForestClassifier...")
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Metrics
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print("-" * 30)
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=["Steady (0)", "Needs Calm (1)"]))

# Plot Confusion Matrix
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=["Steady", "Needs Calm"], yticklabels=["Steady", "Needs Calm"])
plt.title('Random Forest Confusion Matrix\nAccuracy: {:.2f}%'.format(acc * 100))
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')

# Save plot
plt.tight_layout()
plt.savefig('static/img/confusion_matrix.png')
print("3. Saved Confusion Matrix to static/img/confusion_matrix.png")

# Save model
joblib.dump(model, 'models/rf_behavior.pkl')
print("4. Model saved successfully to models/rf_behavior.pkl")
