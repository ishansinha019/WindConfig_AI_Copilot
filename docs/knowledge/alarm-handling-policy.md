---
doc_id: alarm-handling-policy
title: Alarm Handling Policy - Required and Optional Categories
topic: alarm-policy
codes: [GRID, GRID_LOW, GRID_LOSS, MAINT, SERVICE, BLADE, WX, ICE, STORM]
---
 
# Alarm Handling Policy
 
## Categories and alarms
 
Alarms are organised into categories. Each category either must or may be represented in a configuration.
 
| Category | Name | Status | Alarms |
|---|---|---|---|
| GRID | Grid interruption | Required | GRID_LOW (Grid voltage low), GRID_LOSS (Grid loss) |
| MAINT | Planned maintenance | Required | SERVICE (Scheduled service), BLADE (Blade inspection) |
| WX | Weather event | Optional | ICE (Icing), STORM (Storm shutdown) |
 
No other categories or alarm codes exist in this knowledge base.
 
## Required versus optional
 
A category marked *required* must have at least one of its alarms included in the configuration before it can be published. For GRID, including only GRID_LOSS satisfies the rule. For MAINT, including only SERVICE satisfies it.
 
An *optional* category may be left out entirely. A configuration with no WX alarms can still satisfy the alarm rule, because WX does not have to be represented. Including WX alarms is appropriate when the contract recognises weather events.
 
## Per-turbine assignment
 
Alarm inclusion is assigned per turbine. This means that each turbine selected in the configuration has its own set of included alarms. The key constraint is that alarm assignments may only reference turbines that are selected in the configuration. If an assignment names a turbine that is not selected, the configuration violates the rule and cannot be published.
 
Note that turbine codes such as T01 are specific to each contract. An assignment for T01 always refers to the T01 of the contract that owns the configuration.
 
## Drafts
 
Drafts may be incomplete. A draft may have no alarms at all, may include only optional categories, or may contain assignments that are later corrected. These states only become problems when publishing is attempted.
 
## Who decides
 
Whether the alarm requirements are satisfied is decided by backend code in the readiness check. The AI Copilot may explain the policy, give examples and point out which categories are required, but it never states that a configuration is ready to publish.
 
## Examples
 
- A configuration with GRID_LOSS and SERVICE included for all selected turbines satisfies both required categories.
- A configuration with only ICE and STORM included does not satisfy the required categories, because GRID and MAINT have no alarm.
- A configuration with turbines T01 and T02 selected and an alarm assignment for T03 breaks the assignment rule.
