def investigate(transaction: dict, ml_result: dict) -> str:
    amount   = float(transaction.get("amount", 0))
    location = transaction.get("location", "unknown")
    device   = transaction.get("device_id", "unknown")
    user     = transaction.get("user_id", "unknown")
    score    = float(ml_result.get("anomaly_score", 0))
    risk     = ml_result.get("risk_level", "LOW")

    card1    = float(transaction.get("card1", 0))
    card2    = float(transaction.get("card2", 0))
    card3    = float(transaction.get("card3", 0))
    card5    = float(transaction.get("card5", 0))
    dist1    = float(transaction.get("dist1", 0))

    # ── Red Flag Engine ────────────────────────────────────────────
    red_flags = []

    # Amount based flags
    if amount > 1000000:
        red_flags.append(f"🚨 CRITICAL: Extremely high transaction amount ${amount:,.0f} — exceeds $1M threshold")
    elif amount > 500000:
        red_flags.append(f"⚠️  Very high transaction amount ${amount:,.0f} — exceeds $500K threshold")
    elif amount > 100000:
        red_flags.append(f"⚠️  High transaction amount ${amount:,.0f} — exceeds $100K reporting threshold")
    elif amount < 10 and amount > 0:
        red_flags.append(f"⚠️  Suspiciously low amount ${amount:.2f} — classic card testing pattern")

    # Location based flags
    high_risk_locations = {
        "Lagos":      "Nigeria — FATF high-risk jurisdiction",
        "Pyongyang":  "North Korea — OFAC sanctioned country",
        "Minsk":      "Belarus — EU sanctioned country",
        "Bishkek":    "Kyrgyzstan — high money laundering risk",
        "Caracas":    "Venezuela — FATF monitored jurisdiction",
        "Tehran":     "Iran — OFAC sanctioned country",
    }
    if location in high_risk_locations:
        red_flags.append(f"🌍 High-risk jurisdiction: {location} ({high_risk_locations[location]})")

    # Device based flags
    if "unknown" in str(device).lower():
        red_flags.append(f"💻 Unrecognized device fingerprint: '{device}' — possible spoofed/anonymous device")
    if any(x in str(device).lower() for x in ["bot", "vm", "tor", "proxy", "headless", "kali"]):
        red_flags.append(f"🤖 Automated/malicious tool detected in device ID: '{device}'")

    # Card anomaly flags
    if card1 > 9000:
        red_flags.append(f"💳 Abnormal card1 value: {card1:.0f} — statistical outlier (normal < 5000)")
    if card2 > 400:
        red_flags.append(f"💳 Abnormal card2 value: {card2:.0f} — statistical outlier (normal < 200)")
    if card3 > 150:
        red_flags.append(f"💳 Abnormal card3 value: {card3:.0f} — statistical outlier (normal < 100)")
    if card5 > 220:
        red_flags.append(f"💳 Abnormal card5 value: {card5:.0f} — statistical outlier (normal < 150)")

    # Distance flags
    if dist1 > 500:
        red_flags.append(f"📍 Abnormal transaction distance: {dist1:.0f}km — far from billing address")
    if dist1 > 900:
        red_flags.append(f"📍 CRITICAL distance anomaly: {dist1:.0f}km — possible account takeover")

    # Score severity flags
    if score > 0.20:
        red_flags.append(f"🔴 CRITICAL anomaly score {score:.4f} — top 1% most suspicious transactions")
    elif score > 0.15:
        red_flags.append(f"🔴 HIGH anomaly score {score:.4f} — significantly above safe threshold (0.05)")
    elif score > 0.10:
        red_flags.append(f"🟡 ELEVATED anomaly score {score:.4f} — above normal range")
    elif score > 0.05:
        red_flags.append(f"🟡 Moderate anomaly score {score:.4f} — borderline suspicious")

    # Combination flags (most powerful)
    if amount > 50000 and "unknown" in str(device).lower():
        red_flags.append(f"🔗 COMBINATION FLAG: High amount + unknown device = classic account takeover pattern")
    if location in high_risk_locations and amount > 10000:
        red_flags.append(f"🔗 COMBINATION FLAG: High-risk country + large amount = potential money laundering")
    if card1 > 9000 and dist1 > 500:
        red_flags.append(f"🔗 COMBINATION FLAG: Abnormal card profile + large distance = stolen card indicator")

    if not red_flags:
        red_flags.append("📊 Statistical deviation from normal transaction patterns detected by ML model")

    # ── Feature Analysis ───────────────────────────────────────────
    feature_analysis = []

    features = {
        "TransactionAmt": (amount,       50000,  "transaction amount"),
        "card1":          (card1,         5000,  "card identifier 1"),
        "card2":          (card2,          200,  "card identifier 2"),
        "card3":          (card3,          100,  "card type code"),
        "card5":          (card5,          150,  "card product code"),
        "dist1":          (dist1,          100,  "billing distance (km)"),
    }

    for feat, (val, normal_max, desc) in features.items():
        if val > normal_max * 2:
            feature_analysis.append(f"  ▲ {feat} = {val:,.2f} → HIGHLY ANOMALOUS ({desc}, normal max ~{normal_max:,})")
        elif val > normal_max:
            feature_analysis.append(f"  ↑ {feat} = {val:,.2f} → Above normal ({desc}, normal max ~{normal_max:,})")
        else:
            feature_analysis.append(f"  ✓ {feat} = {val:,.2f} → Within normal range")

    # ── Action & Regulatory ────────────────────────────────────────
    if score > 0.15:
        action = "BLOCK"
        action_detail = "Immediately freeze account and block transaction. Escalate to fraud team."
    elif score > 0.05:
        action = "MONITOR"
        action_detail = "Flag for 24-hour surveillance. Request step-up authentication. Alert compliance team."
    else:
        action = "ESCALATE"
        action_detail = "Manual review by senior compliance officer. Request transaction justification."

    if amount > 50000 or location in high_risk_locations:
        reg_note = (
            "• FATF Recommendation 16: Wire transfer reporting required\n"
            "• RBI AML Circular 12228: Suspicious transaction report (STR) mandatory\n"
            "• PMLA Section 12: Report to FIU-IND within 7 working days\n"
            "• PCI-DSS Alert: Card data anomaly requires security review"
        )
    else:
        reg_note = (
            "• Standard RBI AML/KYC review required\n"
            "• PMLA Section 12: Monitor and log transaction\n"
            "• No immediate STR filing required"
        )

    # ── Build Report ───────────────────────────────────────────────
    report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FRAUDSENSE AI INVESTIGATION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY:
  User        : {user}
  Amount      : ${amount:,.2f}
  Location    : {location}
  Device      : {device}
  Risk Level  : {risk}
  Score       : {score:.4f} / 1.0000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RED FLAGS DETECTED ({len(red_flags)} found):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(red_flags)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FEATURE-BY-FEATURE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(feature_analysis)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RISK ASSESSMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Isolation Forest anomaly score: {score:.4f}
  Model trained on: 590,540 real IEEE-CIS transactions
  Contamination threshold: 3.5%
  Decision: {'FRAUD DETECTED' if score > 0.05 else 'SUSPICIOUS PATTERN'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED ACTION: {action}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {action_detail}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REGULATORY COMPLIANCE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{reg_note}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Generated by FraudSense AI Platform v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""".strip()

    return report
