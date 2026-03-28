from datetime import datetime
import uuid

def generate_report(txn: dict, ml_result: dict, reg_result: dict) -> dict:
    risk_score   = ml_result.get("risk_score", txn.get("risk_score", 0))
    anomaly_flag = ml_result.get("anomaly_flag", txn.get("anomaly_flag", "NORMAL"))
    reg_level    = reg_result.get("risk_level", "LOW")

    if risk_score >= 85 or (anomaly_flag == "FRAUDULENT" and reg_level == "HIGH"):
        action, reason, confidence = "BLOCK", "High confidence fraud pattern with regulatory violations", min(99, risk_score+5)
    elif risk_score >= 60 or anomaly_flag == "SUSPICIOUS":
        action, reason, confidence = "MONITOR", "Unusual activity detected — requires close monitoring", risk_score
    elif reg_result.get("violations"):
        action, reason, confidence = "ESCALATE", "Regulatory violations require human compliance review", 75
    else:
        action, reason, confidence = "AUTO_RESOLVE", "Low risk score — likely false positive", 100 - risk_score

    shap = ml_result.get("shap_values", [])
    top_reasons = [f"{s['feature']} (importance: {s['importance']:.2f})" for s in shap[:3]]

    return {
        "report_id": f"RPT-{uuid.uuid4().hex[:8].upper()}",
        "case_id": txn.get("transaction_id", "N/A"),
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "transaction": {
            "id": txn.get("transaction_id"),
            "user_id": txn.get("user_id"),
            "amount": txn.get("amount"),
            "currency": txn.get("currency", "INR"),
            "type": txn.get("type"),
            "timestamp": txn.get("timestamp"),
            "from_account": txn.get("from_account"),
            "to_account": txn.get("to_account"),
            "location": txn.get("location"),
            "device_id": txn.get("device_id"),
            "ip_address": txn.get("ip_address"),
            "kyc_status": txn.get("kyc_status"),
        },
        "ml_analysis": {
            "risk_score": risk_score,
            "anomaly_flag": anomaly_flag,
            "top_features": top_reasons,
            "shap_values": shap,
        },
        "regulatory_assessment": {
            "risk_level": reg_level,
            "violations": reg_result.get("violations", []),
            "details": reg_result.get("details", []),
        },
        "evidence": {
            "flags_triggered": txn.get("flags", []),
            "device_match": "new_device" not in txn.get("flags", []),
            "geo_anomaly": "geo_anomaly" in txn.get("flags", []),
            "odd_hours": "odd_hours" in txn.get("flags", []),
            "velocity_breach": "velocity_breach" in txn.get("flags", []),
        },
        "recommendation": {
            "action": action,
            "reason": reason,
            "confidence_percent": confidence,
        },
        "investigator_notes": "",
        "status": "PENDING_REVIEW"
    }