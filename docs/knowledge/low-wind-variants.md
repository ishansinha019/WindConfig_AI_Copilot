---
doc_id: low-wind-variants
title: Low Wind Variants
topic: wind-variant
codes: [LW_EXCLUDE_BELOW_CUT_IN, LW_COUNT_AS_AVAILABLE, LW_PRO_RATA_POWER_CURVE, TBA, YBA, RBA]
---
 
# Low Wind Variants
 
## Why low wind needs a rule
 
When wind speed is very low, turbines may not produce energy even though nothing is wrong with them. Cut-in wind speed is the speed below which a turbine does not generate power. A configuration therefore needs a rule that states how such periods are treated. This rule is called the low wind variant. Both a low wind variant and a high wind variant must be chosen before a configuration can be published.
 
## The three variants
 
### LW_EXCLUDE_BELOW_CUT_IN
 
Periods in which the wind is below the cut-in speed are excluded from the calculation. They are neither counted as available nor as unavailable. This is a natural match with a formula that has an explicit exclusion term, such as TBA_EXCL, although it can be selected with any calculation type.
 
### LW_COUNT_AS_AVAILABLE
 
Periods of low wind are counted as available. The turbines receive full credit for these periods, even though they produce little or no energy. This variant is the most favourable to the service provider.
 
### LW_PRO_RATA_POWER_CURVE
 
Periods of low wind receive partial credit in proportion to the power curve. The lower the possible output according to the power curve, the less the period weighs. This is a middle path between excluding the period and fully crediting it, and it suits yield-based or revenue-based measures.
 
## Summary table
 
| Variant | Treatment of low wind periods |
|---|---|
| LW_EXCLUDE_BELOW_CUT_IN | Removed from the calculation |
| LW_COUNT_AS_AVAILABLE | Counted as available |
| LW_PRO_RATA_POWER_CURVE | Weighted pro rata to the power curve |
 
## Choosing a variant
 
The choice follows the contract wording. In general:
 
- Select LW_EXCLUDE_BELOW_CUT_IN when the contract says that periods below cut-in do not count.
- Select LW_COUNT_AS_AVAILABLE when the contract says that low wind periods count in favour of availability.
- Select LW_PRO_RATA_POWER_CURVE when the contract refers to a power curve and proportional treatment.
 
## Compatibility
 
All three variants can be selected with TBA, YBA and RBA configurations. The knowledge base does not prohibit any combination of low wind variant and high wind variant.
 
## Drafts and publishing
 
A draft may leave the low wind variant unselected. Publishing requires that both wind variants are chosen. Whether a particular configuration satisfies this is decided by the backend readiness check, not by the AI Copilot.
 
## What is not covered
 
This knowledge base does not state numeric cut-in wind speeds or the exact power curve of any turbine, as these are not part of the fictional demo data.
