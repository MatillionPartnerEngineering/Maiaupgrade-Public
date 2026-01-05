# Matillion GTM Analysis and Recommendations

**Generated:** 2025-11-17 20:33:15
**Data Warehouse:** snowflake

---

## Executive Summary

| Metric | Value |
| --- | --- |
| Projects Analyzed | 1 |
| Total Jobs | 42977 |
| Total Components | 8634 |
| Total Variables | 105 |
| Max Concurrent Tasks | 7.7 |
| Recommended Agent Instances | 2 |

### Component Migration Analysis

Based on analysis of 8634 component instances across 1 project(s) with components:

| Migration Type | Percentage | Effort Level |
| --- | --- | --- |
| Type 1 (Auto-convert) | 83.7% | Minimal - Automated conversion |
| Type 2 (Minor changes) | 10.5% | Low - Simple refactoring |
| Type 3 (Significant work) | 5.8% | Medium-High - Custom development |

## Detailed Project Analysis

### N-ABLE/Production (Versions: default)


**Project Metrics:**

| Metric | Value |
| --- | --- |
| Total Tasks | 42977 |
| Max Concurrent Tasks | 7.7 |
| Total Components | 8634 |
| Type 1 (Auto-convert) | 83.7% |
| Type 2 (Minor changes) | 10.5% |
| Type 3 (Significant work) | 5.8% |
| Variables | 105 |
| Python Usage | Yes |
| Custom Libraries | 36 |
| Versions Analyzed | default |

**GTM Recommendations:**

| Category | Recommendation |
| --- | --- |
| Deployment Type | Customer Hosted Agent |
| License Type | Enterprise |
| Agent Instances | 2 |
| Upgrade Complexity | High |
| Complexity Score | 872.0 |
| Migration Size | Custom |
| Effort Estimate | Varies (53+ days) |
| Confidence Level | Low |

**Key Considerations:**

- More than 5 custom Python libraries suggest CHA need (36 found)
- Legacy Python interpreters require CHA (Jython, Python 2)

**Component Breakdown:**

| Component | Count | Type | Migration Effort |
| --- | --- | --- | --- |
| nable.audit_log | 958 | Type 1 | Auto-convert |
| Start | 890 | Type 1 | Auto-convert |
| Run Orchestration | 580 | Type 1 | Auto-convert |
| Query Result To Scalar | 481 | Type 1 | Auto-convert |
| SQL Script | 453 | Type 2 | Minor changes |
| Python Script | 394 | Type 3 | Significant work |
| If | 376 | Type 1 | Auto-convert |
| End Success | 375 | Type 1 | Auto-convert |
| End Failure | 368 | Type 1 | Auto-convert |
| Table Input | 355 | Type 1 | Auto-convert |
| Or | 315 | Type 1 | Auto-convert |
| Filter | 249 | Type 1 | Auto-convert |
| Query Result To Grid | 241 | Type 1 | Auto-convert |
| Run Transformation | 220 | Type 1 | Auto-convert |
| Calculator | 218 | Type 1 | Auto-convert |
| Grid Iterator | 202 | Type 1 | Auto-convert |
| Table Update | 157 | Type 1 | Auto-convert |
| Deprecated: API Query | 150 | Unknown | To be assessed |
| Temporary Output | 133 | Type 1 | Auto-convert |
| Database Query | 117 | Type 2 | Minor changes |
| Table Output | 113 | Type 1 | Auto-convert |
| Join | 94 | Type 1 | Auto-convert |
| Create Table | 92 | Type 1 | Auto-convert |
| SQL | 86 | Type 2 | Minor changes |
| Deprecated: Python Script | 84 | Unknown | To be assessed |
| Detect Changes | 74 | Type 1 | Auto-convert |
| Begin | 72 | Type 1 | Auto-convert |
| Commit | 71 | Type 1 | Auto-convert |
| Rollback | 71 | Type 1 | Auto-convert |
| Replicate | 70 | Type 2 | Minor changes |
| Retry | 65 | Type 1 | Auto-convert |
| Table Metadata To Grid | 47 | Type 1 | Auto-convert |
| Truncate Table | 31 | Type 1 | Auto-convert |
| nable.sns_notification | 29 | Type 1 | Auto-convert |
| Google BigQuery | 28 | Type 1 | Auto-convert |
| Assert Table | 26 | Type 1 | Auto-convert |
| Zuora Bulk Query | 24 | Type 3 | Significant work |
| Fixed Flow | 24 | Type 1 | Auto-convert |
| Pivot | 23 | Type 1 | Auto-convert |
| S3 Load | 22 | Type 1 | Auto-convert |
| Rename | 21 | Type 1 | Auto-convert |
| Salesforce Query | 20 | Type 2 | Minor changes |
| Distinct | 19 | Type 1 | Auto-convert |
| Lead/Lag | 19 | Type 1 | Auto-convert |
| Loop Iterator | 16 | Type 1 | Auto-convert |
| Table Iterator | 16 | Type 1 | Auto-convert |
| Aggregate | 15 | Type 1 | Auto-convert |
| Jira Query | 10 | Type 1 | Auto-convert |
| OData Query | 9 | Type 1 | Auto-convert |
| SNS Message | 6 | Type 1 | Auto-convert |
| Rank | 6 | Type 1 | Auto-convert |
| Marketo Query | 6 | Type 2 | Minor changes |
| nable.job_dependency | 6 | Type 1 | Auto-convert |
| DynamoDB Query | 5 | Type 1 | Auto-convert |
| Append To Grid | 5 | Type 1 | Auto-convert |
| Window Calculation | 4 | Type 1 | Auto-convert |
| Data Transfer Object | 4 | Type 1 | Auto-convert |
| Convert Type | 4 | Type 1 | Auto-convert |
| And | 3 | Type 1 | Auto-convert |
| Construct Variant | 2 | Type 1 | Auto-convert |
| S3 Unload | 2 | Type 1 | Auto-convert |
| Salesforce Bulk Query | 2 | Type 2 | Minor changes |
| Bing Ads Query | 2 | Type 1 | Auto-convert |
| Delete Tables | 2 | Type 1 | Auto-convert |
| Assert View | 2 | Type 1 | Auto-convert |
| Split Field | 2 | Type 1 | Auto-convert |
| Extract Nested Data SF | 2 | Type 1 | Auto-convert |
| Flatten Variant | 1 | Type 1 | Auto-convert |
| JDBC Table Metadata To Grid | 1 | Type 1 | Auto-convert |
| Deprecated: Fixed Flow | 1 | Unknown | To be assessed |
| API Extract | 1 | Type 3 | Significant work |
| File Iterator | 1 | Type 1 | Auto-convert |
| Unknown Component (1289309076) | 1 | Type 3 | Significant work |
| Table Delete Rows | 1 | Type 1 | Auto-convert |
| LDAP Query | 1 | Type 1 | Auto-convert |
| Excel Query | 1 | Type 1 | Auto-convert |
| Google Analytics Query | 1 | Type 1 | Auto-convert |
| Deprecated: Google AdWords Query | 1 | Unknown | To be assessed |
| Alter Warehouse | 1 | Type 1 | Auto-convert |
| nable.email_alerts | 1 | Type 1 | Auto-convert |
| Microsoft SQL Server Output | 1 | Type 1 | Auto-convert |
| NetSuite Query | 1 | Type 2 | Minor changes |
| SharedJobMarketplace.AWS Power Off Matillion | 1 | Type 1 | Auto-convert |
| Unite | 1 | Type 1 | Auto-convert |
| Map Values | 1 | Type 1 | Auto-convert |
| Multi Table Input | 1 | Type 1 | Auto-convert |

**Database Drivers:**

- Snowflake
- Aws Services

**Library Requirements:**

- Data Processing
- Web Apis
- File Processing
- Utilities
- Other/Custom

---

## Configuration Applied

The following configuration rules were applied during this analysis:

| Category | Setting | Value |
| --- | --- | --- |
| Deployment | CHA Threshold | 1.5x |
| Deployment | Multi-tenant Max | 300 |
| Licensing | Pro Threshold | 150 components |
| Licensing | Premium Threshold | 450 components |
| Complexity | Low Threshold | < 3 |
| Complexity | Medium Threshold | < 6 |
| Complexity | High Threshold | >= 6 |

## Migration Effort Sizing

Migration effort has been estimated using a **T-shirt sizing model** (S/M/L/XL/Custom) which provides project-based scoping and realistic effort ranges. This approach enables rapid estimation for >75% of projects while identifying those requiring detailed discovery.

**Portfolio Summary:** 1 project(s) analyzed • 0 (0%) auto-sizable • 1 requiring custom scoping

### Size Distribution

| Size | Count | Percentage | Typical Scope |
| --- | --- | --- | --- |
| S | 0 | 0.0% | Simple migration, minimal customization |
| M | 0 | 0.0% | Moderate complexity, standard patterns |
| L | 0 | 0.0% | Complex migration, significant customization |
| XL | 0 | 0.0% | Very complex, extensive refactoring |
| Custom | 1 | 100.0% | Requires detailed scoping |

### Project-Level Sizing

| Project | Size | Estimate | Confidence | Key Factors |
| --- | --- | --- | --- | --- |
| N-ABLE/Production | Custom | Varies (53+ days) | Low | Significant refactoring required (5.8% Type 3 components), Python usage requires validation/refactoring |

**Confidence Levels:** High = Standard migration patterns | Medium = Some complexity factors | Low = Custom scoping recommended

## Analysis Status

| Analysis Step | Status | Data Source | Details |
| --- | --- | --- | --- |
| Overall Performance | ✓ Complete | taskHistory.overall | 42977 task batches analyzed |
| Project Analysis | ✓ Complete | taskHistory.projects, jobScan, environmentScan | 1 project(s) with detailed metrics |
| GTM Recommendations | ✓ Complete | Configuration: gtm_config.yaml | 1 recommendation(s) generated |
