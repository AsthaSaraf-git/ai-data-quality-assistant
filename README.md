🔍 Data Quality Assistant

A metadata-driven data quality framework built in Python that validates datasets using configurable YAML rules, tracks quality trends over time, and generates dashboards for monitoring data health.

The framework follows a simple principle:

New datasets should be onboarded through configuration, not code changes.

⸻

🚀 Features

Validation Rules

* ✅ Not Null Validation
* ✅ Regex Validation
* ✅ Min Value Validation
* ✅ Max Value Validation
* ✅ Unique Validation
* ✅ Accepted Values Validation

Framework Capabilities

* ✅ Metadata-driven architecture
* ✅ Multi-table validation
* ✅ YAML-based rule configuration
* ✅ Detailed validation reports
* ✅ Quality score calculation
* ✅ Historical quality tracking
* ✅ Trend chart generation
* ✅ HTML dashboard generation

⸻
## 📸 Screenshots

### Data Quality Dashboard

![Dashboard](screenshots/dashboard.png)

### Customer Quality Trend

![Customer Trend](screenshots/customers_quality_trend.png)

______

🏗️ Architecture
```text
CSV Files
    │
    ▼
YAML Rules
    │
    ▼
Validation Engine
    │
    ▼
Validation Report
    │
    ▼
Quality Metrics
    │
    ├── Summary Report
    ├── History Tracking
    ├── Trend Charts
    └── HTML Dashboard
```
⸻

📂 Project Structure

data-quality-assistant/
│
├── data/
│   ├── customers.csv
│   └── products.csv
│
├── rules/
│   ├── customer_rules.yaml
│   └── product_rules.yaml
│
├── reports/
│   ├── validation_report.csv
│   ├── summary_report.csv
│   ├── history.csv
│   ├── customers_quality_trend.png
│   ├── products_quality_trend.png
│   └── quality_dashboard.html
│
├── src/
│   ├── file_loader.py
│   ├── rule_engine.py
│   ├── report_generator.py
│   ├── dashboard_generator.py
│   ├── history_tracker.py
│   ├── trend_dashboard.py
│   └── validator.py
│
├── requirements.txt
└── README.md

⸻

⚙️ Example Rule Configuration

table_name: customers
columns:
  customer_id:
    not_null: true
    unique: true
  email:
    not_null: true
    regex: "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$"
  country:
    not_null: true
    accepted_values:
      - India
      - USA

⸻

📊 Outputs

Validation Report

Provides row-level validation results.

Example:

table_name	column	rule	status
customers	customer_id	unique	FAILED
customers	email	regex	FAILED
products	product_name	not_null	FAILED

⸻

Summary Report

Provides overall quality scores.

table_name	total_rules	passed_rules	failed_rules	quality_score
customers	10	3	7	30.0
products	3	1	2	33.33

⸻

Historical Tracking

Stores quality metrics from every execution.

Example:

run_timestamp	table_name	quality_score
2026-06-15	customers	90
2026-06-16	customers	88
2026-06-17	customers	30

⸻

Trend Charts

Automatically generates quality trend visualizations.

Generated files:

customers_quality_trend.png
products_quality_trend.png

⸻

Dashboard

Generates an HTML dashboard containing:

* Validation summary
* Quality metrics
* Trend visualizations

⸻

🖥️ Run Locally

Install dependencies:

python3 -m pip install -r requirements.txt

Run validation:

python3 src/validator.py

Generated outputs:

reports/validation_report.csv
reports/summary_report.csv
reports/history.csv
reports/quality_dashboard.html
reports/customers_quality_trend.png
reports/products_quality_trend.png

⸻

💡 Design Principles

* Separation of Concerns
* Metadata-Driven Design
* Extensible Rule Engine
* Reusable Validation Logic
* Configuration over Code

⸻

🔮 Roadmap

Phase 1 - Data Quality Framework ✅

* Multi-table validation
* Metadata-driven rules
* Quality scoring
* Historical tracking
* Trend analysis
* Dashboard generation

Phase 2 - Observability

* Quality alerts
* SLA monitoring
* Data freshness checks
* Volume anomaly detection

Phase 3 - AI Assistant

* OpenAI integration
* Root cause analysis
* Natural language investigation
* Remediation recommendations

Example:

Why did customer quality score drop this week?
Customer quality score decreased from 88% to 30%.
Primary causes:
- Duplicate customer IDs
- Invalid email formats
- Missing customer names
Recommended actions:
- Validate customer IDs at source
- Add email validation during ingestion
- Make customer name mandatory

⸻

🛠️ Tech Stack

* Python
* Pandas
* Matplotlib
* YAML
* HTML
* Git
* GitHub

⸻

👩‍💻 Author

Built as part of a Data Engineering and Data Architecture portfolio focused on metadata-driven frameworks, data quality automation, observability, and AI-powered analytics.