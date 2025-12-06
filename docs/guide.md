ExtractionKit Guide

1  Put this extraction-kit folder into your project or vault.

2  Add your real seed urls in _01_targets/url-seeds.md and domains in allowed-domains.md.

3  Use the pre scrape url grabber prompt with your seeds to get a url list and save it as a json file in _02_scrapes_raw.

4  Use the multi url agent prompt with selected urls to generate extraction output and save it in _02_scrapes_raw with a run header that follows run-schema.md.

5  When ready, create cleaned chunks in _03_scrapes_clean/chunks using the chunk guidelines and templates.

6  Update _06_logs/run-log.md after each run with run id, date, and status.

This project is generic and contains no site specific references.
