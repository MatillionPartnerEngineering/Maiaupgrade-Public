Analyze the Matillion ETL export file and extract all data ingestion components with their connection and authentication requirements.

**INPUT:**
- File: METL Exports/[PROJECT_NAME].json
- Supporting data: Migration Context/component_details.csv

**OUTPUT FORMAT:**

Provide a structured report with the following sections:

1. **Executive Summary**
   - Analysis scope (file name)
   - Total ingestion components identified
   - Unique source systems count
   - Connector types in use
   - Environment coverage

2. **Ingestion Component Inventory by Connector Type**

   Group components into categories:
   - **API-Based Connectors**: API Query, API Extract
   - **Database Connectors**: Database Query, specific DB queries (Oracle Query, SQL Server Query, etc.)
   - **SaaS Connectors**: Salesforce Query, Zuora Bulk Query, NetSuite Query, OData Query, Jira Query, etc.
   - **Cloud Storage**: S3 Load, Azure Blob Storage Load, GCS Load
   - **Cloud Data Warehouses**: Google BigQuery, Snowflake (cross-instance), Redshift Query
   - **NoSQL/Other**: DynamoDB Query, MongoDB Query

   For each category, provide table with:
   | Source System | Component Type | Component Name | Pipeline Context | Environment | Status |

3. **Authentication Requirements by Source System**

   For each unique source system, document:

   **System Name**: [e.g., Salesforce, NetSuite, SQL Server]
   
   **Connection Type**: [e.g., OAuth 2.0, API Key, Username/Password, Service Account]
   
   **Required Credentials**:
   - List all authentication parameters needed
   - Examples:
     - API Key/Secret
     - Username/Password
     - OAuth Client ID/Secret
     - Service Account JSON
     - Token/Bearer Authentication
     - Certificate-based auth
     - Multi-factor authentication requirements
   
   **Connection Configuration**:
   - Hostname/Endpoint URL
   - Port (if applicable)
   - Database/Schema/Instance names
   - Region (for cloud services)
   - API Version
   - Additional connection properties
   
   **Network Requirements**:
   - Public internet access or VPN required
   - IP whitelist requirements
   - Firewall rules needed
   - SSL/TLS requirements
   
   **Component Count**: [Number of components using this connection]
   
   **Pipelines Using This Connection**: [List of pipeline names]

4. **Connection Profile Mapping**

   If connection profiles are used in the export:
   
   | Connection Profile Name | Connector Type | Source System | Used By (Pipeline Count) | Authentication Method |

5. **Environment-Specific Connections**

   Identify connections that vary by environment:
   
   | Source System | DEV Config | UAT Config | PROD Config | Differences |
   
   Note:
   - Different hostnames/endpoints
   - Different credentials
   - Different databases/schemas

6. **High-Risk/Complex Authentication Patterns**

   Flag systems with:
   - Multi-stage authentication (e.g., token retrieval then API calls)
   - Credential rotation requirements
   - OAuth refresh token management
   - Certificate expiration tracking
   - VPN/network dependencies
   - Custom authentication flows

7. **Authentication Pattern Summary**

   | Authentication Type | System Count | Systems | Complexity Rating |
   
   Group by:
   - OAuth 2.0
   - API Key/Token
   - Basic Auth (Username/Password)
   - Service Account/JSON Key
   - Certificate-based
   - Multi-factor/Multi-stage
   - Custom/Proprietary

8. **Migration Readiness - Authentication Checklist**

   For each source system, provide:
   
   **System**: [Name]
   
   **Credentials Needed for Migration**:
   - [ ] API credentials/keys
   - [ ] Service account details
   - [ ] OAuth app configuration
   - [ ] VPN/network access
   - [ ] IP whitelisting in source system
   - [ ] Certificate files
   - [ ] Connection strings
   
   **Known Issues/Considerations**:
   - Credential format changes between ETL versions
   - Deprecated authentication methods
   - New security requirements in DPC
   
   **Documentation Links**: [If available]

9. **Summary Statistics**

   - Total ingestion components: [count]
   - Unique source systems: [count]
   - Connector types in use: [count]
   - Systems requiring OAuth: [count]
   - Systems requiring VPN: [count]
   - Systems with multi-environment configs: [count]
   - Unsupported components (component_exists=0): [count]

**SEARCH SCOPE:**
- Component Types: API Query, API Extract, Database Query, Salesforce Query, NetSuite Query, 
  Zuora Bulk Query, OData Query, Jira Query, S3 Load, Google BigQuery, DynamoDB Query, 
  Bing Ads Query, and all other data ingestion components
- Source: component_details.csv or JSON export