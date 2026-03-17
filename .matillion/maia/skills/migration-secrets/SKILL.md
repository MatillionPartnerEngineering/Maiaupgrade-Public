## Secrets

For security reasons, credentials such as secrets and passwords are **not migrated** from Matillion ETL to the Data Productivity Cloud.

- Any secrets or other credentials you have set up in Matillion ETL must be recreated manually in the Data Productivity Cloud to allow pipelines to run.
- Read **Secrets and secret definitions** and **Cloud provider credentials** for details.

Passwords can’t be entered directly into Data Productivity Cloud components (by design). All passwords must be stored in **secrets**, which the component references.

- Secrets are stored in:
  - DPC secret manager in a **Full SaaS** environment, or
  - your own cloud platform’s secret manager in a **Hybrid SaaS** environment.