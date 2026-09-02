# 🏎️ F1 Telemetry Cybersecurity Risk Analysis

A Python-based cybersecurity research and simulation project investigating how cyber attacks affecting Formula One telemetry data could influence race-strategy decisions and operational outcomes.

## 📌 Project Overview

Modern Formula One relies heavily on telemetry and data-driven decision-making. Race teams use information such as lap times, tyre performance, driver position and other telemetry to support strategic decisions throughout a race.

This project investigates the potential cybersecurity risks associated with telemetry-dependent race strategy.

Using historical 2025 Formula One race data, I developed a Python-based simulation that creates a baseline race-strategy recommendation and then introduces controlled cyber attack scenarios to evaluate how manipulated, delayed or unavailable data could influence strategy decisions.

The project combines data analysis, cybersecurity threat modelling and risk assessment to demonstrate how the integrity and availability of telemetry can affect data-driven decision-making.

---

## 🎯 Research Question

**How can a cybersecurity risk assessment framework be used to evaluate the effect of telemetry attacks on Formula One race-strategy systems?**

---

## 🛠️ Technologies & Frameworks

### Programming & Data Analysis
- Python
- pandas
- matplotlib
- requests

### Formula One Data
- FastF1
- OpenF1 API

### Cybersecurity
- STRIDE Threat Modelling
- CIA Triad
- Cybersecurity Risk Assessment
- NIST-oriented risk analysis

---

## ⚙️ Project Workflow

The project follows the workflow below:

1. Retrieve historical 2025 Formula One race data using FastF1.
2. Process and clean race telemetry data.
3. Generate telemetry-derived features.
4. Create a baseline race-strategy recommendation.
5. Introduce controlled cyber attack scenarios.
6. Compare clean and attacked strategy recommendations.
7. Measure changes in pit-stop recommendations.
8. Estimate simulated race-position impact.
9. Map attack scenarios using STRIDE and the CIA Triad.
10. Perform cybersecurity risk assessment.
11. Generate CSV results and visualisations.
12. Use OpenF1 as an additional source for data validation.

---

## 📊 Telemetry Features

The simulation derives several features from the race data to support strategy decisions.

### Median Lap Time

The median lap time is calculated for each race lap and is used as a baseline for comparison between drivers.

### Pace Delta

The difference between a driver's lap time and the median lap time for that lap.

### Tyre Degradation Proxy

Changes in lap time during a driver's stint are used as a simplified indicator of tyre degradation.

### Position Change

Changes in race position are calculated for each driver throughout a race.

These features are then used by the strategy model to generate one of three recommendations:

- `PIT`
- `CONSIDER PIT`
- `STAY OUT`

---

## 🚨 Simulated Cyber Attack Scenarios

Four controlled attack scenarios are simulated against the telemetry data.

### 1. Spoofing

Lap-time data is manipulated to simulate falsified telemetry being supplied to the strategy model.

The purpose of this scenario is to investigate whether false telemetry could influence strategic recommendations.

### 2. Data Tampering

The tyre-degradation proxy is modified to simulate unauthorised manipulation of data used by the strategy model.

This evaluates the effect that compromised data integrity could have on pit-stop decisions.

### 3. Telemetry Delay

Tyre-life data is shifted to simulate stale or delayed information reaching the strategy system.

This scenario explores how outdated telemetry could affect real-time decision-making.

### 4. Denial of Service (DoS)

A proportion of telemetry observations is removed to simulate reduced data availability.

The simulation evaluates how loss of telemetry could affect the reliability of strategy decisions.

---

## 📈 Impact Analysis

The clean baseline data is compared against the attacked datasets.

The project measures:

- Number of strategy decisions changed
- Percentage of strategy decisions changed
- Clean vs attacked pit-stop recommendations
- Pit-stop timing error
- Average pit-stop error
- Maximum pit-stop error
- Simulated race-position impact
- Attack impact by race
- Decision accuracy under reduced telemetry availability

These measurements provide a way of translating cybersecurity attacks into potential operational consequences.

---

## 🔐 STRIDE Threat Modelling

The simulated attacks are mapped against relevant STRIDE threat categories.

| Attack Scenario | STRIDE Category |
|---|---|
| Spoofing | Spoofing |
| Data Tampering | Tampering |
| Telemetry Delay | Denial of Service |
| Denial of Service | Denial of Service |

This helps connect the technical simulations to an established cybersecurity threat-modelling approach.

---

## 🛡️ CIA Triad Assessment

The attack scenarios are also evaluated against the three principles of the CIA Triad:

### Confidentiality
Protecting information from unauthorised disclosure.

### Integrity
Ensuring that telemetry remains accurate and has not been improperly modified.

### Availability
Ensuring that telemetry remains accessible when required by race-strategy systems.

Within this simulation, spoofing and tampering primarily affect **integrity**, while telemetry delay and denial-of-service scenarios affect **availability** and, in the case of delayed data, can also affect the usefulness and integrity of information used for decision-making.

---

## ⚠️ Cybersecurity Risk Assessment

A simplified likelihood × impact approach is used to calculate cybersecurity risk scores for the simulated attacks.

Each scenario is assigned:

- Likelihood
- Impact
- Risk Score
- Risk Level

Risk levels are classified as:

- Low
- Medium
- High

The purpose of the assessment is to combine the technical simulation results with cybersecurity risk analysis.

---

## 🔎 OpenF1 Data Validation

A separate Python script uses the OpenF1 API as an additional data source.

The validation process retrieves:

- Formula One session metadata
- Driver position data
- Session timing information

The script then produces validation outputs that compare the availability of selected data elements between FastF1 and OpenF1.

---

## 📂 Repository Structure

```text
F1-Telemetry-Cybersecurity-Risk-Analysis/
│
├── README.md
├── requirements.txt
├── .gitignore
│
└── src/
    ├── README.md
    ├── main.py
    ├── nist_mapping.py
    └── openf1_validation.py
```

Additional result files and graphs are generated when the scripts are executed.

---

## 💻 Installation

### 1. Clone the repository

Clone or download the IT & Cybersecurity Portfolio repository to your computer.

### 2. Navigate to the F1 project directory

```bash
cd F1-Telemetry-Cybersecurity-Risk-Analysis
```

### 3. Create a virtual environment (recommended)

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install the required Python packages

```bash
pip install -r requirements.txt
```

The project requires:

- fastf1
- pandas
- matplotlib
- requests

---

## ▶️ Running the Project

Run these commands from the main `F1-Telemetry-Cybersecurity-Risk-Analysis` directory.

### Main Cybersecurity Simulation

```bash
python src/main.py
```

The main script:

- Retrieves 2025 F1 race data
- Processes telemetry-derived features
- Generates baseline strategy decisions
- Simulates cyber attacks
- Compares clean and attacked decisions
- Calculates pit-stop errors
- Estimates simulated position impact
- Generates cybersecurity mappings
- Produces CSV results
- Generates graphs

### OpenF1 Validation

```bash
python src/openf1_validation.py
```

This retrieves OpenF1 data and generates validation outputs.

### NIST Risk Visualisation

```bash
python src/nist_mapping.py
```

This generates a visual representation of the project's risk assessment.

---

## 📁 Generated Outputs

Running the project generates several CSV files containing analysis results, including:

- Attack comparison results
- Attack summary
- Pit-stop error analysis
- Position-impact analysis
- DoS impact analysis
- STRIDE mapping
- CIA Triad mapping
- Cybersecurity risk assessment
- Dataset summary
- Baseline strategy outputs
- Attack strategy outputs

The project also generates visualisations inside the `graphs/` directory.

---

## 🧠 Skills Demonstrated

This project demonstrates practical experience in:

**Cybersecurity**
- Cybersecurity risk assessment
- Threat modelling
- STRIDE
- CIA Triad
- Data integrity and availability analysis
- Security impact assessment

**Programming**
- Python
- pandas
- Data processing
- Data manipulation
- Automation
- API requests

**Data Analysis**
- Formula One telemetry analysis
- Data cleaning
- Feature engineering
- Comparative analysis
- Data visualisation

**Technical Skills**
- FastF1
- OpenF1 API
- matplotlib
- CSV data processing
- Reproducible technical analysis
- Technical documentation

---

## ⚖️ Ethics & Scope

This project is an academic cybersecurity simulation.

It uses publicly available historical Formula One data and controlled manipulation of locally processed datasets.

No live Formula One systems, team infrastructure, proprietary telemetry networks or operational race systems were accessed, attacked or tested.

The attack scenarios are simplified simulations designed to investigate the potential consequences of compromised telemetry data. They should not be interpreted as representations of the internal architecture or security controls used by real Formula One teams.

---

## 🎓 Academic Context

This project was developed as part of my **MSc Computer Science with Cyber Security** at the **University of York**.

The project combines my interests in cybersecurity, data analysis and Formula One to investigate how cyber risk can translate into operational and strategic consequences in a high-performance, data-driven environment.

---

## 👤 Author

**Nikita Kerai**

MSc Computer Science with Cyber Security  
BSc Computer Security and Forensics — First Class Honours

Areas of interest:

- Cybersecurity
- IT Infrastructure
- Cloud Technologies
- Network Security
- Security Operations
- Data Analysis
