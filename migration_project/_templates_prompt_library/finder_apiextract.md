Analyze the Matillion ETL export file and extract API Extract component profiles.

**INPUT:**
- File: METL Exports/[PROJECT_NAME].json
- Supporting data: Migration Context/component_details.csv

**OUTPUT FORMAT:**

Provide a structured report with the following sections:

1. **Executive Summary**
   - Analysis scope (file name)
   - Component type analyzed (API Extract)
   - Total components identified
   - Unique source systems count
   - Environment coverage

2. **API Extract Source System Inventory**
   - Table with columns: Source System, Connector Count, Pipeline Context, Environment(s), Status
   - Sort by connector count (descending)
   - Note: API Extract differs from API Query - it uses pre-built connectors

3. **Detailed Connector Breakdown**
   - Group by complexity: High (5+ connectors), Medium (2-4 connectors), Standard (1 connector)
   - For each system include:
     - Pipeline name(s)
     - Table of connectors with: Component Name, Object/Entity Type, Sync Pattern
     - Connector configuration pattern (incremental, full, delta)

4. **Environment Distribution Analysis**
   - Identify DEV/UAT/PROD variations
   - Note any environment-specific deployments
   - Flag archived/deprecated connectors

5. **Complexity Classification**
   - Define classification criteria (based on connector count and data volume)
   - Table with: Complexity Level, Connector Range, Systems, Count

6. **Authentication & Connection Patterns**
   - Identify authentication methods used
   - Connection profile names
   - OAuth vs API key vs basic auth patterns
   - Group systems by authentication type

7. **Data Sync Patterns**
   - Incremental sync configurations
   - Full refresh patterns
   - Delta detection methods
   - Timestamp-based vs bookmark-based sync

8. **Migration Considerations**
   - Priority levels based on complexity
   - Pre-built connector availability in Data Productivity Cloud
   - Special considerations for custom/deprecated connectors
   - Environment-specific configurations

9. **Summary Statistics**
   - Total API Extract component count
   - Active vs archived breakdown
   - Multi-connector system count
   - Environment distribution
   - Supported vs unsupported connector breakdown

**SEARCH SCOPE:**
- Component Type: "API Extract"
- Source: component_details.csv or JSON export
- Include component_exists field status (0=unsupported, 1=supported)
- Focus on pre-built connector usage patterns