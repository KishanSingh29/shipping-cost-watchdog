# Evaluation report

Cases in template: 30
Cases scored: 28
Cases excluded due to incomplete labels: 2

## Metric definitions

- **Flag accuracy:** numeric anomaly detection accuracy. Both `Yes` and `No (justified)` mean an anomaly was detected.
- **Verdict accuracy:** accuracy of `justified`, `unexplained`, or `not_flagged` verdicts.
- **Note ID accuracy:** exact match of the expected and predicted supporting note IDs. Two blank IDs count as a match.

## Metrics

- Flag accuracy: **1.000**
- Verdict accuracy: **0.964**
- Note ID accuracy: **0.964**

## Labelled case results

| Case | Route | Week | Expected flag | Actual flag | Expected verdict | Actual verdict | Expected note | Actual note |
|---|---|---|---:|---:|---|---|---|---|
| C001 | Delhi-Jaipur | 2024-11-11 | 1 | 1 | unexplained | unexplained | (blank) | (blank) |
| C002 | Ahmedabad-Mumbai | 2025-01-20 | 1 | 1 | justified | justified | N002 | N002 |
| C003 | Chennai-Bangalore | 2025-02-24 | 1 | 1 | justified | justified | N001 | N001 |
| C004 | Chennai-Bangalore | 2025-03-10 | 1 | 1 | unexplained | unexplained | (blank) | (blank) |
| C005 | Mumbai-Delhi | 2025-05-12 | 1 | 1 | unexplained | justified | (blank) | N003 |
| C006 | Mumbai-Pune | 2025-09-15 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C007 | Delhi-Jaipur | 2024-05-20 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C008 | Mumbai-Delhi | 2024-07-29 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C009 | Kolkata-Bhubaneswar | 2025-06-09 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C010 | Delhi-Jaipur | 2024-03-11 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C011 | Delhi-Jaipur | 2025-10-27 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C012 | Chennai-Bangalore | 2025-03-17 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C013 | Ahmedabad-Mumbai | 2025-02-24 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C014 | Delhi-Jaipur | 2025-02-24 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C015 | Mumbai-Delhi | 2025-02-24 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C018 | Delhi-Jaipur | 2025-05-12 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C019 | Chennai-Bangalore | 2025-03-03 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C020 | Chennai-Bangalore | 2025-03-10 | 1 | 1 | unexplained | unexplained | (blank) | (blank) |
| C021 | Ahmedabad-Mumbai | 2025-01-13 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C022 | Mumbai-Delhi | 2025-05-05 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C023 | Mumbai-Delhi | 2025-05-19 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C024 | Delhi-Jaipur | 2025-05-12 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C025 | Chennai-Bangalore | 2025-02-17 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C026 | Chennai-Bangalore | 2025-03-17 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C027 | Kolkata-Bhubaneswar | 2025-09-22 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C028 | Delhi-Jaipur | 2024-05-20 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C029 | Mumbai-Delhi | 2024-07-29 | 0 | 0 | not_flagged | not_flagged | (blank) | (blank) |
| C030 | Ahmedabad-Mumbai | 2025-01-20 | 1 | 1 | justified | justified | N002 | N002 |

## Important limitations

- Metrics are trustworthy only when labels are independently verified against source data and context notes.
- Cases with the same route and week share the same prediction.
- Missing route-week data is not automatically evidence of a negative case.
- A supporting note is evidence of a possible cause, not proof that it explains the entire cost increase.

