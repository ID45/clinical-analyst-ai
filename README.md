# Clinical Analyst AI

An AI-powered hospital performance dashboard built with Streamlit. It calculates clinical KPIs from raw CSV data, visualises them with interactive Plotly charts, and provides GPT-4-backed insights, metric deep-dives, 90-day action plans, and a conversational chat interface.

---

## Features

- **Dashboard** — headline KPI cards with benchmark deltas and a full KPI vs benchmark chart
- **Clinical Quality** — readmission rate, HAI rate, mortality rate, average length of stay
- **Operations** — bed turnover, wait times, no-show rate, ER wait time
- **Financial** — claim denial rate, days in A/R, collection rate, cost per visit
- **Patient Experience** — satisfaction score distribution and trends
- **AI Insights** — executive summary, metric deep-dives, custom Q&A, and 90-day action plans powered by GPT-4
- **Chat** — persistent conversational interface with suggested starter questions
- **Upload Data** — upload your own CSV files; missing files fall back to sample data automatically

---

## Prerequisites

- Python 3.9 or higher
- An [OpenAI API key](https://platform.openai.com/api-keys) (required for AI Insights and Chat pages)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/clinical-analyst-ai.git
cd clinical-analyst-ai
```

### 2. Create and activate a virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and add your API key:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder:

```
OPENAI_API_KEY=your-openai-api-key-here
```

> The `.env` file is listed in `.gitignore` and will never be committed.

---

## Data Setup

### Option A — Generate sample data (quickest way to get started)

A data generation script is included. Run it once to create realistic synthetic CSV files in `data/sample_data/`:

```bash
python generate_sample_data.py
```

This creates 1,000 synthetic patient records across Q1 2024 with matching readmissions, infections, claims, appointments, and survey data.

### Option B — Bring your own data

Place your own CSV files in `data/sample_data/` using the column schemas below, or upload them directly in the app via the **Upload Data** page.

The app expects six CSV files placed in `data/sample_data/`. The required columns for each file are listed below.

### `patients.csv`
| Column | Type | Description |
|--------|------|-------------|
| `patient_id` | string | Unique patient identifier |
| `admission_date` | date | Admission date (YYYY-MM-DD) |
| `discharge_date` | date | Discharge date (YYYY-MM-DD) |
| `length_of_stay` | int | Days in hospital |
| `department` | string | Admitting department (e.g. Cardiology, Emergency) |
| `discharge_status` | string | `discharged`, `transferred`, or `deceased` |

### `readmissions.csv`
| Column | Type | Description |
|--------|------|-------------|
| `patient_id` | string | Patient identifier |
| `original_discharge` | date | Date of original discharge |
| `readmission_date` | date | Date of readmission |
| `days_between` | int | Days between discharge and readmission |

### `infections.csv`
| Column | Type | Description |
|--------|------|-------------|
| `patient_id` | string | Patient identifier |
| `department` | string | Department where infection occurred |
| `infection_type` | string | Type of HAI (e.g. UTI, CLABSI) |
| `onset_date` | date | Date infection was identified |

### `claims.csv`
| Column | Type | Description |
|--------|------|-------------|
| `claim_id` | string | Unique claim identifier |
| `patient_id` | string | Patient identifier |
| `claim_status` | string | `paid`, `denied`, or `pending` |
| `claim_amount` | float | Total billed amount |
| `allowed_amount` | float | Amount approved by payer |
| `paid_amount` | float | Amount actually paid |
| `submission_date` | date | Date claim was submitted |
| `payment_date` | date | Date payment was received (null if not paid) |
| `denial_reason` | string | Reason for denial (null if not denied) |

### `appointments.csv`
| Column | Type | Description |
|--------|------|-------------|
| `appointment_id` | string | Unique appointment identifier |
| `patient_id` | string | Patient identifier |
| `scheduled_time` | datetime | Scheduled appointment time |
| `status` | string | `completed`, `no_show`, or `cancelled` |
| `wait_time_minutes` | int | Minutes waited before being seen |

### `surveys.csv`
| Column | Type | Description |
|--------|------|-------------|
| `survey_id` | string | Unique survey identifier |
| `patient_id` | string | Patient identifier |
| `survey_date` | date | Date survey was completed |
| `overall_satisfaction` | float | Score from 1–10 |

> You can also upload your own files directly in the app via the **Upload Data** page without modifying the `data/sample_data/` directory.

---

## Running the App

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

---

## Project Structure

```
clinical-analyst-ai/
├── app.py                        # Streamlit application entry point
├── agents/
│   ├── data_loader.py            # Loads and validates CSV data
│   ├── metrics_calculator.py     # Calculates all 15 clinical KPIs
│   ├── visualizer.py             # Creates Plotly charts
│   └── insights_generator.py    # GPT-4 powered insights and chat
├── data/
│   └── sample_data/              # Place your CSV files here
│       ├── patients.csv
│       ├── readmissions.csv
│       ├── infections.csv
│       ├── claims.csv
│       ├── appointments.csv
│       └── surveys.csv
├── .env                          # Your API keys (not committed)
├── .env.example                  # Template for environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

---

## KPIs Calculated

| Category | Metric | Benchmark |
|----------|--------|-----------|
| Clinical Quality | 30-Day Readmission Rate | < 15% |
| Clinical Quality | Healthcare-Associated Infection Rate | < 1 per 1,000 patient days |
| Clinical Quality | Inpatient Mortality Rate | < 2% |
| Clinical Quality | Average Length of Stay | < 4.5 days |
| Operations | Bed Turnover Rate | > 0.70 |
| Operations | Average Patient Wait Time | < 30 min |
| Operations | Appointment No-Show Rate | < 5% |
| Operations | ER Wait Time | < 30 min |
| Financial | Claim Denial Rate | < 5% |
| Financial | Days in Accounts Receivable | < 35 days |
| Financial | Net Collection Rate | > 95% |
| Financial | Average Cost per Visit | — |
| Patient Experience | Patient Satisfaction Score | > 8.0 / 10 |
| Data | Data Quality Score | — |
| Data | Data Accessibility | — |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | [Streamlit](https://streamlit.io) |
| Charts | [Plotly](https://plotly.com/python/) |
| AI | [OpenAI GPT-4](https://platform.openai.com) via [LangChain](https://python.langchain.com) |
| Data | [Pandas](https://pandas.pydata.org) / [NumPy](https://numpy.org) |
| Config | [python-dotenv](https://pypi.org/project/python-dotenv/) |

---

## Security Notes

- Never commit your `.env` file. It is excluded by `.gitignore`.
- If you accidentally expose your `OPENAI_API_KEY`, revoke it immediately at [platform.openai.com/api-keys](https://platform.openai.com/api-keys) and generate a new one.
- Patient data files in `data/sample_data/` are also excluded from version control by `.gitignore`. Do not modify this behaviour if you are working with real patient data.
