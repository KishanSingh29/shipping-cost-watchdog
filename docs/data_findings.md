# Phase 1 — Data Inspection Findings

## 1. Input files and schema

### `shipment_records.csv`
- Shape: **2,940 rows × 10 columns**.
- Columns, in source order:
  1. `shipment_id` — object/string
  2. `origin` — object/string
  3. `destination` — object/string
  4. `route_type` — object/string
  5. `material` — object/string
  6. `quantity_tonnes` — float64
  7. `distance_km` — float64
  8. `freight_cost_inr` — int64
  9. `shipment_date` — source string, parseable as date
  10. `transporter` — object/string
- Date range: **2024-01-01 through 2025-12-28**.
- Parsed weekly range (Monday week starts): **2024-01-01 through 2025-12-22**, 104 consecutive weeks.
- Missing values: **0 in every column**. Blank-string checks: **0 in every column**.
- Exact duplicate rows: **0**. Duplicate `shipment_id`: **0**.
- Invalid dates: **0**. Invalid `route_type` values outside Short/Medium/Long: **0**.
- Non-positive values: quantity **0**, distance **0**, freight cost **0**.

### Route inventory
There are **7 distinct (origin, destination, route_type) groups**. Every route has records in all 104 weeks; no route-week gaps were detected.

| Origin | Destination | Route type | Shipments |
|---|---|---:|---:|
| Ahmedabad | Mumbai | Medium | 421 |
| Chennai | Bangalore | Medium | 410 |
| Delhi | Chennai | Long | 419 |
| Delhi | Jaipur | Short | 416 |
| Kolkata | Bhubaneswar | Medium | 433 |
| Mumbai | Delhi | Long | 423 |
| Mumbai | Pune | Short | 418 |

| Route type | Shipment count |
|---|---:|
| Short | 834 |
| Medium | 1,264 |
| Long | 842 |

The overall 104-week calendar is continuous from Monday 2024-01-01 through Monday 2025-12-22. Each of the seven routes has data in all 104 weeks; minimum shipment count in a route-week is 3.

### Numeric ranges and outlier screening

| Field | Minimum | Maximum | `<= 0` count | IQR-rule outliers* |
|---|---:|---:|---:|---:|
| `quantity_tonnes` | 9.0 | 22.0 | 0 | 0 |
| `distance_km` | 147.0 | 2,220.0 | 0 | 0 |
| `freight_cost_inr` | 4,710 | 105,839 | 0 | 192 |

\*Outliers are flagged for inspection using the conventional 1.5×IQR rule; this is a screening signal, not proof of bad data. Do not delete or winsorize these values automatically. Freight cost naturally varies with quantity and distance, so inspect cost-per-tonne-km and route-week aggregates before deciding whether any record is erroneous.

Materials: Packaged Foods (530), Textiles (491), FMCG Cartons (490), Cement (478), Auto Parts (477), Steel Coils (474). There are 6 distinct transporters.

## 2. `context_notes.csv` structure and note inventory

- Shape: **10 rows × 4 columns**.
- Columns: `note_id` (string), `date` (source string; parseable date), `applies_to` (string), `note` (string).
- Missing values and blank strings: **0**.
- `applies_to` is free text, not a normalized origin/destination pair. It contains exact corridors such as `Chennai-Bangalore`, broad scope `All Routes`, and other corridors not necessarily present in the shipment dataset. The note body provides effective date ranges, causal direction, and caveats. The pipeline must parse/validate those claims conservatively rather than treating every retrieved note as support.
- The `date` field appears to be the note's start/announcement date; where the note states a more precise effective window, use that stated window. If a note does not establish a cost increase, it must not justify an increase flag.

### All 10 notes (verbatim)

| Note ID | Date | Applies to | Note |
|---|---|---|---|
| N001 | 2025-02-24 | Chennai-Bangalore | Heavy flooding on the Chennai-Bangalore highway disrupted normal truck movement from Feb 24 to Mar 8, forcing longer detours and higher trip costs. Roads were passable again by Mar 9. |
| N002 | 2025-01-20 | Ahmedabad-Mumbai | A regional festival week saw a temporary surcharge applied by transporters on the Ahmedabad-Mumbai corridor due to high demand and limited truck availability. |
| N003 | 2025-05-05 | All Routes | Diesel prices rose nationwide starting this week, pushing up transportation costs across all routes by roughly 5-7%. |
| N004 | 2024-03-11 | All Routes | A new toll plaza was commissioned on a national highway stretch, but the affected routes are not part of this dataset. |
| N005 | 2024-07-29 | Mumbai-Delhi | Scheduled highway maintenance work between Mumbai and Delhi caused minor delays for about a week; costs were not significantly affected. |
| N006 | 2025-09-22 | All Routes | A logistics industry report noted overall demand for freight capacity remained stable this quarter with no major disruptions reported. |
| N007 | 2024-05-20 | Delhi-Jaipur | Local authorities announced improved road conditions on the Delhi-Jaipur stretch after resurfacing work was completed. |
| N008 | 2025-06-09 | Kolkata-Bhubaneswar | No significant disruptions were reported on the Kolkata-Bhubaneswar corridor this quarter; freight movement remained normal. |
| N009 | 2025-03-17 | Chennai-Bangalore | Highway authorities confirmed the Chennai-Bangalore route returned to normal conditions after flood-related repairs were completed. |
| N010 | 2025-10-27 | All Routes | A new vehicle tracking mandate was introduced for commercial fleets; compliance costs were absorbed by transporters without a rate change. |

Important negative/non-supporting evidence includes N004 (affected routes explicitly outside this dataset), N005 (costs not significantly affected), N006 (stable demand/no major disruptions, not a cause of increase), N007 (improved road conditions), N008 (normal movement), N009 (route returned to normal), and N010 (costs absorbed, no rate change). Retrieval similarity alone must never make these supporting notes.

## 3. `sample_output_format_v2.csv` inspection

The first line defines the required eight-column contract, in this exact order:

`route, week_of, cost_per_tonne_km, vs_own_history, vs_similar_routes, flagged, matched_note_id, reason`

The file contains three illustrative data rows after the header, but **the file is not valid RFC-style CSV as supplied**: unquoted commas inside the `reason` prose create inconsistent field counts (the standard CSV parser errors on line 4). Therefore, use the header as the column contract and preserve the example values as examples only; do not infer that the entire file is a clean parseable template. Generated output must be written with a proper CSV writer so prose commas are quoted correctly. Before submission, confirm with the hiring contact if the grader expects the provided example rows to be retained; the brief describes this as an output format, so the implementation should normally emit generated result rows, not append these examples.

The examples use `Yes` / `No (justified)` in `flagged`, percentage strings in both comparison fields, a blank `matched_note_id` for unexplained flags, and note IDs such as `N002` for justified examples. Exact accepted categorical values and numeric formatting are not fully specified by the header alone; follow the examples conservatively and document the interpretation in README.

## 4. Proposed cleaning and handling rules

1. Load CSVs without modifying source files; preserve originals under `data/`.
2. Parse `shipment_date` and note `date` into dates; fail fast and log invalid rows if future input has unparseable dates.
3. Strip surrounding whitespace from string fields, but do not silently rewrite route names or route direction.
4. Validate required columns and allowed `route_type` values; fail fast for missing required columns or unknown route types.
5. Do not drop rows for outlier status alone. For rows with missing required fields, invalid dates, or non-positive quantity/distance/cost, log each affected `shipment_id` and reason to a cleaning report; exclude only those invalid rows from calculations. Current files have no such rows, so expected drop count is **0**.
6. Treat a route as the directed pair `(origin, destination)` plus `route_type`; do not assume A→B is equivalent to B→A.
7. Compute weekly cost from valid records using the brief's required aggregation choice: `sum(freight_cost_inr) / sum(quantity_tonnes * distance_km)` for each route-week.
8. Outlier screening uses the IQR rule for reporting only; no automatic removal or winsorization.
9. Notes are evidence, not labels. Require scope, effective-time overlap, plausible cause, and explicit positive cost direction before assigning `matched_note_id`.

## 5. Assumptions and questions to resolve in later phases

- The brief defines a route as same start and end point and asks grouping by route plus `route_type`; implementation will use directed `(origin, destination, route_type)`.
- Weekly aggregation uses the ratio of sums, not the average of individual shipment ratios.
- History uses only prior observed route-weeks; because the current data has every week for every route, no missing-week policy is needed for these files, but code should still avoid look-ahead.
- Similar-route baseline can be computed from the other routes in the same `route_type` and week; if there are no peers, return null rather than fabricate a baseline.
- The supplied output examples are malformed CSV after the header due to unescaped commas in prose. The header is clear; exact expected values for `flagged` should be validated against the examples/brief before final submission.
- Note effective windows should use explicit date ranges in note text where present. For notes with only a start date and no end date, do not invent a long duration; define a conservative documented rule in the retrieval phase.
