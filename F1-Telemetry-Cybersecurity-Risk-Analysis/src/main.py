import os
import fastf1
import pandas as pd
import matplotlib.pyplot as plt

YEAR = 2025

os.makedirs("f1_cache", exist_ok=True)
os.makedirs("graphs", exist_ok=True)

fastf1.Cache.enable_cache("f1_cache")

schedule = fastf1.get_event_schedule(YEAR)

races = []

for _, row in schedule.iterrows():
    if row["EventFormat"] != "testing":
        races.append(int(row["RoundNumber"]))

print(f"Total races found for {YEAR}: {len(races)}")
print("Race rounds:", races)

all_race_data = []

for race_round in races:
    try:
        print(f"\nLoading {YEAR} race round {race_round}...")

        session = fastf1.get_session(YEAR, race_round, "R")
        session.load()

        laps = session.laps

        race_data = laps[[
            "Driver",
            "LapNumber",
            "LapTime",
            "Compound",
            "TyreLife",
            "Stint",
            "PitInTime",
            "PitOutTime",
            "Position"
        ]].copy()

        race_data["RaceName"] = session.event["EventName"]
        race_data["Round"] = race_round
        race_data["Year"] = YEAR

        all_race_data.append(race_data)

        print(f"Loaded: {session.event['EventName']}")

    except Exception as e:
        print(f"Skipping round {race_round}: {e}")
        continue

if len(all_race_data) == 0:
    raise Exception("No race data loaded.")

race_data = pd.concat(all_race_data, ignore_index=True)

race_data = race_data.dropna(subset=["LapTime", "Compound", "TyreLife"])
race_data["LapTimeSeconds"] = race_data["LapTime"].dt.total_seconds()
race_data = race_data[race_data["LapTimeSeconds"] > 0]


def create_features(data):
    data = data.copy()

    data["MedianLapTime"] = data.groupby(
        ["RaceName", "LapNumber"]
    )["LapTimeSeconds"].transform("median")

    data["PaceDelta"] = data["LapTimeSeconds"] - data["MedianLapTime"]

    data["TyreDegProxy"] = data.groupby(
        ["RaceName", "Driver", "Stint"]
    )["LapTimeSeconds"].diff()

    data["PositionChange"] = data.groupby(
        ["RaceName", "Driver"]
    )["Position"].diff()

    data["PaceDelta"] = data["PaceDelta"].fillna(0)
    data["TyreDegProxy"] = data["TyreDegProxy"].fillna(0)
    data["PositionChange"] = data["PositionChange"].fillna(0)

    return data


race_data = create_features(race_data)


def strategy_decision(row):
    pit_score = (
        row["TyreDegProxy"] * 0.4 +
        row["PaceDelta"] * 0.4 +
        row["TyreLife"] * 0.2
    )

    if pit_score > 5:
        return "PIT"
    elif pit_score > 3:
        return "CONSIDER PIT"
    else:
        return "STAY OUT"


race_data["CleanDecision"] = race_data.apply(strategy_decision, axis=1)

spoofed_data = race_data.copy()
spoofed_data["LapTimeSeconds"] = spoofed_data["LapTimeSeconds"] * 0.85
spoofed_data = create_features(spoofed_data)
spoofed_data["CleanDecision"] = race_data["CleanDecision"].values
spoofed_data["AttackDecision"] = spoofed_data.apply(strategy_decision, axis=1)

tampered_data = race_data.copy()
tampered_data["TyreDegProxy"] = tampered_data["TyreDegProxy"] * 0.2
tampered_data["AttackDecision"] = tampered_data.apply(strategy_decision, axis=1)

delay_data = race_data.copy()
delay_data["TyreLife"] = delay_data.groupby(
    ["RaceName", "Driver"]
)["TyreLife"].shift(3)
delay_data["TyreLife"] = delay_data["TyreLife"].bfill()
delay_data["AttackDecision"] = delay_data.apply(strategy_decision, axis=1)

dos_data = race_data.copy()
dos_data = dos_data.sample(frac=0.7, random_state=42).copy()
dos_data["AttackDecision"] = dos_data.apply(strategy_decision, axis=1)


def compare_attack(attack_name, attack_data):
    comparison = attack_data[[
        "Year",
        "RaceName",
        "Round",
        "Driver",
        "LapNumber",
        "CleanDecision",
        "AttackDecision"
    ]].copy()

    comparison["Attack"] = attack_name
    comparison["DecisionChanged"] = (
        comparison["CleanDecision"] != comparison["AttackDecision"]
    )

    print("\nAttack:", attack_name)
    print("Changed decisions:", comparison["DecisionChanged"].sum())
    print("Changed percentage:", comparison["DecisionChanged"].mean() * 100)

    comparison.to_csv(f"{attack_name}_{YEAR}_results.csv", index=False)

    return comparison


spoofing_results = compare_attack("spoofing", spoofed_data)
tampering_results = compare_attack("tampering", tampered_data)
delay_results = compare_attack("delay", delay_data)
dos_results = compare_attack("DoS", dos_data)

all_results = pd.concat([
    spoofing_results,
    tampering_results,
    delay_results,
    dos_results
], ignore_index=True)

# =========================
# Phase 3: Attack summary table
# =========================

attack_summary = (
    all_results
    .groupby("Attack")["DecisionChanged"]
    .agg(
        ChangedDecisions="sum",
        TotalObservations="count"
    )
)

attack_summary["PercentageChanged"] = (
    attack_summary["ChangedDecisions"]
    / attack_summary["TotalObservations"]
) * 100

attack_summary = attack_summary.reset_index()

attack_summary.to_csv(f"attack_summary_{YEAR}.csv", index=False)

print("\nAttack Summary")
print(attack_summary)

# =========================
# Phase 4: Pit stop error analysis
# =========================

def first_pit_lap(data, decision_column):
    pit_data = data[data[decision_column] == "PIT"]

    return pit_data.groupby(
        ["RaceName", "Round", "Driver"]
    )["LapNumber"].min()


def pit_error_analysis(attack_name, attack_data):
    clean_pits = first_pit_lap(race_data, "CleanDecision")
    attack_pits = first_pit_lap(attack_data, "AttackDecision")

    pit_error = pd.DataFrame({
        "CleanPitLap": clean_pits,
        "AttackPitLap": attack_pits
    }).dropna()

    pit_error["PitStopError"] = (
        pit_error["AttackPitLap"] - pit_error["CleanPitLap"]
    )

    pit_error["AbsolutePitStopError"] = pit_error["PitStopError"].abs()
    pit_error["Attack"] = attack_name

    pit_error = pit_error.reset_index()

    pit_error.to_csv(f"pit_error_{attack_name}_{YEAR}.csv", index=False)

    return pit_error


spoofing_pit_error = pit_error_analysis("spoofing", spoofed_data)
tampering_pit_error = pit_error_analysis("tampering", tampered_data)
delay_pit_error = pit_error_analysis("delay", delay_data)
dos_pit_error = pit_error_analysis("DoS", dos_data)

all_pit_errors = pd.concat([
    spoofing_pit_error,
    tampering_pit_error,
    delay_pit_error,
    dos_pit_error
], ignore_index=True)

all_pit_errors.to_csv(f"all_pit_errors_{YEAR}.csv", index=False)

pit_error_summary = (
    all_pit_errors
    .groupby("Attack")["AbsolutePitStopError"]
    .agg(
        AveragePitStopError="mean",
        MaxPitStopError="max",
        TotalPitStopError="sum"
    )
    .reset_index()
)

pit_error_summary.to_csv(f"pit_error_summary_{YEAR}.csv", index=False)

print("\nPit Stop Error Summary")
print(pit_error_summary)

# =========================
# Phase 5: Simulated position impact
# =========================

all_pit_errors["SimulatedPositionImpact"] = (
    all_pit_errors["AbsolutePitStopError"] * 0.3
)

all_pit_errors.to_csv(
    f"pit_error_with_position_impact_{YEAR}.csv",
    index=False
)

position_impact_summary = (
    all_pit_errors
    .groupby("Attack")["SimulatedPositionImpact"]
    .agg(
        AveragePositionImpact="mean",
        MaxPositionImpact="max",
        TotalPositionImpact="sum"
    )
    .reset_index()
)

position_impact_summary.to_csv(
    f"position_impact_summary_{YEAR}.csv",
    index=False
)

print("\nSimulated Position Impact Summary")
print(position_impact_summary)

race_data.to_csv(f"clean_{YEAR}_race_data.csv", index=False)
all_results.to_csv(f"all_{YEAR}_attack_results.csv", index=False)

# =========================
# Graphs
# =========================

summary = all_results.groupby("Attack")["DecisionChanged"].mean() * 100

plt.figure()
summary.plot(kind="bar")
plt.ylabel("Changed Decisions (%)")
plt.title(f"{YEAR} Strategy Decision Changes by Cyber Attack")
plt.tight_layout()
plt.savefig(f"graphs/graph_1_{YEAR}_attack_impact.png")
plt.close()

race_summary = all_results.groupby(
    ["RaceName", "Attack"]
)["DecisionChanged"].mean().unstack() * 100

race_summary.plot(kind="bar", figsize=(14, 7))
plt.ylabel("Changed Decisions (%)")
plt.title(f"{YEAR} Attack Impact by Race")
plt.tight_layout()
plt.savefig(f"graphs/graph_2_{YEAR}_attack_impact_by_race.png")
plt.close()

driver = "VER"
first_race = race_data["RaceName"].iloc[0]

driver_data = race_data[
    (race_data["Driver"] == driver) &
    (race_data["RaceName"] == first_race)
]

if not driver_data.empty:
    plt.figure()
    plt.plot(driver_data["LapNumber"], driver_data["LapTimeSeconds"])
    plt.xlabel("Lap Number")
    plt.ylabel("Lap Time Seconds")
    plt.title(f"Lap Time Trend for {driver} - {first_race}")
    plt.tight_layout()
    plt.savefig(f"graphs/graph_3_{YEAR}_tyre_degradation_trend.png")
    plt.close()

spoofed_driver_data = spoofed_data[
    (spoofed_data["Driver"] == driver) &
    (spoofed_data["RaceName"] == first_race)
]

if not driver_data.empty and not spoofed_driver_data.empty:
    plt.figure()
    plt.plot(driver_data["LapNumber"], driver_data["LapTimeSeconds"], label="Clean")
    plt.plot(spoofed_driver_data["LapNumber"], spoofed_driver_data["LapTimeSeconds"], label="Spoofed")
    plt.xlabel("Lap Number")
    plt.ylabel("Lap Time Seconds")
    plt.title(f"Clean vs Spoofed Lap Times for {driver} - {first_race}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"graphs/graph_4_{YEAR}_clean_vs_spoofed_lap_times.png")
    plt.close()

tampered_driver_data = tampered_data[
    (tampered_data["Driver"] == driver) &
    (tampered_data["RaceName"] == first_race)
]

if not driver_data.empty and not tampered_driver_data.empty:
    plt.figure()
    plt.plot(driver_data["LapNumber"], driver_data["TyreDegProxy"], label="Clean")
    plt.plot(tampered_driver_data["LapNumber"], tampered_driver_data["TyreDegProxy"], label="Tampered")
    plt.xlabel("Lap Number")
    plt.ylabel("Tyre Degradation Proxy")
    plt.title(f"Clean vs Tampered Tyre Degradation for {driver} - {first_race}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"graphs/graph_5_{YEAR}_clean_vs_tampered_tyre_degradation.png")
    plt.close()

pit_plot_data = all_pit_errors.head(15)

if not pit_plot_data.empty:
    pit_plot_data.plot(
        x="Driver",
        y=["CleanPitLap", "AttackPitLap"],
        kind="bar",
        figsize=(14, 7)
    )
    plt.ylabel("Recommended Pit Lap")
    plt.title(f"{YEAR} Clean vs Attacked Pit Stop Recommendation")
    plt.tight_layout()
    plt.savefig(f"graphs/graph_6_{YEAR}_pit_stop_recommendation_comparison.png")
    plt.close()

dos_levels = [100, 90, 80, 70, 60]
dos_accuracy = []

for level in dos_levels:
    temp_data = race_data.sample(frac=level / 100, random_state=42).copy()
    temp_data["AttackDecision"] = temp_data.apply(strategy_decision, axis=1)
    accuracy = (temp_data["CleanDecision"] == temp_data["AttackDecision"]).mean() * 100
    dos_accuracy.append(accuracy)

dos_impact = pd.DataFrame({
    "DataAvailable": dos_levels,
    "DecisionAccuracy": dos_accuracy
})

plt.figure()
plt.plot(dos_impact["DataAvailable"], dos_impact["DecisionAccuracy"], marker="o")
plt.xlabel("Telemetry Data Available (%)")
plt.ylabel("Decision Accuracy (%)")
plt.title(f"{YEAR} DoS Attack Impact on Strategy Accuracy")
plt.tight_layout()
plt.savefig(f"graphs/graph_7_{YEAR}_dos_attack_impact.png")
plt.close()

dos_impact.to_csv(f"dos_impact_{YEAR}_results.csv", index=False)

plt.figure()
pit_error_summary.plot(
    x="Attack",
    y="AveragePitStopError",
    kind="bar",
    legend=False
)
plt.ylabel("Average Pit Stop Error in Laps")
plt.title(f"{YEAR} Average Pit Stop Error by Attack")
plt.tight_layout()
plt.savefig(f"graphs/graph_8_{YEAR}_average_pit_stop_error.png")
plt.close()

plt.figure()
position_impact_summary.plot(
    x="Attack",
    y="AveragePositionImpact",
    kind="bar",
    legend=False
)
plt.ylabel("Average Simulated Position Impact")
plt.title(f"{YEAR} Simulated Position Impact by Attack")
plt.tight_layout()
plt.savefig(f"graphs/graph_9_{YEAR}_position_impact.png")
plt.close()

# =========================
# Phase 6: STRIDE Mapping
# =========================

stride_mapping = pd.DataFrame([
    ["spoofing", "Spoofing"],
    ["tampering", "Tampering"],
    ["delay", "Denial of Service"],
    ["dos", "Denial of Service"]
], columns=["Attack", "STRIDECategory"])

stride_mapping.to_csv(
    f"stride_mapping_{YEAR}.csv",
    index=False
)

# =========================
# Phase 7: CIA Mapping
# =========================

cia_mapping = pd.DataFrame([
    ["spoofing", "No", "Yes", "No"],
    ["tampering", "No", "Yes", "No"],
    ["delay", "No", "Partial", "Yes"],
    ["dos", "No", "No", "Yes"]
], columns=[
    "Attack",
    "Confidentiality",
    "Integrity",
    "Availability"
])

cia_mapping.to_csv(
    f"cia_mapping_{YEAR}.csv",
    index=False
)

# =========================
# Cybersecurity Risk Assessment
# Likelihood x Impact
# =========================

cybersecurity_risk_mapping = pd.DataFrame([
    ["spoofing",  2, 3],
    ["tampering", 2, 3],
    ["delay",      2, 2],
    ["DoS",        2, 2]
], columns=["Attack", "Likelihood", "Impact"])

# Calculate risk score
cybersecurity_risk_mapping["RiskScore"] = (
    cybersecurity_risk_mapping["Likelihood"]
    * cybersecurity_risk_mapping["Impact"]
)

# Convert score into risk rating
def assign_risk_level(score):
    if score <= 2:
        return "Low"
    elif score <= 4:
        return "Medium"
    else:
        return "High"

cybersecurity_risk_mapping["RiskLevel"] = (
    cybersecurity_risk_mapping["RiskScore"]
    .apply(assign_risk_level)
)

cybersecurity_risk_mapping.to_csv(
    f"cybersecurity_risk_mapping_{YEAR}.csv",
    index=False
)

print("\nCybersecurity Risk Assessment")
print(cybersecurity_risk_mapping)

# =========================
# Export mapping tables as PNG images
# =========================

def save_table_as_png(dataframe, filename, title):
    fig, ax = plt.subplots(figsize=(12, 2 + len(dataframe) * 0.6))
    ax.axis("off")

    table = ax.table(
        cellText=dataframe.values,
        colLabels=dataframe.columns,
        cellLoc="center",
        loc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)

    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


save_table_as_png(
    stride_mapping,
    f"graphs/table_stride_mapping_{YEAR}.png",
    "STRIDE Mapping of Simulated Cyber Attacks"
)

save_table_as_png(
    cia_mapping,
    f"graphs/table_cia_mapping_{YEAR}.png",
    "CIA Triad Impact Assessment"
)

save_table_as_png(
    cybersecurity_risk_mapping,
    f"graphs/table_cybersecurity_risk_assessment_{YEAR}.png",
    "Cybersecurity Risk Assessment"
)

print("STRIDE, CIA and risk tables exported as PNG images.")

# =========================
# Graph 10: Risk Levels
# =========================

risk_map = {
    "Low": 1,
    "Medium": 2,
    "High": 3
}

risk_graph = cybersecurity_risk_mapping.copy()

risk_graph["RiskScore"] = (
    risk_graph["RiskLevel"]
    .map(risk_map)
)

plt.figure()

plt.bar(
    risk_graph["Attack"],
    risk_graph["RiskScore"]
)

plt.ylabel("Risk Level")
plt.title("Cybersecurity Risk by Attack Type")

plt.tight_layout()

plt.savefig(
    f"graphs/graph_10_{YEAR}_risk_levels.png"
)

plt.close()

# =========================
# Chapter 4 Quantitative Summary
# =========================

dataset_summary = pd.DataFrame({
    "Metric": [
        "Number of Races",
        "Number of Drivers",
        "Total Clean Telemetry Observations",
        "Unique Race Laps"
    ],
    "Value": [
        race_data["RaceName"].nunique(),
        race_data["Driver"].nunique(),
        len(race_data),
        race_data[["RaceName", "LapNumber"]].drop_duplicates().shape[0]
    ]
})

print("\nDataset Summary")
print(dataset_summary)

dataset_summary.to_csv(
    f"dataset_summary_{YEAR}.csv",
    index=False
)

# Baseline strategy output counts
baseline_outputs = (
    race_data["CleanDecision"]
    .value_counts()
    .rename_axis("StrategyRecommendation")
    .reset_index(name="BaselineCount")
)

print("\nBaseline Strategy Outputs")
print(baseline_outputs)

baseline_outputs.to_csv(
    f"baseline_strategy_outputs_{YEAR}.csv",
    index=False
)

# Attack output counts
attack_outputs = (
    all_results
    .groupby(["Attack", "AttackDecision"])
    .size()
    .reset_index(name="AttackOutputCount")
)

print("\nAttack Strategy Outputs")
print(attack_outputs)

attack_outputs.to_csv(
    f"attack_strategy_outputs_{YEAR}.csv",
    index=False
)

# Full Chapter 4 attack summary
chapter4_summary = attack_summary.merge(
    pit_error_summary[["Attack", "AveragePitStopError"]],
    on="Attack",
    how="left"
).merge(
    position_impact_summary[["Attack", "AveragePositionImpact"]],
    on="Attack",
    how="left"
).merge(
    cybersecurity_risk_mapping,
    on="Attack",
    how="left"
)

print("\nChapter 4 Summary")
print(chapter4_summary)

chapter4_summary.to_csv(
    f"chapter4_summary_{YEAR}.csv",
    index=False
)

print("\nSTRIDE mapping created")
print("CIA mapping created")
print("Cybersecurity risk mapping created")

print("\nProject completed successfully.")
print(f"Year analysed: {YEAR}")
print(f"Races loaded: {race_data['RaceName'].nunique()}")
print("Phase 3 complete: attack_summary CSV created.")
print("Phase 4 complete: pit stop error CSVs created.")
print("Phase 5 complete: simulated position impact CSV created.")
print("Graphs saved here:")
print(os.path.abspath("graphs"))