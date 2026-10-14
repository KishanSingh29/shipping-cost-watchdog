# Shipping Cost Watchdog

A reproducible Python-based case-study project that detects unusual weekly freight costs, compares them against historical route costs and peer routes, and conservatively checks contextual notes before attributing a possible reason for a cost increase.

The project focuses on deterministic anomaly detection, explainable decisions, conservative evidence matching, citation auditing, and reproducible outputs.

> **Current implementation:** The project includes a deterministic cost-anomaly detection pipeline with TF-IDF-based context retrieval by default. A Sentence Transformers retrieval adapter is available, but full semantic retrieval and the end-to-end semantic RAG workflow have not yet been validated. Evaluation metrics are provisional and must not be interpreted as independently verified model accuracy.

## Table of Contents

- [Problem Statement](#problem-statement)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Anomaly Detection Logic](#anomaly-detection-logic)
- [Context Retrieval and Verification](#context-retrieval-and-verification)
- [Output Format](#output-format)
- [Evaluation](#evaluation)
- [Testing and Reproducibility](#testing-and-reproducibility)
- [Configuration](#configuration)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)

## Problem Statement

Freight transportation costs can vary across routes and weeks because of changes in demand, fuel prices, road conditions, seasonal events, and other operational factors.

Manually reviewing these changes can be time-consuming. However, an unusually high cost does not automatically mean that something is wrong, and a contextual note does not necessarily prove why the cost increased.

Shipping Cost Watchdog addresses this problem by:

1. Aggregating shipment records into weekly route-level costs.
2. Comparing each route's costs with its own historical baseline and comparable peer routes.
3. Identifying potential cost anomalies using explicit thresholds.
4. Retrieving potentially relevant contextual notes.
5. Applying rule-based checks to determine whether a note is suitable supporting evidence.
6. Producing an auditable CSV watchlist with explanations and note references.

When no note passes the verification checks, the system prefers an unexplained result over an unsupported attribution.

## Features

- **Weekly cost aggregation:** Calculates weighted cost per tonne-kilometre from shipment records.
- **Historical comparison:** Uses previous observed weeks to estimate a route's historical cost baseline.
- **Peer comparison:** Compares a route against other routes of the same route type during the same week.
- **Deterministic anomaly detection:** Uses configurable thresholds and historical statistical signals.
- **Context-note retrieval:** Uses TF-IDF retrieval by default to find potentially relevant notes.
- **Evidence verification:** Checks route applicability, date windows, positive cost impact, and plausible causes.
- **Conservative explanations:** Does not automatically treat retrieval similarity as proof.
- **Citation auditing:** Runs an independent rule-based check on generated output.
- **Reproducibility:** Includes a script that checks whether three pipeline runs produce byte-identical output files.
- **Evaluation tooling:** Compares predictions with supplied case labels while keeping missing labels excluded from scoring.
- **Optional local LLM integration:** Ollama can optionally be used for wording; it must not change anomaly flags or supporting citations.

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| Data processing | pandas |
| Context retrieval | TF-IDF baseline |
| Optional semantic retrieval | Sentence Transformers |
| Optional wording generation | Local Ollama |
| Testing | pytest |
| Configuration | YAML |
| Output | CSV and Markdown |
| Version control | Git and GitHub |

## Architecture

```text
Shipment Records
      |
      v
Schema and Value Validation
      |
      v
Weekly Route-Level Aggregation
      |
      v
Weighted Cost per Tonne-Kilometre
      |
      v
Historical and Peer Baselines
      |
      v
Deterministic Anomaly Detection
      |
      v
Context-Note Retrieval (TF-IDF by default)
      |
      v
Rule-Based Evidence Verification
      |
      +-----------------------------+
      |                             |
      v                             v
Supporting Note Found         No Valid Note Found
      |                             |
      v                             v
Justified Anomaly              Unexplained Anomaly
      |                             |
      +--------------+--------------+
                     |
                     v
          Watchlist CSV and Audit
```

The pipeline separates numerical anomaly detection from note-based justification. A route can have a detected anomaly even when a note provides a plausible explanation.

## Project Structure

```text
watchdog/
├── config.yaml
├── requirements.txt
├── README.md
├── data/
│   ├── shipment_records.csv
│   ├── context_notes.csv
│   └── sample_output_format_v2.csv
├── docs/
│   └── repro_report.md
├── eval/
│   ├── labeled_cases.csv
│   ├── label_cases.py
│   └── run_eval.py
├── outputs/
│   ├── watchlist.csv
│   ├── citation_audit.csv
│   └── eval_report.md
├── scripts/
│   ├── audit_output.py
│   └── repro_check.sh
├── src/
│   └── watchdog/
│       ├── cli.py
│       ├── weekly.py
│       ├── baselines.py
│       ├── flags.py
│       ├── retrieval.py
│       ├── verify.py
│       └── pipeline.py
└── tests/
```

The exact contents may evolve as the implementation changes.

## Prerequisites

- Python 3.11 or newer
- Git
- A terminal such as Windows CMD, PowerShell, Git Bash, or a Unix shell
- Internet access for installing Python dependencies

The default TF-IDF configuration does not require downloading a neural embedding model. Optional semantic retrieval and Ollama functionality have additional setup requirements.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/KishanSingh29/shipping-cost-watchdog.git
cd shipping-cost-watchdog
```

### 2. Create a virtual environment

**Windows CMD:**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Project

Run commands from the project root with the virtual environment activated.

### Windows CMD

Set the source directory on the Python module path:

```cmd
set PYTHONPATH=src
```

Run the pipeline:

```cmd
python -m watchdog.cli --config config.yaml
```

Run automated tests:

```cmd
python -m pytest -q
```

Run the citation audit:

```cmd
python scripts\audit_output.py
```

Run evaluation:

```cmd
python eval\run_eval.py
```

### PowerShell

```powershell
$env:PYTHONPATH = "src"

python -m watchdog.cli --config config.yaml
python -m pytest -q
python scripts/audit_output.py
python eval/run_eval.py
```

### macOS/Linux

```bash
export PYTHONPATH=src

python -m watchdog.cli --config config.yaml
python -m pytest -q
python scripts/audit_output.py
python eval/run_eval.py
```

### Expected pipeline output

The verified local run produced:

```text
Weekly route rows analyzed: 728
Flags written: 5
Output: outputs/watchlist.csv
```

These figures describe the supplied dataset and current configuration. They are not performance metrics and may change when the input data or configuration changes.

## Anomaly Detection Logic

### 1. Weekly cost aggregation

Shipment records are aggregated by route, route type, and week.

The weekly cost-per-tonne-kilometre metric is:

\[
\text{Cost per tonne-km} =
\frac{\sum \text{Freight Cost (INR)}}
{\sum(\text{Quantity (tonnes)} \times \text{Distance (km)})}
\]

This ratio-of-sums calculation weights shipment records according to their transported tonne-kilometres.

Weeks run from Monday through Sunday. The `week_of` field represents the Monday starting that week.

### 2. Historical baseline

The system calculates a historical baseline using up to eight previous observed route-weeks.

The current week is excluded from its own historical baseline to avoid leakage.

If there is insufficient prior history to calculate a baseline, the route-week cannot be flagged using the normal detection logic.

### 3. Peer baseline

The peer baseline compares a route against other routes of the same route type during the same week.

The current route is excluded from its peer group.

### 4. Flagging rules

The detector uses configurable thresholds to check:

- Whether the current cost is higher than the previous observed week's cost.
- Whether the cost exceeds the route's historical average by the configured threshold.
- Whether the cost exceeds the peer average or satisfies the configured historical z-score condition.
- Whether the required baselines are available.

These thresholds are explicit starting assumptions defined in `config.yaml`. They are not trained parameters, and they should not be tuned against held-out evaluation labels without a documented methodology.

## Context Retrieval and Verification

Retrieval finds candidate notes that may be relevant to a flagged route-week. Retrieval similarity alone does not establish that a note explains a cost increase.

The default retrieval implementation uses TF-IDF. A Sentence Transformers adapter exists, but full semantic retrieval has not been validated by the current test results.

Candidate notes are checked against evidence requirements, including:

- **Route applicability:** The note must apply to the affected route or explicitly apply to all routes.
- **Date compatibility:** The note's effective period must overlap the relevant cost event according to the verification rules.
- **Positive cost impact:** The note must indicate a plausible increase in costs.
- **Plausible cause:** The note must describe a plausible reason for the increase.
- **Contradictory evidence:** Wording indicating no material cost impact, improved conditions, or no rate change can disqualify a note.

If a note passes the checks, its identifier is included in the output. Otherwise, the detected anomaly is classified as unexplained.

A note that passes verification is evidence of a possible cause, not proof that it fully explains the observed increase.

## Output Format

The main output is:

```text
outputs/watchlist.csv
```

It contains the following eight columns:

| Column | Meaning |
|---|---|
| `route` | Route name |
| `week_of` | Monday starting the relevant week |
| `cost_per_tonne_km` | Calculated weekly cost per tonne-kilometre |
| `vs_own_history` | Comparison with the route's historical baseline |
| `vs_similar_routes` | Comparison with comparable routes |
| `flagged` | `Yes` or `No (justified)` |
| `matched_note_id` | Supporting context-note identifier, if any |
| `reason` | Explanation of the decision |

**Flag interpretation:**

- `Yes`: A numerical anomaly was detected, and no supporting note passed the verification checks.
- `No (justified)`: A numerical anomaly was detected, and a contextual note passed the verification checks.

Both statuses represent detected numerical anomalies. `No (justified)` does not mean that no anomaly was detected.

Other generated artifacts include:

- `outputs/citation_audit.csv` — results from the citation auditor.
- `outputs/eval_report.md` — evaluation results for the currently labelled cases.
- `docs/repro_report.md` — reproducibility documentation.

## Evaluation

The evaluation dataset is:

```text
eval/labeled_cases.csv
```

It contains 30 proposed cases covering positive anomalies, negative examples, route mismatches, date-window cases, recovery scenarios, and note-selection scenarios.

The evaluation script is:

```bash
python eval/run_eval.py
```

### Current evaluation status

The current local report scores 28 cases and excludes two cases (`C016` and `C017`) because their route-week data is missing.

The latest report showed:

| Metric | Reported score |
|---|---:|
| Flag accuracy | 1.000 |
| Verdict accuracy | 1.000 |
| Note ID accuracy | 1.000 |

**These scores are provisional, not independently validated performance estimates.**

The current labels still require independent review against the shipment records and context notes. Some labels were assigned using the observed pipeline output, which can produce circular evaluation if the same predictions are used to define the expected answers.

Before claiming validated accuracy:

1. Inspect each evaluation case against the raw shipment data and context notes.
2. Assign expected labels independently of the prediction being evaluated.
3. Resolve inconsistent or ambiguous cases.
4. Keep missing-data cases separate from genuine negative cases.
5. Rerun evaluation after the labels have been reviewed.

Cases sharing the same route and week necessarily share the same prediction. Duplicate cases should therefore be treated as repeated checks, not as independent observations.

## Testing and Reproducibility

### Automated tests

Run:

```bash
python -m pytest -q
```

The current local verification completed successfully with:

```text
16 passed
```

Test results apply to the current local test suite and do not establish that every optional retrieval or LLM component has been validated.

### Citation audit

Run:

```bash
python scripts/audit_output.py
```

The citation auditor is a separate, conservative rule-based cross-check. It is useful for identifying unsupported note references, but it is not a formal proof that every explanation is entailed by its source.

### Reproducibility check

The script runs the pipeline three times and checks whether the output files are byte-identical.

**macOS/Linux:**

```bash
bash scripts/repro_check.sh
```

**Windows with Git for Windows installed, from CMD:**

```cmd
"C:\Program Files\Git\bin\bash.exe" scripts/repro_check.sh
```

The verified local run produced:

```text
Weekly route rows analyzed: 728
Flags written: 5
Weekly route rows analyzed: 728
Flags written: 5
Weekly route rows analyzed: 728
Flags written: 5
PASS: three outputs are byte-identical.
```

This demonstrates repeatability for the tested environment, dataset, and configuration. It does not establish correctness of the anomaly rules or the validity of the evaluation labels.

### Optional LLM usage

The token log at `outputs/token_log.csv` is generated only when an Ollama call is made. When no live LLM call occurs, no token usage is claimed.

Local inference may still consume hardware resources and electricity even when no paid API is used.

## Configuration

The project is configured through:

```text
config.yaml
```

It contains input and output paths, anomaly thresholds, historical-window settings, retrieval configuration, and optional LLM settings.

- `retrieval.method: tfidf` selects the default lexical retrieval baseline.
- `retrieval.method: semantic` selects the Sentence Transformers adapter and requires the relevant model to be downloaded.
- `llm.provider: none` disables LLM calls.
- An optional Ollama configuration can be used for explanation wording.

Optional LLM-generated wording must not be allowed to change the numerical anomaly decision or the selected supporting note.

## Known Limitations

- The default TF-IDF retriever is lexical retrieval, not full semantic RAG.
- The Sentence Transformers adapter and full semantic workflow have not been validated by the current test suite.
- Date-window verification relies on conservative text rules and requires independent adversarial testing.
- Rule-based note verification cannot prove that a note fully explains a cost increase.
- The citation auditor is a guardrail rather than a formal entailment verifier.
- Current evaluation metrics are provisional until expected labels are independently reviewed.
- Two evaluation cases currently lack matching route-week data and are excluded from scoring.
- Thresholds are starting assumptions rather than statistically calibrated production settings.
- Reproducibility has been verified for the supplied local dataset and configuration; other environments may differ.

## Future Improvements

Potential next steps include:

1. Independently validate all evaluation labels.
2. Add precision, recall, F1-score, and confusion-matrix reporting for anomaly detection.
3. Add more adversarial tests for date windows, contradictory notes, and route applicability.
4. Validate the Sentence Transformers retrieval path end to end.
5. Add retrieval-quality metrics such as Recall@K and MRR using independently labelled relevance judgments.
6. Add structured logs and richer error reporting.
7. Evaluate threshold stability on a separate validation dataset.
8. Add integration tests for optional Ollama wording without allowing it to alter decisions or citations.

These are planned improvements, not claims about completed functionality.
