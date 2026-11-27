---
doc_id: calc-type-yba
title: Calculation Type YBA - Yield-Based Availability
topic: calculation-type
codes: [YBA, YBA_STD, YBA_LOSS, LW_PRO_RATA_POWER_CURVE, HW_STORM_GRACE_WINDOW]
---
 
# Calculation Type YBA - Yield-Based Availability
 
## Purpose
 
YBA stands for Yield-Based Availability. Instead of counting hours, it compares energy quantities. It answers the question: of the energy the selected turbines could have produced, how much did they actually deliver?
 
Yield-based measures give more weight to windy hours than to calm hours. An hour of downtime during strong wind costs more yield than an hour of downtime in light wind, so YBA reflects the real production consequences of unavailability.
 
## Formulas
 
A configuration whose calculation type is YBA may use one of two formulas:
 
- **YBA_STD**: Actual yield / Potential yield.
- **YBA_LOSS**: 1 - Lost yield / Potential yield.
 
YBA_STD starts from what was delivered. YBA_LOSS starts from what was lost and subtracts the loss ratio from 1. Both produce a value between 0 and 1, which is usually shown as a percentage. A worked example for both is in the document *Formulas for YBA* (doc_id: formula-yba).
 
## Matching rule
 
A formula must match the configuration's calculation type. A YBA configuration cannot use TBA_STD, TBA_EXCL, RBA_STD or RBA_LOSS. If a draft contains a mismatched formula, it can be saved, but it will not pass the backend readiness check.
 
## Inputs
 
YBA relies on yield quantities: potential yield, actual yield and lost yield. The source of these quantities, such as a power curve or measured data, is not described in this knowledge base.
 
## Interaction with wind variants
 
Wind variants are especially relevant for YBA, because wind speed drives potential yield.
 
- LW_PRO_RATA_POWER_CURVE gives credit for low wind periods in proportion to the power curve rather than all or nothing, which suits a yield-based measure.
- HW_STORM_GRACE_WINDOW gives a grace window around storm conditions, so a storm shutdown does not immediately count as lost yield.
 
The other variants are also permitted, as every variant can be combined with every calculation type. The document on low wind variants and the document on high wind variants explain each of them.
 
## Alarm handling
 
The required alarm categories GRID and MAINT must each have at least one alarm included for publishing. The optional WX category, with alarms such as ICE and STORM, can be included when weather-related loss events should be recognised. Alarm assignments are made per turbine and may only reference turbines that are selected in the configuration.
 
## Drafts and publishing
 
Drafts may be incomplete. Publishing requires every rule to be satisfied, including both wind variants being chosen, and that decision is made by backend code, never by the AI Copilot.
