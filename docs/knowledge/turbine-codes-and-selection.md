---
doc_id: turbine-codes-and-selection
title: Turbine Codes and Turbine Selection
topic: workflow
codes: [GRID, MAINT]
---
 
# Turbine Codes and Turbine Selection
 
## Contract-specific codes
 
Turbines are labelled with codes from T01 to T10. These codes are **specific to a contract**. T01 in Contract Alpha and T01 in Contract Beta are two different physical turbines that happen to share a label. A code is therefore meaningful only together with the contract that owns it.
 
This has an important consequence. When the system compares configurations, for example in the overlap rule, it compares turbines only inside the same contract. A shared label across two contracts never counts as a shared turbine.
 
## Selecting turbines
 
Every configuration selects the turbines it covers. Selection rules:
 
- A draft may have no turbines selected.
- Publishing requires at least one turbine.
- All alarm assignments must reference only selected turbines.
- Two published configurations of the same contract that share at least one turbine must not have overlapping date ranges, with inclusive dates.
 
## Examples
 
**Example 1.** Contract Alpha has a configuration covering T01 and T02. A user wants a second configuration for the same contract covering T02 and T03. The two share T02. If both are published, their date ranges must not overlap. If the dates are different and do not overlap, both can coexist.
 
**Example 2.** A configuration in Contract Alpha covers T01 for 2025. A configuration in Contract Beta covers T01 for 2025. Because these are different turbines, no overlap issue arises.
 
**Example 3.** A user selects T01 and T02 but creates an alarm assignment for T05. T05 is not selected, so the assignment violates the rule that alarm assignments reference only selected turbines.
 
## Changing the selection
 
If a turbine is removed from the selection, any alarm assignments that reference it must also be corrected before publishing. The knowledge base does not describe whether the system cleans these up automatically.
 
## Relationship to required alarm categories
 
Alarms are assigned per turbine, and the required categories GRID and MAINT each need at least one alarm included. The precise way these requirements are checked across several turbines is not detailed here. The backend readiness check applies the rules and decides.
 
## Limits
 
The knowledge base lists only the codes T01 to T10. It does not state how many turbines a real park has, which turbine model each code represents, or any technical data about the turbines.
