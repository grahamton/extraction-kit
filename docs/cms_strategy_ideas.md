# CMS Extraction & Prompt Strategy Ideas

## Industry Standard (The Foundation)
These are expected in any high-quality CMS migration or RAG setup.

1.  **Audience Classifier**:
    - *Prompt*: "Classify the intended audience for this content: [Developer, IT Admin, C-Level, End User]."
    - *Why*: Critical for personalization. You don't show API docs to a CEO.
2.  **Intent Labeling**:
    - *Prompt*: "What is the user trying to DO? [Troubleshoot, Configure, Purchase, Learn Concept]."
    - *Why*: Align search results with user goals.
3.  **Cross-Linking**:
    - *Prompt*: "Extract all related internal links and label the relationship (e.g., 'prerequisite', 'next_step', 'reference')."
    - *Why*: Builds the navigation graph.

## Creative / Advanced (The "Magic")
These add high value for LLMs and Agents.

4.  **Synthetic Search Queries (HyDE)**:
    - *Prompt*: "Write 5 Google search queries that a frustrated user would type to find this specific page."
    - *Why*: Matches real user language ("fix error 500") vs. corporate language ("Server Availability Protocol").
5.  **The "Pre-requisite" Scanner**:
    - *Prompt*: "What knowledge or access does the user need *before* reading this? (e.g., 'Admin Access', 'Python installed')."
    - *Why*: Agents can check user state before providing the answer.
6.  **Knowledge Graph Triples**:
    - *Prompt*: "Extract 5 key facts as Subject-Predicate-Object triples (e.g., 'Insight Flex' -> 'includes' -> 'Device Imaging')."
    - *Why*: deterministic fact checking.
7.  **"Tweet & Abstract" Summaries**:
    - *Prompt*: "Write a 1-sentence hook (Tweet) and a 1-paragraph technical abstract."
    - *Why*: Tweeting is great for Slack/Teams notifications; Abstract is for search previews.

## Implementation Plan
- Update `multi-url-agent-prompt.md` to include Audience, Intent, and Synthetic Queries.
- Update `chunking-guidelines.md` to support YAML frontmatter for these new fields.
