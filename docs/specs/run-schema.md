# Run Schema

Canonical json schema for a single extraction run.

Example

{
  "run_id": "YYYY-MM-DD_example",
  "date": "YYYY-MM-DD",
  "seeds": ["https://example.com/docs"],
  "domains": ["example.com"],
  "mode": "multi-url",
  "topic_filters": [],
  "depth_limit": 3,
  "max_fetches": 40,
  "fetch_count": 0,
  "status": "planned",
  "pages": [],
  "errors": []
}

Page entry structure

{
  "slug": "managing-user-accounts",
  "url": "https://example.com/docs/managing-user-accounts",
  "content_type": "html",
  "selected": true,
  "summary_tokens": 0,
  "chunk_count": 0
}

Error entry structure

{
  "url": "https://example.com/docs/broken-link",
  "stage": "fetch",
  "code": "404",
  "message": "Not Found"
}

Raw file header pattern

At the top of each file in _02_scrapes_raw include

Run: YYYY-MM-DD_example

followed by the json block shown above on its own.
Then add a separator line and paste the raw agent output below.
