import traceback
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models.transaction import Transaction
from models.case import FraudCase
from model import predict
from datetime import datetime


Base.metadata.create_all(bind=engine)

app = FastAPI(title="FraudSense AI Platform 🔍")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve React Frontend ───────────────────────────────────────────
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=f"{FRONTEND_DIST}/assets"), name="assets")
    print("✅ Frontend dist found and mounted")
else:
    print("⚠️ Frontend dist not found — run: npm run build")


class TransactionInput(BaseModel):
    user_id:   str
    amount:    float
    card1:     int   = 0
    card2:     int   = 0
    card3:     int   = 0
    card5:     int   = 0
    dist1:     float = 0.0
    dist2:     float = 0.0
    C1:        float = 1.0
    C2:        float = 1.0
    C6:        float = 1.0
    C13:       float = 10.0
    D1:        float = 5.0
    D10:       float = 5.0
    D15:       float = 5.0
    addr1:     float = 299.0
    addr2:     float = 87.0
    device_id: str   = "unknown"
    location:  str   = "unknown"


# ── Safe import of investigator agent ─────────────────────────────
try:
    from agents.investigator_agent import investigate
    AGENT_AVAILABLE = True
    print("✅ Investigator Agent loaded successfully")
except Exception as e:
    AGENT_AVAILABLE = False
    print(f"⚠️ Agent not available: {e}")

# ── Safe import of RL agent ────────────────────────────────────────
try:
    from agents.rl_agent import FraudRLAgent
    rl_agent = FraudRLAgent()
    rl_agent.load()
    RL_AVAILABLE = True
    print("✅ RL Agent loaded successfully")
except Exception as e:
    RL_AVAILABLE = False
    print(f"⚠️ RL Agent not available: {e}")


# ── Routes ─────────────────────────────────────────────────────────

@app.get("/app", include_in_schema=False)
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))


@app.get("/")
def root():
    return {
        "status":   "FraudSense API is running ✅",
        "frontend": "http://127.0.0.1:8000/app",
        "docs":     "http://127.0.0.1:8000/docs",
        "agent":    "active" if AGENT_AVAILABLE else "unavailable",
        "rl_agent": "active" if RL_AVAILABLE    else "unavailable"
    }


@app.post("/transaction")
def process_transaction(tx: TransactionInput, db: Session = Depends(get_db)):
    try:
        # ── Step 1: ML Prediction ──────────────────────────────────
        try:
            ml_result = predict({
                "TransactionAmt": tx.amount,
                "card1":  tx.card1,
                "card2":  tx.card2,
                "card3":  tx.card3,
                "card5":  tx.card5,
                "dist1":  tx.dist1,
                "dist2":  tx.dist2,
                "C1":     tx.C1,
                "C2":     tx.C2,
                "C6":     tx.C6,
                "C13":    tx.C13,
                "D1":     tx.D1,
                "D10":    tx.D10,
                "D15":    tx.D15,
                "addr1":  tx.addr1,
                "addr2":  tx.addr2,
            })
            print(f"✅ ML Result: {ml_result}")
        except Exception as e:
            print("❌ ML predict() failed:")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"ML model error: {str(e)}")

        # ── Step 2: RL Agent Decides Action ───────────────────────
        score = ml_result["anomaly_score"]
        try:
            if RL_AVAILABLE:
                action = rl_agent.decide(ml_result)
                print(f"✅ RL Agent raw action: {action}")
            else:
                raise Exception("RL not loaded")
        except Exception:
            action = None

        # ── Safety Override: RL sanity check ──────────────────────
        risk = ml_result["risk_level"]
        if not ml_result["is_fraud"] and risk == "LOW":
            action = "clear"
        elif not ml_result["is_fraud"] and risk == "MEDIUM":
            action = "monitor"
        elif action not in ("block", "monitor", "clear"):
            # Final rule-based fallback
            if score > 0.7:
                action = "block"
            elif ml_result["is_fraud"]:
                action = "monitor"
            else:
                action = "clear"

        print(f"✅ Final action: {action}")

        # ── Step 3: Save Transaction to DB ─────────────────────────
        try:
            db_tx = Transaction(
                user_id=tx.user_id,
                amount=tx.amount,
                device_id=tx.device_id,
                location=tx.location,
                is_fraud=ml_result["is_fraud"],
                anomaly_score=score,
                timestamp=datetime.utcnow()
            )
            db.add(db_tx)
            db.commit()
            db.refresh(db_tx)
            print(f"✅ Transaction saved: ID {db_tx.id}")
        except Exception as e:
            print("❌ Database save failed:")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        # ── Step 4: AI Investigation Report ───────────────────────
        if ml_result["is_fraud"]:
            try:
                if AGENT_AVAILABLE:
                    report = investigate(
                        transaction={
                            "user_id":   tx.user_id,
                            "amount":    tx.amount,
                            "location":  tx.location,
                            "device_id": tx.device_id,
                            "timestamp": str(datetime.utcnow()),
                            "card1":     tx.card1,
                            "card2":     tx.card2,
                            "card3":     tx.card3,
                            "card5":     tx.card5,
                            "dist1":     tx.dist1,
                            "dist2":     tx.dist2,
                            "C1":        tx.C1,
                            "C2":        tx.C2,
                            "C6":        tx.C6,
                            "C13":       tx.C13,
                            "D1":        tx.D1,
                            "D10":       tx.D10,
                            "D15":       tx.D15,
                            "addr1":     tx.addr1,
                            "addr2":     tx.addr2,
                        },
                        ml_result=ml_result
                    )
                    print("✅ Investigation report generated")
                else:
                    raise Exception("Agent not loaded")
            except Exception as e:
                print(f"⚠️ Investigation fallback triggered: {e}")
                report = (
                    f"SUMMARY: Transaction by {tx.user_id} of ${tx.amount:,.0f} "
                    f"flagged as {ml_result['risk_level']} risk.\n\n"
                    f"RED FLAGS:\n"
                    f"• Amount: ${tx.amount:,.0f}\n"
                    f"• Device: {tx.device_id}\n"
                    f"• Location: {tx.location}\n\n"
                    f"RISK ASSESSMENT: Anomaly score {score:.4f} detected by ML model.\n\n"
                    f"RECOMMENDED ACTION: {action.upper()}\n\n"
                    f"REGULATORY NOTE: Manual review required per RBI AML guidelines."
                )

            # ── Step 5: Save Fraud Case ────────────────────────────
            try:
                case = FraudCase(
                    transaction_id=db_tx.id,
                    investigation_report=report,
                    risk_score=score,
                    action_taken=action
                )
                db.add(case)
                db.commit()
                print(f"✅ Fraud case saved for transaction ID {db_tx.id}")
            except Exception as e:
                print("❌ Fraud case DB save failed:")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"Fraud case save error: {str(e)}")

        # ── Step 6: Return Response ────────────────────────────────
        return {
            "transaction_id": db_tx.id,
            "user_id":        tx.user_id,
            "amount":         tx.amount,
            "is_fraud":       ml_result["is_fraud"],
            "anomaly_score":  round(score, 4),
            "risk_level":     ml_result["risk_level"],
            "action":         action,
            "rl_decided":     RL_AVAILABLE,
            "timestamp":      str(db_tx.timestamp)
        }

    except HTTPException:
        raise
    except Exception as e:
        print("❌ UNHANDLED ERROR in /transaction:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    try:
        return db.query(Transaction).order_by(Transaction.id.desc()).limit(50).all()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cases")
def get_cases(db: Session = Depends(get_db)):
    try:
        return db.query(FraudCase).order_by(FraudCase.id.desc()).limit(50).all()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/investigate/{transaction_id}")
def get_investigation(transaction_id: int, db: Session = Depends(get_db)):
    try:
        case = db.query(FraudCase).filter(
            FraudCase.transaction_id == transaction_id
        ).first()
        if not case:
            return {"message": "No fraud case found for this transaction"}
        return {
            "transaction_id":       transaction_id,
            "risk_score":           case.risk_score,
            "action":               case.action_taken,
            "investigation_report": case.investigation_report
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    try:
        total   = db.query(Transaction).count()
        fraud   = db.query(Transaction).filter(Transaction.is_fraud == True).count()
        blocked = db.query(FraudCase).filter(FraudCase.action_taken == "block").count()
        return {
            "total_transactions": total,
            "fraud_detected":     fraud,
            "fraud_rate":         round((fraud / total * 100), 2) if total > 0 else 0,
            "blocked":            blocked,
            "monitored":          fraud - blocked
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ── Catch-all: serve React for all unknown routes ──────────────────
@app.get("/{full_path:path}", include_in_schema=False)
def catch_all(full_path: str):
    index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"error": "Frontend not built. Run: npm run build"}


# ── Entry Point ────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
