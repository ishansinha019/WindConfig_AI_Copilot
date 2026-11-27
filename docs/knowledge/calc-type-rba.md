---
doc_id: calc-type-rba
title: Calculation Type RBA - Revenue-Based Availability
topic: calculation-type
codes: [RBA, RBA_STD, RBA_LOSS, LW_COUNT_AS_AVAILABLE, HW_COUNT_AS_UNAVAILABLE]
---
 
# Calculation Type RBA - Revenue-Based Availability
 
## Purpose
 
RBA stands for Revenue-Based Availability. It extends the yield idea by weighting energy with its value. It answers the question: of the revenue the selected turbines could have earned, how much was actually earned?
 
Revenue-based measures reflect the fact that energy is not always worth the same amount at every moment. Production lost during a high-value period counts for more than production lost during a low-value period. In this fictional knowledge base, all revenue figures are given in generic currency units (CU).
 
## Formulas
 
A configuration whose calculation type is RBA may use one of two formulas:
 
- **RBA_STD**: Actual revenue / Potential revenue.
- **RBA_LOSS**: 1 - Lost revenue / Potential revenue.
 
RBA_STD begins with the revenue actually earned. RBA_LOSS begins with the revenue lost and subtracts the loss ratio from 1. A worked numeric example is in the document *Formulas for RBA* (doc_id: formula-rba).
 
## Matching rule
 
A formula must match the configuration's calculation type. An RBA configuration cannot use TBA_STD, TBA_EXCL, YBA_STD or YBA_LOSS. Mismatches can exist in a draft but cannot be published.
 
## Inputs
 
RBA needs revenue quantities: potential revenue, actual revenue and lost revenue. How the price per unit of energy is determined is not described in this knowledge base.
 
## Interaction with wind variants
 
Any low wind variant and any high wind variant may be combined with RBA. Two examples illustrate the contrast in intent:
 
- LW_COUNT_AS_AVAILABLE treats low wind periods as available, which protects the service provider from being penalised for calm conditions.
- HW_COUNT_AS_UNAVAILABLE treats high wind periods as unavailable, which is the more conservative treatment for the service provider.
 
The documents on low wind and high wind variants describe all six variants.
 
## Alarm handling
 
As for every calculation type, the required categories GRID and MAINT each need at least one alarm included when publishing. WX is optional. Assignments are per turbine and may only reference selected turbines.
 
## Publishing
 
An RBA draft can be incomplete. Publishing requires completeness and is decided by the backend readiness check. The AI Copilot may describe the rules, but it never states that a configuration is publishable.
