---
doc_id: calc-type-tba
title: Calculation Type TBA - Time-Based Availability
topic: calculation-type
codes: [TBA, TBA_STD, TBA_EXCL, LW_EXCLUDE_BELOW_CUT_IN, HW_EXCLUDE_ABOVE_CUT_OUT]
---
 
# Calculation Type TBA - Time-Based Availability
 
## Purpose
 
TBA stands for Time-Based Availability. It measures availability as a share of time. The question it answers is: during the evaluated period, for what fraction of the hours were the selected turbines available to operate?
 
Because it counts hours rather than energy or money, TBA is the simplest of the three calculation types. It does not depend on how much wind there was or how much the energy was worth. It only depends on how long turbines were available and which periods are excluded.
 
## Formulas
 
A configuration whose calculation type is TBA may use one of two formulas:
 
- **TBA_STD**: Available hours / Period hours.
- **TBA_EXCL**: (Period - Excluded - Unavailable) / (Period - Excluded).
 
TBA_STD treats the whole period as the denominator. TBA_EXCL first removes excluded time from both the numerator and the denominator, so excluded time neither helps nor hurts the result. A worked numeric example of both formulas is in the document *Formulas for TBA* (doc_id: formula-tba).
 
## Matching rule
 
A formula must match the configuration's calculation type. A TBA configuration cannot use YBA_STD, YBA_LOSS, RBA_STD or RBA_LOSS. Selecting a formula from another family is an invalid combination, and the backend readiness check will not accept it for publishing.
 
## Interaction with wind variants
 
Every configuration must choose one low wind variant and one high wind variant before publishing. For a TBA configuration these variants decide how hours with very low or very high wind are classified. For example:
 
- With LW_EXCLUDE_BELOW_CUT_IN, hours below the cut-in wind speed are treated as excluded time, which is most naturally used together with TBA_EXCL.
- With HW_EXCLUDE_ABOVE_CUT_OUT, hours above the cut-out wind speed are likewise removed from the calculation.
 
The full list of variants is described in the documents on low wind and high wind variants.
 
## Interaction with alarms
 
The alarms included in the configuration determine which kinds of events are recognised. Two alarm categories, GRID and MAINT, are required for publishing, and each needs at least one alarm included. The optional category WX may be added when weather events should be recognised. See the alarm handling policy for details.
 
## When TBA is a natural choice
 
TBA is often chosen when the parties want a transparent, easily audited measure that does not require yield or price data. It is also a common starting point when a contract is first set up, since it needs the fewest inputs.
 
## Draft versus published
 
A TBA draft may be saved without a formula, without turbines or without alarms. Publishing requires completeness, and that decision belongs to the backend readiness check.
