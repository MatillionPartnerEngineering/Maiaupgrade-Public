# Matillion ETL → Data Productivity Cloud Migration Strategy – [CUSTOMER]

Customer: [CUSTOMER]  
Initial Workload: [WORKLOAD]  
Workspace: customer_migration_workspace  

---

## 📊 Project Progress Dashboard

**Overall Completion:** `[□□□□□□□□□□] 0%`

| Phase | Milestone | Progress | Status |
|------|-----------|----------|--------|
| Phase 0 | Pre-Migration Customer Checklist | `[□□□□□□□□□□] 0%` | Pending |
| Phase 1 | DPC Setup, Assets & Secrets | `[□□□□□□□□□□] 0%` | Pending |
| Phase 2 | Shared Pipelines Foundation | `[□□□□□□□□□□] 0%` | Pending |
| Phase 3 | Refactor Discovery | `[□□□□□□□□□□] 0%` | Pending |
| Phase 4 | Migration, Validation & Execution | `[□□□□□□□□□□] 0%` | Pending |

---

## ✅ To Do (Next Actions)

> This section is actively maintained by Maia.  
> It always reflects the **next highest-impact steps** required to move the migration forward.

- [ ] Confirm **Customer Name** and **Initial Workload**
- [ ] Upload and verify all required source files in `migration_project`
- [ ] Complete **Phase 0: Pre-Migration Checklist**
- [ ] Provision DPC Agent and confirm connectivity
- [ ] Approve **Refactor Discovery** scan (Phase 3)

---

## Phase 0: Pre-Migration Checklist

- [ ] Full audit of all secrets used in Matillion ETL
- [ ] Cloud provider confirmed (AWS / Azure / GCP)
- [ ] Agent model confirmed (Full SaaS / Hybrid SaaS)

---

## Phase 1: DPC Setup, Assets & Secrets

- [ ] DPC project and access configured
- [ ] Agent provisioned and connected
- [ ] Network and firewall rules validated

### Secrets (Living, Gated)

Secrets are discovered continuously but **tracked here**.

| Secret Name | Used By | Created | Validated |
|------------|--------|---------|-----------|
| [SECRET] | [Component] | ⬜ | ⬜ |

> A workload cannot complete unless all required secrets are **Validated**.

---

### Project-Related Assets

- [ ] Python libraries from `MAUD.md` uploaded
- [ ] JDBC drivers deployed and configured

---

## Phase 2: Shared Pipelines Foundation

- [ ] Shared pipelines identified
- [ ] Dependencies audited
- [ ] Shared jobs refactored and published
- [ ] Parent pipelines validated

---

## Phase 3: Refactor Discovery

- [ ] User approval obtained
- [ ] Read-only scan executed
- [ ] `refactor_components.md` generated or updated
- [ ] Severity assigned and reviewed

---

## Phase 4: Migration, Validation & Execution

### Interactive Workload Migration Tracker

| # | Workload | Import | Refactor | Validation | Successful Run | Status |
|---|----------|:------:|:--------:|:----------:|:--------------:|--------|
| 1 | [A] | ⬜ | ⬜ | ⬜ | ⬜ | Pending |

---

### Gating Rules

A workload is **Complete** only when:

- All **Blocker** refactors are completed
- All required **Secrets** are validated
- Validation passes
- **Successful Run** is confirmed

Validation reports are stored in:

`migration_project/validation_reports/`