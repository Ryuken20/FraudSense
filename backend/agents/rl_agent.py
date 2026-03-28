import numpy as np
import pickle
import os

QTABLE_PATH = "saved_rl_qtable.pkl"

# ── Actions ────────────────────────────────────────────────────
ACTIONS      = ["clear", "monitor", "block"]
ACTION_IDX   = {a: i for i, a in enumerate(ACTIONS)}

# ── Reward Structure (mimics real bank policy) ─────────────────
REWARDS = {
    # (actual_fraud, action)
    (True,  "block"):   +10,   # ✅ correctly blocked fraud
    (True,  "monitor"): +3,    # ⚠️ monitored fraud (partial credit)
    (True,  "clear"):   -20,   # 💀 missed fraud — worst outcome
    (False, "clear"):   +5,    # ✅ correctly cleared clean txn
    (False, "monitor"): -2,    # ⚠️ unnecessary monitoring
    (False, "block"):   -5,    # ❌ false alarm — blocked clean txn
}


class FraudRLAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.alpha   = alpha    # learning rate
        self.gamma   = gamma    # discount factor
        self.epsilon = epsilon  # exploration rate

        # State = (risk_level, anomaly_bucket)
        # Q-table: state → action values
        self.q_table = {}

    def _get_state(self, ml_result: dict) -> tuple:
        risk  = ml_result.get("risk_level", "LOW")           # HIGH/MEDIUM/LOW
        score = ml_result.get("anomaly_score", 0.0)
        bucket = "high" if score > 0.7 else "mid" if score > 0.4 else "low"
        return (risk, bucket)

    def _get_q(self, state):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(ACTIONS))
        return self.q_table[state]

    def decide(self, ml_result: dict) -> str:
        """Choose action using epsilon-greedy policy"""
        state = self._get_state(ml_result)
        q     = self._get_q(state)

        # Explore vs exploit
        if np.random.rand() < self.epsilon:
            return np.random.choice(ACTIONS)     # explore
        else:
            return ACTIONS[np.argmax(q)]          # exploit best known

    def learn(self, ml_result: dict, action: str, actual_fraud: bool):
        """Update Q-table based on outcome feedback"""
        state  = self._get_state(ml_result)
        reward = REWARDS.get((actual_fraud, action), 0)
        q      = self._get_q(state)
        idx    = ACTION_IDX[action]

        # Q-learning update rule
        q[idx] = q[idx] + self.alpha * (reward + self.gamma * np.max(q) - q[idx])
        self.q_table[state] = q

        return reward

    def save(self):
        pickle.dump(self.q_table, open(QTABLE_PATH, "wb"))
        print(f"✅ RL Q-table saved ({len(self.q_table)} states learned)")

    def load(self):
        if os.path.exists(QTABLE_PATH):
            self.q_table = pickle.load(open(QTABLE_PATH, "rb"))
            print(f"✅ RL Q-table loaded ({len(self.q_table)} states)")

    def stats(self):
        print("\n📊 RL Agent Q-Table Summary:")
        print(f"  States learned : {len(self.q_table)}")
        for state, q in self.q_table.items():
            best = ACTIONS[np.argmax(q)]
            print(f"  State {state} → Best Action: {best} | Q-values: {np.round(q,2)}")


# ── Simulate Training (show concept) ──────────────────────────
if __name__ == "__main__":
    agent = FraudRLAgent(epsilon=0.3)

    print("🤖 Training RL Agent on simulated transactions...")

    # Simulate 1000 transactions
    for i in range(5000):
        # Simulate ML result
        is_fraud  = np.random.rand() < 0.035    # 3.5% fraud rate
        score     = np.random.uniform(0.6, 0.95) if is_fraud else np.random.uniform(0.0, 0.4)
        risk      = "HIGH" if score > 0.7 else "MEDIUM" if score > 0.4 else "LOW"

        ml_result = {"anomaly_score": score, "risk_level": risk}

        # Agent decides
        action = agent.decide(ml_result)

        # Agent learns from outcome
        reward = agent.learn(ml_result, action, actual_fraud=is_fraud)

    # Reduce exploration after training
    agent.epsilon = 0.05
    agent.save()
    agent.stats()

    print("\n✅ RL Agent trained!")
    print("   It now knows optimal actions for each risk state")
    print("   Penalizes missed fraud 4x more than false alarms")
