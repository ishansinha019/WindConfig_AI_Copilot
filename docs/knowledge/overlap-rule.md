---
doc_id: overlap-rule
title: The Overlap Rule with Worked Examples
topic: workflow
codes: [TBA, YBA, RBA]
---
 
# The Overlap Rule
 
## Statement of the rule
 
When a configuration is published, the backend readiness check verifies that no other **published** configuration of the **same contract** both:
 
1. shares at least one turbine with it, **and**
2. has an overlapping date range.
 
Date ranges are **inclusive**. A range that ends on a given day overlaps with a range that starts on that same day. A conflict exists only if both conditions are true. If either one is false, the rule is satisfied.
 
Important details:
 
- Only published configurations are compared. Drafts and archived versions are not part of the comparison.
- Only configurations of the same contract are compared. Because turbine codes are contract-specific, T01 in one contract is a different turbine from T01 in another.
- Dates may lie outside the contract dates, since contracts renew.
 
## Setup for the examples
 
Contract Alpha (fictional) already has one published configuration, P1:
 
- Turbines: T01, T02, T03
- Dates: 2025-01-01 to 2025-12-31
 
## Example 1 - Overlap (conflict)
 
A new configuration N1 selects turbines T03 and T04, with dates 2025-12-31 to 2026-06-30.
 
- Shared turbine: T03, so condition 1 is true.
- Date check: P1 ends on 2025-12-31 and N1 starts on 2025-12-31. Because ranges are inclusive, they share that day, so condition 2 is true.
- Both conditions are true, so the overlap rule is **violated**.
 
## Example 2 - No date overlap
 
A new configuration N2 selects turbines T01 and T02, with dates 2026-01-01 to 2026-12-31.
 
- Shared turbines: T01 and T02, so condition 1 is true.
- Date check: P1 ends on 2025-12-31 and N2 begins on 2026-01-01, one day later. There is no common day, so condition 2 is false.
- Only one condition is true, so the overlap rule is **satisfied**.
 
## Example 3 - No shared turbine
 
A new configuration N3 selects turbines T04 and T05, with dates 2025-03-01 to 2025-09-30.
 
- Shared turbines: none, since P1 uses T01, T02 and T03. Condition 1 is false.
- Date check: the range lies inside P1's range, so condition 2 is true.
- Only one condition is true, so the overlap rule is **satisfied**.
 
## Notes
 
- Examples 2 and 3 show that overlapping dates alone, or shared turbines alone, are not a conflict.
- The overlap rule is one of several publishing rules. A configuration that satisfies it may still fail other rules.
- The AI Copilot explains the rule but never decides it. The backend readiness check makes the decision.
