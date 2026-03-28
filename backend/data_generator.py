import json
import random
from datetime import datetime, timedelta

LOCATIONS = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Pune", "Ahmedabad"]
SUSPICIOUS_LOCATIONS = ["Lagos", "Bishkek", "Minsk", "Pyongyang"]
TRANSACTION_TYPES = ["NEFT", "IMPS", "UPI", "RTGS", "SWIFT"]
KYC_STATUSES = ["COMPLETE", "INCOMPLETE", "PENDING"]
FLAGS_POOL = ["new_device","odd_hours","high_amount","geo_anomaly","rapid_succession","kyc_incomplete","unusual_recipient","velocity_breach","cross_border","round_amount"]

def random_timestamp(days_back=7):
    base = datetime.utcnow() - timedelta(days=random.randint(0, days_back))
    hour = random.choices(range(24), weights=[3,2,1,1,1,2,4,6,8,10,10,10,10,10,10,10,10,9,8,7,6,5,4,3])[0]
    return base.replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59)).strftime("%Y-%m-%dT%H:%M:%SZ")

def generate_transactions(n=200):
    transactions = []
    for i in range(n):
        is_fraud = random.random() < 0.2
        is_suspicious = random.random() < 0.15
        amount = random.choices(
            [random.randint(500,5000), random.randint(5001,50000), random.randint(50001,500000)],
            weights=[60, 30, 10]
        )[0]
        risk_score = random.randint(75,99) if is_fraud else random.randint(50,74) if is_suspicious else random.randint(5,49)
        if is_fraud:
            anomaly_flag = "FRAUDULENT"
            flags = random.sample(FLAGS_POOL, random.randint(2,5))
            location = random.choice(SUSPICIOUS_LOCATIONS + LOCATIONS)
        elif is_suspicious:
            anomaly_flag = "SUSPICIOUS"
            flags = random.sample(FLAGS_POOL, random.randint(1,3))
            location = random.choice(LOCATIONS)
        else:
            anomaly_flag = "NORMAL"
            flags = []
            location = random.choice(LOCATIONS)
        kyc = "INCOMPLETE" if is_fraud and random.random() < 0.5 else random.choice(KYC_STATUSES)
        txn = {
            "transaction_id": f"TXN-{datetime.utcnow().strftime('%Y%m%d')}-{str(i+1).zfill(3)}",
            "user_id": f"USR-{random.randint(1000,9999)}",
            "amount": amount,
            "currency": "INR",
            "timestamp": random_timestamp(),
            "type": random.choice(TRANSACTION_TYPES),
            "from_account": f"XXXX{random.randint(1000,9999)}",
            "to_account": f"XXXX{random.randint(1000,9999)}",
            "location": location,
            "device_id": f"DEV-{'NEW' if 'new_device' in flags else 'OLD'}-{random.randint(100,999)}",
            "ip_address": f"{'185.220.' if is_fraud else '103.21.'}{random.randint(1,254)}.{random.randint(1,254)}",
            "risk_score": risk_score,
            "anomaly_flag": anomaly_flag,
            "kyc_status": kyc,
            "flags": flags
        }
        transactions.append(txn)
    return transactions

if __name__ == "__main__":
    data = generate_transactions(200)
    with open("data/transactions.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Generated {len(data)} transactions")