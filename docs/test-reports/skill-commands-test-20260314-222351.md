# SKILL.md Commands Test Report

**Generated:** Sat Mar 14 22:23:51 CST 2026
**Project:** /home/zxg/workspace/stock-trader-pro

## Summary

| Metric | Count |
|--------|-------|
| PASS   | 21 |
| FAIL   | 2 |
| SKIP   | 2 |
| TOTAL  | 25 |

## Detailed Results

- PASS: Help command (--help)
- PASS: Params defaults
- PASS: Init database (init-db)
- PASS: Account deposit
- FAIL: Mystocks buy position (exit code: 2)
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
- SKIP: Query stock price (query) (timeout after 10s)
- SKIP: Query multiple stocks (timeout after 10s)
- PASS: Flow analysis
- FAIL: Search stock by name (exit code: 1)
- PASS: Sector ranking
- PASS: Concept sector ranking
- PASS: Export K-line data
- PASS: Alert check (once)
- PASS: Smart monitor (once)
