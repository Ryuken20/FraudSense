import pickle
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

SCALER_PATH    = "saved_scaler.pkl"
FEATURES_PATH  = "saved_features.pkl"
AE_MODEL_PATH  = "saved_autoencoder.pt"
XGB_MODEL_PATH = "saved_xgb.pkl"

class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 16)
        )
        self.decoder = nn.Sequential(
            nn.Linear(16, 32), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(32, 64), nn.ReLU(), nn.Linear(64, input_dim)
        )
    def forward(self, x): return self.decoder(self.encoder(x))

ae        = torch.load(AE_MODEL_PATH, weights_only=False)
ae.eval()
scaler    = pickle.load(open(SCALER_PATH,    "rb"))
features  = pickle.load(open(FEATURES_PATH,  "rb"))
model_xgb = pickle.load(open(XGB_MODEL_PATH, "rb"))

print("📂 Loading sample data...")
df = pd.read_csv("../data/raw/train_transaction.csv")
df = df[features + ["isFraud"]].copy()
df.fillna(0, inplace=True)
df_sample = df.sample(n=50000, random_state=42)

X_scaled = scaler.transform(df_sample[features].values)
X_tensor = torch.FloatTensor(X_scaled)
with torch.no_grad():
    recon = ae(X_tensor)
recon_errors = torch.mean((X_tensor - recon) ** 2, dim=1).numpy().reshape(-1, 1)

X_hybrid = np.column_stack([X_scaled, recon_errors])
y_true   = df_sample["isFraud"].values
y_pred   = model_xgb.predict(X_hybrid)

precision = precision_score(y_true, y_pred, zero_division=0)
recall    = recall_score(y_true, y_pred, zero_division=0)
f1        = f1_score(y_true, y_pred, zero_division=0)
cm        = confusion_matrix(y_true, y_pred)

print("\n" + "="*55)
print("   HYBRID AUTOENCODER + XGBOOST RESULTS")
print("="*55)
print(f"  {'Metric':<20} {'Baseline':>10} {'Hybrid':>10}")
print("-"*55)
print(f"  {'Features Used':<20} {'6':>10} {len(features)+1:>10}")
print(f"  {'Precision':<20} {'3.08%':>10} {precision*100:>9.2f}%")
print(f"  {'Recall':<20} {'5.82%':>10} {recall*100:>9.2f}%")
print(f"  {'F1 Score':<20} {'4.03%':>10} {f1*100:>9.2f}%")
print(f"  {'Fraud Caught':<20} {'54':>10} {cm[1][1]:>10,}")
print(f"  {'Fraud Missed':<20} {'874':>10} {cm[1][0]:>10,}")
print("="*55)
print(f"\n  True Negatives  : {cm[0][0]:,}  (clean correctly cleared)")
print(f"  False Positives : {cm[0][1]:,}  (clean wrongly flagged)")
print(f"  False Negatives : {cm[1][0]:,}  (fraud missed ❌)")
print(f"  True Positives  : {cm[1][1]:,}  (fraud caught ✅)")
print("="*55)
