# Chunking Guidelines

Goal
Turn raw extracted text into small, self contained chunks suitable for retrieval augmented generation.

Size
- target 150 to 250 words per chunk
- hard max 350 words
- keep each chunk focused on one topic or workflow

Preferred boundaries
- heading changes such as h2 or h3
- step boundaries in procedures
- large bullet list transitions
- clear shifts in concept such as overview versus configuration

Avoid splitting
- mid sentence
- inside small code or table blocks unless necessary


Metadata (Frontmatter)
Each chunk file MUST start with a YAML frontmatter block containing:
- title: logical title of the chunk
- source_title: title of the original page
- url: canonical url
- section: section or heading name
- run_id: run identifier
- tags: [list, of, tags]
- audience: [Developer, IT Admin, etc]
- intent: [Troubleshoot, Configure, etc]
- prerequisites: [list dependencies]
- synthetic_queries: [list of search strings]

Naming
Use the pattern: `YYYY-MM-DD_{page_slug}_chunk-{index}.md`
Example: `2025-12-05_procurement-services_chunk-01.md`
