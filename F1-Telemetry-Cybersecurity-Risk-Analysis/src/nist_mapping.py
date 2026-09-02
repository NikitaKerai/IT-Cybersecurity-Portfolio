import pandas as pd
import matplotlib.pyplot as plt

# =========================
# NIST Risk Assessment Data
# =========================

nist_mapping = pd.DataFrame([
    {
        "Attack": "spoofing",
        "RiskScore": 3
    },
    {
        "Attack": "tampering",
        "RiskScore": 3
    },
    {
        "Attack": "delay",
        "RiskScore": 2
    },
    {
        "Attack": "dos",
        "RiskScore": 2
    }
])

# =========================
# Create Graph
# =========================

plt.figure(figsize=(8, 5))

plt.bar(
    nist_mapping["Attack"],
    nist_mapping["RiskScore"]
)

plt.title("NIST Risk Assessment of Simulated F1 Telemetry Attacks")
plt.xlabel("Attack Type")
plt.ylabel("Risk Level")

plt.yticks(
    [1, 2, 3],
    ["Low", "Medium", "High"]
)

plt.tight_layout()

# Save into your existing graphs folder
plt.savefig("graphs/nist_risk_graph_2025.png")

print("Graph saved as graphs/nist_risk_graph_2025.png")