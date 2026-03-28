HIGH_RISK_COUNTRIES = ["Nigeria","North Korea","Iran","Belarus","Kyrgyzstan","Lagos","Pyongyang","Bishkek","Minsk"]
CASH_REPORTING_THRESHOLD = 50000
HIGH_VALUE_THRESHOLD = 200000

REGULATIONS = {
    "RBI_KYC":  "RBI KYC Master Direction 2016 — Customer Due Diligence",
    "PMLA_CTR": "PMLA 2002 Section 12 — Cash Transaction Report",
    "FATF_HR":  "FATF Recommendation 19 — High-Risk Countries",
    "RBI_AML":  "RBI AML Guidelines Circular 2019",
    "RBI_HIGH": "RBI Circular on Large Value Transactions",
    "VELOCITY": "RBI Fraud Risk Management — Velocity Checks",
}

def assess_risk(txn: dict) -> dict:
    violations, details = [], []
    risk_level = "LOW"
    amount   = txn.get("amount", 0)
    flags    = txn.get("flags", [])
    location = txn.get("location", "")
    kyc      = txn.get("kyc_status", "COMPLETE")
    txn_type = txn.get("type", "")

    if kyc != "COMPLETE":
        violations.append(REGULATIONS["RBI_KYC"])
        details.append(f"KYC status is {kyc} — transaction flagged per RBI KYC norms")
        risk_level = "HIGH"

    if amount >= CASH_REPORTING_THRESHOLD and txn_type in ["NEFT","RTGS"]:
        violations.append(REGULATIONS["PMLA_CTR"])
        details.append(f"Transaction ₹{amount:,} exceeds PMLA CTR threshold of ₹{CASH_REPORTING_THRESHOLD:,}")
        if risk_level != "HIGH": risk_level = "MEDIUM"

    if any(c in location for c in HIGH_RISK_COUNTRIES):
        violations.append(REGULATIONS["FATF_HR"])
        details.append(f"Transaction originates from FATF high-risk location: {location}")
        risk_level = "HIGH"

    if amount >= HIGH_VALUE_THRESHOLD:
        violations.append(REGULATIONS["RBI_HIGH"])
        details.append(f"Transaction ₹{amount:,} exceeds RBI high-value threshold of ₹{HIGH_VALUE_THRESHOLD:,}")
        if risk_level == "LOW": risk_level = "MEDIUM"

    if "velocity_breach" in flags or "rapid_succession" in flags:
        violations.append(REGULATIONS["VELOCITY"])
        details.append("Multiple transactions in short window — velocity breach detected")
        if risk_level == "LOW": risk_level = "MEDIUM"

    if "geo_anomaly" in flags or "unusual_recipient" in flags:
        violations.append(REGULATIONS["RBI_AML"])
        details.append("Geo anomaly or unusual recipient detected — AML review required")
        if risk_level == "LOW": risk_level = "MEDIUM"

    return {"risk_level": risk_level, "violations": list(set(violations)), "details": details}