# Annotated primary-source note — authority before connectivity

Ashish Srivastava · 19 November 2026

**Question:** what changes when an agency service loses central connectivity, and what must remain an explicit authority decision?

**NIST SP 800-207:** the source makes authorization and trust decisions explicit rather than granting trust solely from network location. **Inference for this experiment:** a disconnected local session should still require record and action scope. The live API's permitted read and cross-record/cross-agency denials are bounded supporting observations.

**NIST CSF 2.0:** the Govern function connects cybersecurity decisions to organizational context, roles and oversight. **Inference:** a local continuity action needs an accountable owner and a defined stop condition; the mission register records both.

**FIPS 199:** the source categorizes information/system impact through confidentiality, integrity and availability. **Inference:** an offline workflow must account for both disclosure and changed/delayed service outcomes. The fixture's labels are not an official impact category.

**AI RMF 1.0:** the source structures governance, context, measurement and risk management. **Inference:** authorizing a model artifact is separate from authorizing its retrieval or tool effects. The router-data and tool-boundary cases deliberately test these separately.

**Open question:** how should a real agency protect local authority/freshness, reconcile global revocation and quantify recovery loss when connectivity and trusted time are unavailable?

[Source register](../../references/primary-sources.json) · [Experimental results](../results/2026-11-19-government-local-authority.md) · [Threat model](../../missions/citizen-services/threat-model.md)
