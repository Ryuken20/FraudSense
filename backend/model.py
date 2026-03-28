import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import torch
import torch.nn as nn
import pickle, os, sys


# ── Paths ──────────────────────────────────────────────────────
SCALER_PATH    = "saved_scaler.pkl"
FEATURES_PATH  = "saved_features.pkl"
THRESHOLD_PATH = "saved_threshold.pkl"
AE_MODEL_PATH  = "saved_autoencoder.pt"
XGB_MODEL_PATH = "saved_xgb.pkl"


ALL_FEATURES = [
    "TransactionAmt",
    "card1", "card2", "card3", "card5",
    "dist1", "dist2",
    "C1", "C2", "C6", "C13",
    "D1", "D10", "D15",
    "addr1", "addr2",
]


# ── Autoencoder Definition ─────────────────────────────────────
class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(64, 32),        nn.ReLU(),
            nn.Linear(32, 16)
        )
        self.decoder = nn.Sequential(
            nn.Linear(16, 32), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(32, 64), nn.ReLU(),
            nn.Linear(64, input_dim)
        )
    def forward(self, x):
        return self.decoder(self.encoder(x))


def train():
    print("📂 Loading dataset...")
    df = pd.read_csv("../data/raw/train_transaction.csv")

    available = [f for f in ALL_FEATURES if f in df.columns]
    print(f"✅ Found {len(available)} features")

    df = df[available + ["isFraud"]].copy()
    df.fillna(0, inplace=True)
    df = df.sample(n=100000, random_state=42)

    X, y = df[available], df["isFraud"]
    print(f"📊 Fraud: {y.sum():,} ({y.mean()*100:.2f}%) | Total: {len(df):,}")

    # ── SMOTE ──────────────────────────────────────────────────
    print("\n⚖️  Applying SMOTE...")
    sm = SMOTE(random_state=42)
    X_res, y_res = sm.fit_resample(X, y)
    print(f"✅ After SMOTE → Fraud: {y_res.sum():,} | Clean: {(y_res==0).sum():,}")

    # ── Scale ───────────────────────────────────────────────────
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X_res)

    # ══════════════════════════════════════════════════════════
    # PART 1: Autoencoder on NORMAL only
    # ══════════════════════════════════════════════════════════
    print("\n🧠 [1/2] Training Autoencoder...")
    X_normal  = torch.FloatTensor(X_scaled[y_res == 0])
    ae        = Autoencoder(input_dim=len(available))
    optimizer = torch.optim.Adam(ae.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    best_loss, patience, pat_count = float("inf"), 7, 0

    for epoch in range(80):
        ae.train()
        perm   = torch.randperm(len(X_normal))
        losses = []
        for i in range(0, len(X_normal), 512):
            batch = X_normal[perm[i:i+512]]
            optimizer.zero_grad()
            loss  = criterion(ae(batch), batch)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())

        avg_loss = np.mean(losses)
        scheduler.step()

        if (epoch + 1) % 10 == 0:
            print(f"  Epoch {epoch+1:>2}/80 | Loss: {avg_loss:.6f}")

        if avg_loss < best_loss - 1e-6:
            best_loss, pat_count = avg_loss, 0
            torch.save(ae.state_dict(), AE_MODEL_PATH + ".best")
        else:
            pat_count += 1
            if pat_count >= patience:
                print(f"  ⏹️  Early stopping at epoch {epoch+1}")
                break

    # Restore best weights and save FULL model
    ae.load_state_dict(torch.load(AE_MODEL_PATH + ".best", weights_only=True))
    ae.eval()

    sys.modules["__main__"].Autoencoder = Autoencoder
    torch.save(ae, AE_MODEL_PATH)
    print("✅ Autoencoder saved!")

    # ── Reconstruction errors as extra feature ─────────────────
    X_res_tensor = torch.FloatTensor(X_scaled)
    with torch.no_grad():
        recon = ae(X_res_tensor)
    recon_errors = torch.mean((X_res_tensor - recon) ** 2, dim=1).numpy()

    # ══════════════════════════════════════════════════════════
    # PART 2: XGBoost with recon_error as extra feature
    # ══════════════════════════════════════════════════════════
    print("\n🚀 [2/2] Training XGBoost...")
    X_hybrid  = np.column_stack([X_scaled, recon_errors])
    model_xgb = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=(y_res == 0).sum() / (y_res == 1).sum(),
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
        verbosity=0
    )
    model_xgb.fit(X_hybrid, y_res)
    print("✅ XGBoost trained!")

    # ── Threshold ──────────────────────────────────────────────
    X_all = torch.FloatTensor(scaler.transform(df[available].values))
    with torch.no_grad():
        recon_all = ae(X_all)
    err_all      = torch.mean((X_all - recon_all) ** 2, dim=1).numpy()
    best_f1, best_thresh = 0, 0
    for pct in np.arange(85, 99, 0.5):
        thresh = np.percentile(err_all, pct)
        f1     = f1_score(y.values, (err_all > thresh).astype(int), zero_division=0)
        if f1 > best_f1:
            best_f1, best_thresh = f1, thresh

    # ── Save ───────────────────────────────────────────────────
    pickle.dump(scaler,       open(SCALER_PATH,    "wb"))
    pickle.dump(available,    open(FEATURES_PATH,  "wb"))
    pickle.dump(best_thresh,  open(THRESHOLD_PATH, "wb"))
    pickle.dump(model_xgb,    open(XGB_MODEL_PATH, "wb"))

    print(f"\n{'='*50}")
    print(f"  ✅ Hybrid Model Trained!")
    print(f"  Autoencoder Best Loss  : {best_loss:.6f}")
    print(f"  AE Best F1 (threshold) : {best_f1*100:.2f}%")
    print(f"  XGBoost features used  : {X_hybrid.shape[1]}")
    print(f"{'='*50}")


def predict(transaction: dict) -> dict:
    if not os.path.exists(XGB_MODEL_PATH):
        return {"is_fraud": False, "anomaly_score": 0.0, "risk_level": "LOW"}

    # ── Load models ────────────────────────────────────────────
    sys.modules["__main__"].Autoencoder = Autoencoder
    ae        = torch.load(AE_MODEL_PATH, weights_only=False)
    ae.eval()

    scaler    = pickle.load(open(SCALER_PATH,    "rb"))
    features  = pickle.load(open(FEATURES_PATH,  "rb"))
    model_xgb = pickle.load(open(XGB_MODEL_PATH, "rb"))

    X        = np.array([float(transaction.get(f, 0)) for f in features]).reshape(1, -1)
    X_scaled = scaler.transform(X)

    # ── Autoencoder reconstruction error ───────────────────────
    X_tensor = torch.FloatTensor(X_scaled)
    with torch.no_grad():
        recon = ae(X_tensor)
    recon_err = float(torch.mean((X_tensor - recon) ** 2).item())

    # ── XGBoost probability ────────────────────────────────────
    X_hybrid = np.column_stack([X_scaled, [[recon_err]]])
    proba    = float(model_xgb.predict_proba(X_hybrid)[0][1])
    pred     = int(model_xgb.predict(X_hybrid)[0])

    # ── Combined anomaly score (blend XGB + recon_err) ─────────
    recon_normalized = min(recon_err * 5.0, 1.0)       # scale recon to 0–1
    combined_score   = max(proba, recon_normalized)     # take the stronger signal

    # ── Risk level using combined score ────────────────────────
    if combined_score > 0.5:
        risk_level = "HIGH"
    elif combined_score > 0.2:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # ── is_fraud: XGB prediction OR combined score is high ─────
    is_fraud = bool(pred == 1) or combined_score > 0.5

    print(f"  📊 proba={proba:.4f} | recon_err={recon_err:.6f} | "
          f"recon_norm={recon_normalized:.4f} | combined={combined_score:.4f}")

    return {
        "is_fraud":             is_fraud,
        "anomaly_score":        round(combined_score, 4),
        "reconstruction_error": round(recon_err, 6),
        "risk_level":           risk_level,
        "features_used":        len(features) + 1
    }


if __name__ == "__main__":
    train()
