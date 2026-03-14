# SKILL.md Commands Test Report

**Generated:** Sat Mar 14 22:26:31 CST 2026
**Project:** /home/zxg/workspace/stock-trader-pro

## Summary

| Metric | Count |
|--------|-------|
| PASS   | 23 |
| FAIL   | 1 |
| SKIP   | 1 |
| TOTAL  | 25 |

## Detailed Results

- PASS: Help command (--help)
- PASS: Params defaults
- PASS: Init database (init-db)
- PASS: Account deposit
- PASS: Mystocks buy position
- PASS: Mystocks view positions (pos)
- PASS: Mystocks summary
- PASS: Mystocks history
- PASS: Account summary
- PASS: Watchlist add
- PASS: Watchlist list
- PASS: Watchlist remove
- PASS: Params list
- PASS: Params get
- PASS: Analyze stock (analyze)
- PASS: Analyze with strategy (vcp)
- PASS: Query stock price (query)
- SKIP: Query multiple stocks (timeout after 10s)
- PASS: Flow analysis
- FAIL: Search stock by name (exit code: 1)
- PASS: Sector ranking
- PASS: Concept sector ranking
- PASS: Export K-line data
- PASS: Alert check (once)
- PASS: Smart monitor (once)
