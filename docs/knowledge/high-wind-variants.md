---
doc_id: high-wind-variants
title: High Wind Variants
topic: wind-variant
codes: [HW_EXCLUDE_ABOVE_CUT_OUT, HW_COUNT_AS_UNAVAILABLE, HW_STORM_GRACE_WINDOW, STORM, TBA, YBA, RBA]
---
 
# High Wind Variants
 
## Why high wind needs a rule
 
When wind speed becomes very high, turbines shut down to protect themselves. Cut-out wind speed is the speed above which a turbine stops generating power. A configuration must state how such periods are treated. This is the high wind variant. Both a high wind variant and a low wind variant must be chosen before a configuration can be published.
 
## The three variants
 
### HW_EXCLUDE_ABOVE_CUT_OUT
 
Periods in which the wind is above the cut-out speed are excluded from the calculation. They are neither counted as available nor as unavailable. This variant is neutral toward both parties, since the periods do not influence the result at all.
 
### HW_COUNT_AS_UNAVAILABLE
 
Periods of high wind are counted as unavailable. This is the most conservative treatment for the service provider, because shutdowns caused by high wind reduce the availability result.
 
### HW_STORM_GRACE_WINDOW
 
A grace window is applied around storm conditions. During this window, a storm-related shutdown is not counted against the service provider. The length of the grace window is defined by the contract wording and is not stated in this knowledge base. This variant is related to the optional weather alarm STORM, which belongs to the category WX, but the two are separate settings: the variant concerns the calculation, whereas the alarm concerns which events are recognised.
 
## Summary table
 
| Variant | Treatment of high wind periods |
|---|---|
| HW_EXCLUDE_ABOVE_CUT_OUT | Removed from the calculation |
| HW_COUNT_AS_UNAVAILABLE | Counted as unavailable |
| HW_STORM_GRACE_WINDOW | Storm shutdowns forgiven during a grace window |
 
## Choosing a variant
 
The choice follows the contract wording:
 
- Use HW_EXCLUDE_ABOVE_CUT_OUT when periods above cut-out should not count either way.
- Use HW_COUNT_AS_UNAVAILABLE when high wind shutdowns must reduce availability.
- Use HW_STORM_GRACE_WINDOW when the contract grants a grace window for storms.
 
## Compatibility
 
All three variants can be selected with TBA, YBA and RBA configurations. No combination with a low wind variant is prohibited by this knowledge base.
 
## Drafts and publishing
 
A draft may leave the high wind variant unselected. Publishing requires that both wind variants are chosen. The backend readiness check decides whether a configuration satisfies this rule. The AI Copilot never states that a configuration is ready.
 
## What is not covered
 
This knowledge base gives no numeric cut-out speed and no duration for the grace window.
