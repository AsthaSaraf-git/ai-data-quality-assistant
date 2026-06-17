🔍 Data Quality Assistant

A metadata-driven data quality framework that validates datasets using configurable YAML rules and generates quality metrics, reports, and dashboards.

The framework is designed around a core principle:

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

Framework Features

* ✅ Metadata-driven rule configuration
* ✅ Multi-table processing
* ✅ CSV-based reporting
* ✅ Quality score calculation
* ✅ HTML dashboard generation
* ✅ Extensible rule engine architecture

⸻

🏗️ Architecture

CSV Files
    │
    ▼
YAML Rule Definitions
    │
    ▼
Rule Engine
    │
    ▼
Validation Results
    │
    ├── Detailed Report
    ├── Summary Report
    └── Quality Dashboard

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
│   └── quality_dashboard.html
│
├── src/
│   ├── file_loader.py
│   ├── rule_engine.py
│   ├── report_generator.py
│   ├── dashboard_generator.py
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

📊 Sample Output

Validation Report

table_name	column	rule	status
customers	customer_id	unique	FAILED
customers	email	regex	FAILED
products	product_name	not_null	FAILED

Quality Summary

table_name	total_rules	passed_rules	failed_rules	quality_score
customers	9	3	6	33.33
products	3	1	2	33.33

⸻

🖥️ Run Locally

Install dependencies:

pip install -r requirements.txt

Run validation:

python3 src/validator.py

Generated outputs:

reports/validation_report.csv
reports/summary_report.csv
reports/quality_dashboard.html

⸻

💡 Design Principles

This project follows a metadata-driven architecture:

* Validation logic is separated from configuration.
* New datasets can be onboarded using YAML files.
* Validation rules are reusable across datasets.
* Rule execution is centralized in a dedicated rule engine.
* Reports and dashboards are generated automatically.

⸻

🔮 Roadmap

Phase 1 - Data Quality Framework ✅

* Metadata-driven rules
* Multi-table validation
* Quality scoring
* HTML dashboard

Phase 2 - Observability

* Historical quality tracking
* Trend analysis
* Data quality alerts
* SLA monitoring

Phase 3 - AI Assistant

* Root cause analysis using LLMs
* Natural language quality investigation
* AI-generated remediation recommendations
* Conversational Data Quality Copilot

Example:

Why did customer quality score drop this week?
Customer quality score dropped from 92% to 78%.
Primary causes:
- Increase in duplicate customer IDs
- Missing country values
- Invalid email formats
Recommended actions:
- Validate IDs at source
- Add country as mandatory field
- Introduce email validation during ingestion

⸻

🛠️ Tech Stack

* Python
* Pandas
* YAML
* HTML
* Git
* GitHub

⸻

👩‍💻 Author

Built as part of a hands-on Data Engineering and Data Architecture portfolio focused on metadata-driven frameworks, governance, and data quality automation.