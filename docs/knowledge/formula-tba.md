---
doc_id: formula-tba
title: Formulas for TBA - TBA_STD and TBA_EXCL with Worked Examples
topic: formula
codes: [TBA, TBA_STD, TBA_EXCL]
---
 
# Formulas for TBA - TBA_STD and TBA_EXCL
 
Two formulas are available for the calculation type TBA (Time-Based Availability). Both produce a ratio between 0 and 1, which is usually shown as a percentage.
 
## TBA_STD
 
**Formula:** Available hours / Period hours.
 
TBA_STD divides the number of hours in which the turbines were available by the full number of hours in the period. No time is removed from the calculation.
 
### Worked example
 
Take a 30-day month, so Period hours = 30 x 24 = 720 hours. Suppose the turbines were available for 684 hours.
 
- TBA_STD = 684 / 720
- 684 / 720 = 0.95
- Result: **95.00%**
 
The 36 hours of unavailability (720 - 684) therefore cost 5.00 percentage points.
 
## TBA_EXCL
 
**Formula:** (Period - Excluded - Unavailable) / (Period - Excluded).
 
TBA_EXCL removes excluded time from the period before computing the ratio. Excluded time is neither counted as available nor as unavailable, which means it cannot raise or lower the result.
 
### Worked example
 
Use the same 720-hour period. Suppose 40 hours are excluded and 32 hours are unavailable.
 
- Numerator: 720 - 40 - 32 = 648
- Denominator: 720 - 40 = 680
- TBA_EXCL = 648 / 680
- 648 / 680 = 0.952941...
- Result: **95.29%** (rounded to two decimals)
 
## Comparing the two
 
Suppose the same 32 unavailable hours were evaluated with TBA_STD and no exclusions. The available hours would be 720 - 32 = 688, and TBA_STD = 688 / 720 = 0.9556, or 95.56%. In that case the figures differ because TBA_EXCL removes the 40 excluded hours from the denominator, while TBA_STD does not. This shows that the choice of formula changes the outcome even when the underlying events are the same, so the formula should be agreed in the contract.
 
## Choosing between them
 
- Use TBA_STD when no time should be removed from the calculation.
- Use TBA_EXCL when certain periods, for example those removed by a wind variant, must be excluded from both numerator and denominator.
 
## Matching rule
 
Both formulas are valid only for a configuration whose calculation type is TBA. Using TBA_STD or TBA_EXCL on a YBA or RBA configuration is invalid. The backend readiness check enforces this at publishing time, and the AI Copilot never decides it.
 
## Rounding
 
The examples round to two decimals for readability. This knowledge base does not specify an official rounding rule.
