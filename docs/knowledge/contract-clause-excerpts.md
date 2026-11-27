---
doc_id: contract-clause-excerpts
title: Fictional Contract Clause Excerpts
topic: contract-clause
codes: [TBA, TBA_EXCL, YBA, YBA_LOSS, LW_EXCLUDE_BELOW_CUT_IN, LW_PRO_RATA_POWER_CURVE, HW_EXCLUDE_ABOVE_CUT_OUT, HW_STORM_GRACE_WINDOW, GRID, GRID_LOSS, MAINT, SERVICE, BLADE, WX, STORM, ICE]
---
 
# Fictional Contract Clause Excerpts
 
The following three excerpts are invented for the demo. They are not real contract language, and they show how clause wording maps to WindConfig codes. The parties are called the Operator and the Provider.
 
## Clause 1 - Time-Based Availability Guarantee
 
> 1.1 The Provider shall maintain time-based availability for the turbines listed in the schedule. Availability is calculated as (Period - Excluded - Unavailable) / (Period - Excluded).
> 1.2 Hours in which the wind speed is below cut-in shall not form part of the calculation. Hours in which the wind speed is above cut-out shall not form part of the calculation.
 
**Mapping:** calculation type TBA; formula TBA_EXCL; low wind variant LW_EXCLUDE_BELOW_CUT_IN; high wind variant HW_EXCLUDE_ABOVE_CUT_OUT.
 
## Clause 2 - Yield-Based Measure for the Second Schedule
 
> 2.1 For the turbines in the second schedule, availability is measured as one minus the ratio of lost yield to potential yield.
> 2.2 Periods of low wind shall be credited in proportion to the power curve.
> 2.3 A grace window applies at the onset of storm conditions, during which a storm shutdown shall not be treated as lost yield. The duration of the grace window is set out in Annex C.
 
**Mapping:** calculation type YBA; formula YBA_LOSS; low wind variant LW_PRO_RATA_POWER_CURVE; high wind variant HW_STORM_GRACE_WINDOW. The weather alarm STORM, in the optional category WX, may be included so that storm shutdowns are recognised. Annex C is not part of this knowledge base.
 
## Clause 3 - Recognised Events and Reporting Period
 
> 3.1 The following events shall be recognised: grid loss; scheduled service; blade inspection.
> 3.2 Icing may additionally be recognised where the Operator and the Provider agree in writing.
> 3.3 The reporting period of a configuration may begin before or end after the term of this agreement, so that renewals can be accommodated.
 
**Mapping:**
 
- Grid loss corresponds to GRID_LOSS in the required category GRID.
- Scheduled service and blade inspection correspond to SERVICE and BLADE in the required category MAINT.
- Icing corresponds to ICE in the optional category WX, included only by agreement.
- Clause 3.3 is consistent with the rule that configuration dates may lie outside the contract dates because contracts renew.
 
## Reading clauses with care
 
Clause wording tells the user which codes to select, but the clauses cannot decide whether a configuration is publishable. That decision belongs to the backend readiness check. The excerpts also contain no penalties, thresholds or percentage guarantees, so questions about such values cannot be answered from this knowledge base.
