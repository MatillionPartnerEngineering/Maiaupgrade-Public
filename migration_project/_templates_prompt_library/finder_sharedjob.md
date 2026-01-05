# METL Export File Analysis: Shared Jobs ("Unknown" Components)

**Target File:** `[FILE_NAME]`

## Objective
Analyze the provided METL export file to identify and categorize all shared jobs, which appear in the export as "Unknown" components.

---

## 1. Unique Unknown Component IDs
*List every unique component ID identified as "Unknown" or a Shared Job within the export.*

## 2. Detailed Component Analysis
*For each unique ID identified above, provide the following details:*

### Component ID: `[ID_HERE]`
* **Type Identifier:** `[e.g., Job, SharedJob, Unknown]`
* **Total Occurrence Count:** `[Number]`
* **Common Component Names:**
    * `[Name 1]`
    * `[Name 2]`
* **Inferred Purpose/Function:**
    * *Based on naming patterns (e.g., "Audit Logging", "Error Handling").*
* **Usage Context (Pipelines):**
    * `[Pipeline A]`
    * `[Pipeline B]`
    * `[Pipeline C]`

*(Repeat this section for each unique ID)*

---

## 3. Summary of Shared Jobs

| Unknown Component ID | Total Occurrences | Likely Shared Job Name/Purpose |
| :--- | :--- | :--- |
| `[ID_1]` | `[Count]` | `[Purpose]` |
| `[ID_2]` | `[Count]` | `[Purpose]` |
| `[ID_3]` | `[Count]` | `[Purpose]` |

---

## 4. Critical Infrastructure Highlights
*Identify any shared jobs that constitute critical infrastructure based on heavy usage.*

* **Heavily Used Components:**
    * `[Component Name/ID]` (Used in X pipelines)
* **Risk Assessment:**
    * *Note any dependencies that, if broken, would affect a large percentage of the framework.*