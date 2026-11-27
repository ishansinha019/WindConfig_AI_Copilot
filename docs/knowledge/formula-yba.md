---
doc_id: formula-yba
title: Formulas for YBA - YBA_STD and YBA_LOSS with Worked Examples
topic: formula
codes: [YBA, YBA_STD, YBA_LOSS]
---
 
# Formulas for YBA - YBA_STD and YBA_LOSS
 
Two formulas are available for the calculation type YBA (Yield-Based Availability). Yield is expressed here in megawatt-hours (MWh), and all numbers are fictional.
 
## YBA_STD
 
**Formula:** Actual yield / Potential yield.
 
YBA_STD compares the energy actually produced with the energy that could have been produced.
 
### Worked example
 
Suppose the potential yield for the period is 1,200 MWh and the actual yield is 1,140 MWh.
 
- YBA_STD = 1,140 / 1,200
- 1,140 / 1,200 = 0.95
- Result: **95.00%**
 
## YBA_LOSS
 
**Formula:** 1 - Lost yield / Potential yield.
 
YBA_LOSS focuses on the energy that was lost. The loss ratio is subtracted from 1.
 
### Worked example
 
Suppose the potential yield is 1,250 MWh and the lost yield is 75 MWh.
 
- Loss ratio = 75 / 1,250 = 0.06
- YBA_LOSS = 1 - 0.06
- Result: 0.94, or **94.00%**
 
## Relationship between the two
 
If the potential yield equals the actual yield plus the lost yield, the two formulas give the same answer. Using the figures of the second example, the actual yield would be 1,250 - 75 = 1,175 MWh, and YBA_STD = 1,175 / 1,250 = 0.94, or 94.00%, which matches YBA_LOSS.
 
The formulas can differ when the contract defines lost yield in a way that does not simply equal potential minus actual, for example if some losses are not attributable to the service provider. In such a case the choice of formula matters and must follow the contract wording.
 
## Choosing between them
 
- Use YBA_STD when the actual produced energy is the natural reference.
- Use YBA_LOSS when the contract is phrased in terms of losses that are measured or attributed separately.
 
## Matching rule
 
Both formulas are valid only for a configuration whose calculation type is YBA. Selecting TBA or RBA formulas for a YBA configuration is invalid. A draft can hold the mismatch temporarily, but the backend readiness check will not allow publication.
 
## Sanity range
 
A result should fall between 0% and 100%. A value outside this range indicates inconsistent inputs, for example lost yield larger than potential yield.
