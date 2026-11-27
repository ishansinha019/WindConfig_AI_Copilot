---
doc_id: faq-general
title: Frequently Asked Questions
topic: faq
codes: [TBA, YBA, RBA, TBA_STD, TBA_EXCL, YBA_STD, YBA_LOSS, RBA_STD, RBA_LOSS, GRID, MAINT, WX]
---
 
# Frequently Asked Questions
 
**Q: What are the three calculation types?**
TBA (Time-Based Availability), YBA (Yield-Based Availability) and RBA (Revenue-Based Availability).
 
**Q: Which formulas can I use?**
The formula must match the calculation type. TBA allows TBA_STD and TBA_EXCL. YBA allows YBA_STD and YBA_LOSS. RBA allows RBA_STD and RBA_LOSS.
 
**Q: Can I save a draft that is not finished?**
Yes. Drafts may be incomplete. Only publishing requires completeness.
 
**Q: Which alarm categories are mandatory?**
GRID (Grid interruption) and MAINT (Planned maintenance). Each needs at least one alarm included. WX (Weather event) is optional.
 
**Q: Can one contract have several configurations?**
Yes. A contract can have several configurations, each identified by its own GUID. The knowledge base does not state a maximum number.
 
**Q: How many published versions can a configuration have?**
Only one.
 
**Q: Can I delete a configuration?**
Drafts can be deleted. Published configurations cannot be deleted.
 
**Q: Why did the Copilot not tell me whether my configuration is ready?**
Publishing rules are decided by backend code, never by the AI. The Copilot explains the relevant rule and tells you that the backend readiness check decides. This protects you from relying on an unverified answer.
 
**Q: May the configuration dates fall outside the contract dates?**
Yes, because contracts renew. The end date must still be after the start date.
 
**Q: Does the overlap rule apply across contracts?**
No. It applies to published configurations of the same contract that share at least one turbine and have an overlapping date range, with inclusive dates. Turbine codes are contract-specific, so T01 in two contracts means two different turbines.
 
**Q: What range is allowed for park availability?**
0 to 100.
 
**Q: Do I have to choose wind variants?**
Yes, both a low wind variant and a high wind variant must be chosen before publishing. Drafts may leave them open.
 
**Q: Where can I find numeric details such as cut-in speeds, penalty amounts or grace window lengths?**
Not in this knowledge base. These values depend on the actual contract text and are not part of the fictional demo data.
 
**Q: Does the AI Copilot change my configuration?**
This knowledge base does not describe any automatic changes. Its role here is to explain terms, formulas, variants and rules.
