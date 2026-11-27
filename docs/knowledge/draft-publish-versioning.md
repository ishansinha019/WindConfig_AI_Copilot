---
doc_id: draft-publish-versioning
title: Draft, Publish, Versioning and Deletion
topic: workflow
codes: [TBA, YBA, RBA, GRID, MAINT]
---
 
# Draft, Publish, Versioning and Deletion
 
## Hierarchy
 
The structure is: Contract, then Availability Configuration, then numbered versions. A contract can have several configurations. Each configuration is identified by a GUID. Each configuration has one or more versions, numbered in sequence.
 
## Version states
 
A version is in one of three states:
 
- **Draft**: a working version that may be incomplete.
- **Published**: a complete and validated version.
- **Archived**: a version kept for history.
 
Only one published version may exist per configuration at any time. The knowledge base does not describe how or when a version becomes archived, and it does not state whether an archived version can be restored.
 
## Drafts may be incomplete
 
Drafts can be saved with missing information. A draft may lack turbines, alarms, a formula or a wind variant. This lets users work step by step without being blocked.
 
## Publishing requires completeness
 
Publishing requires every rule to be satisfied. The rules are decided by backend code and never by AI:
 
1. The name is unique within the contract.
2. The end date is after the start date. Dates may lie outside the contract dates, because contracts renew.
3. At least one turbine is selected.
4. Every required alarm category (GRID and MAINT) has at least one alarm included.
5. Alarm assignments reference only selected turbines.
6. Park availability is between 0 and 100.
7. Both wind variants are chosen.
8. No other published configuration of the same contract shares at least one turbine and also has an overlapping date range (inclusive).
 
In addition, the formula must match the calculation type (TBA, YBA or RBA).
 
## The role of the AI Copilot
 
The AI Copilot explains these rules in plain language. When a user asks whether a configuration can be published, the Copilot describes the relevant rule and states that the backend readiness check makes the decision. It never answers yes or no on its own.
 
## Deletion
 
- **Drafts can be deleted.**
- **Published configurations cannot be deleted.**
 
This knowledge base does not say whether archived versions can be deleted.
 
## Typical workflow
 
1. Create a draft within a contract.
2. Fill in the calculation type, formula, wind variants, turbines, alarms and dates.
3. Run the backend readiness check.
4. If all rules are met, publish the version.
5. To change a published configuration, work on a new version and publish it when ready.
 
Step 5 describes the general intent of versioning. Exact mechanics are not specified here.
