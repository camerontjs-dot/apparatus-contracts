---
template_id: knowledge-backlog-intake-rc0
condition: mainframe_backlog_intake
version: "0.1.0"
---

You are reconstructing auditable proposition candidates from a synthesized MainFrame knowledge note.

The note is origin material, not evidence. Do not decide whether a cited source supports, refutes, validates, proves, authorizes, or is sufficient for any proposition. Do not invent source URLs, paths, citations, or source identities. Software will recover explicit source references separately from the paragraphs you identify.

Extract only substantive propositions that would make sense to audit later. Preserve uncertainty and distinguish what the note explicitly asserts from what it presents as an inference, hypothesis, or quotation.

For each claim return:
- `text`: a standalone proposition.
- `origin_relation`: one of `explicit`, `inference`, `hypothesis`, `quotation`.
- `origin_refs`: the paragraph references where the proposition is stated or reconstructed.
- `lineage_refs`: any additional paragraph references that explicitly contain source/citation material the note associates with that proposition. Use this only for source-lineage reconstruction, never as a support judgment.

Paragraph references must use the exact form `paragraph[N]`.

Return no more than 15 claims. Return JSON only with this shape:

```json
{
  "claims": [
    {
      "text": "A complete auditable proposition.",
      "origin_relation": "explicit",
      "origin_refs": ["paragraph[1]"],
      "lineage_refs": ["paragraph[2]"]
    }
  ]
}
```

If the note contains no auditable proposition, return `{"claims": []}`.

## Synthesized knowledge

{{ numbered_knowledge }}
