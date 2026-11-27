---
doc_id: formula-rba
title: Formulas for RBA - RBA_STD and RBA_LOSS with Worked Examples
topic: formula
codes: [RBA, RBA_STD, RBA_LOSS]
---
 
# Formulas for RBA - RBA_STD and RBA_LOSS
 
Two formulas are available for the calculation type RBA (Revenue-Based Availability). Revenue is given in generic currency units (CU), and all numbers are fictional.
 
## RBA_STD
 
**Formula:** Actual revenue / Potential revenue.
 
RBA_STD compares the revenue earned with the revenue that could have been earned.
 
### Worked example
 
Suppose the potential revenue is 90,000 CU and the actual revenue is 86,400 CU.
 
- RBA_STD = 86,400 / 90,000
- 86,400 / 90,000 = 0.96
- Result: **96.00%**
 
The shortfall is 90,000 - 86,400 = 3,600 CU, which is 4.00% of the potential revenue.
 
## RBA_LOSS
 
**Formula:** 1 - Lost revenue / Potential revenue.
 
RBA_LOSS subtracts the ratio of lost revenue from 1.
 
### Worked example
 
Suppose the potential revenue is 105,000 CU and the lost revenue is 5,250 CU.
 
- Loss ratio = 5,250 / 105,000 = 0.05
- RBA_LOSS = 1 - 0.05
- Result: 0.95, or **95.00%**
 
## Relationship between the two
 
When potential revenue equals actual revenue plus lost revenue, both formulas agree. In the second example, the actual revenue would be 105,000 - 5,250 = 99,750 CU, and 99,750 / 105,000 = 0.95, which equals the RBA_LOSS result. If part of the shortfall is not counted as lost revenue under the contract, the two formulas can diverge, and the contract wording decides which one applies.
 
## Choosing between them
 
- Use RBA_STD when the revenue actually earned is the natural reference.
- Use RBA_LOSS when losses are tracked and agreed separately.
 
## Matching rule
 
Both formulas are valid only for a configuration whose calculation type is RBA. Using them on a TBA or YBA configuration is invalid. The mismatch can exist in a draft, but the backend readiness check rejects it at publishing time. The AI Copilot explains this rule but does not decide it.
 
## Notes on inputs
 
This knowledge base does not describe how prices are set or where revenue data originates. Questions about these points cannot be answered from this material.
