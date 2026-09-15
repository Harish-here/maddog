# Erratum to SBS-GATE-3

F21 and the SPEC-LEVEL bullet state that the ledger specimen was mirrored from `spec.md` and that the spec's specimen contradicted its GAP rule. At the time of the release gate the spec read `| — | Escalation | GAP | ... |` and stated "A GAP row has no section id"; the `S7` id lived in the shipped skill text alone. Found by release verdict REL-3.1.0-RULE-1 NOTE-1; corrected in commit e831f11. The ruling above is left as filed.
