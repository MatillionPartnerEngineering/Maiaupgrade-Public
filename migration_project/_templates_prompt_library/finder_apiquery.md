Analyze the Matillion ETL export file and extract API Query component profiles.

**INPUT:**
- File: METL Exports/INGESTION_FRAMEWORK.json
- Supporting data: Migration Context/component_details.csv

**OUTPUT FORMAT:**

Provide a structured report with the following sections:

1. **Executive Summary**
   - Analysis scope (file name)
   - Component type analyzed
   - Total components identified
   - Unique source systems count
   - Environment coverage

2. **API Source System Inventory**
   - Table with columns: Source System, Endpoint Count, Pipeline Context, Environment(s), Status
   - Sort by endpoint count (descending)

3. **Detailed Endpoint Breakdown**
   - Group by complexity: High (5+ endpoints), Medium (2-4 endpoints), Standard (1 endpoint)
   - For each system include:
     - Pipeline name(s)
     - Table of endpoints with: Component Name, Function, Data Entity
     - Integration pattern description

4. **Environment Distribution Analysis**
   - Identify DEV/UAT/PROD variations
   - Note any environment-specific deployments
   - Flag archived/deprecated systems

5. **Complexity Classification**
   - Define classification criteria
   - Table with: Complexity Level, Endpoint Range, Systems, Count

6. **Authentication Patterns**
   - Identify authentication methods used
   - Group systems by pattern type

7. **Migration Considerations**
   - Priority levels based on complexity
   - Special considerations for multi-environment systems
   - Archived system recommendations

8. **Summary Statistics**
   - Total component count
   - Active vs archived breakdown
   - Multi-endpoint system count
   - Environment distribution

**SEARCH SCOPE:**
- Component Type: "API Query"
- Source: component_details.csv or JSON export
- Include component_exists field status (0=unsupported, 1=supported)
