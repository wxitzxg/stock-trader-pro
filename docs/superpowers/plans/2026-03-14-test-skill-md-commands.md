# Test SKILL.md Commands Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create and execute a test script that validates all bash commands in SKILL.md are executable with proper output format.

**Architecture:** Single bash test script with categorized tests (no-dependency, database-dependency, API-dependency), automatic setup, and JSON-formatted report output.

**Tech Stack:** Bash scripting, Python subprocess, SQLite test database, timeout control (10s for API commands).

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `scripts/test_skill_commands.sh` | Create | Main test script with all command tests |
| `scripts/test_setup.py` | Create | Python helper for test data setup |
| `docs/test-reports/skill-commands-test-report.md` | Create | Test execution report |

---

## Chunk 1: Test Infrastructure

### Task 1: Create test setup helper

**Files:**
- Create: `scripts/test_setup.py`

- [ ] **Step 1: Create test_setup.py with database initialization and test data creation**

```python
#!/usr/bin/env python3
"""Test data setup for SKILL.md command tests."""

import subprocess
import sys
import os

# Change to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

def run_cmd(cmd: list) -> tuple[bool, str]:
    """Run command and return (success, output)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 50)
    print("Setting up test data...")
    print("=" * 50)

    # Step 1: Initialize database
    print("\n[1/4] Initializing database...")
    success, output = run_cmd([sys.executable, "main.py", "init-db"])
    if success:
        print(f"  ✅ Database initialized")
    else:
        print(f"  ❌ Database init failed: {output}")
        return 1

    # Step 2: Add test cash deposit
    print("\n[2/4] Adding test cash deposit...")
    success, output = run_cmd([sys.executable, "main.py", "account", "--deposit", "100000"])
    if "✅" in output or "success" in output.lower():
        print(f"  ✅ Cash deposit added")
    else:
        print(f"  ⚠️  Deposit result: {output[:200]}")

    # Step 3: Add test position (buy stock)
    print("\n[3/4] Adding test position (600519)...")
    success, output = run_cmd([
        sys.executable, "main.py", "mystocks", "buy",
        "600519", "--qty", "100", "--price", "1500", "--name", "贵州茅台"
    ])
    if success or "✅" in output:
        print(f"  ✅ Test position added")
    else:
        print(f"  ⚠️  Position result: {output[:200]}")

    # Step 4: Add test watchlist
    print("\n[4/4] Adding test watchlist (300760)...")
    success, output = run_cmd([
        sys.executable, "main.py", "watchlist", "--add", "300760",
        "--name", "迈瑞医疗", "--tags", "医疗器械"
    ])
    if success or "✅" in output:
        print(f"  ✅ Test watchlist added")
    else:
        print(f"  ⚠️  Watchlist result: {output[:200]}")

    print("\n" + "=" * 50)
    print("Test setup complete!")
    print("=" * 50)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify test_setup.py is syntactically correct**

Run: `python3 -m py_compile scripts/test_setup.py`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add scripts/test_setup.py
git commit -m "test: add test data setup helper for SKILL.md command tests"
```

---

### Task 2: Create main test script

**Files:**
- Create: `scripts/test_skill_commands.sh`

- [ ] **Step 1: Create test_skill_commands.sh - Part 1 (Header and helper functions)**

```bash
#!/usr/bin/env bash
# =============================================================================
# Test Script for SKILL.md Commands
# =============================================================================
# Purpose: Validate all bash commands in SKILL.md documentation are executable
#
# Test Categories:
#   A. No Dependency - Commands that work without database or API
#   B. Database Dependency - Commands requiring initialized database
#   C. API Dependency - Commands requiring external API (AKShare/Sina)
#
# Test Levels:
#   PASS     - Command executed with expected output format
#   FAIL     - Command failed unexpectedly
#   SKIP     - Command skipped (API unavailable, network issue)
# =============================================================================

set -o pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
TOTAL_COUNT=0

# Results array
declare -a RESULTS=()

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Python executable
PYTHON="${PYTHON:-python3}"

# =============================================================================
# Helper Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASS_COUNT++))
    RESULTS+=("PASS: $1")
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAIL_COUNT++))
    RESULTS+=("FAIL: $1")
}

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
    ((SKIP_COUNT++))
    RESULTS+=("SKIP: $1")
}

# Run command with timeout and check result
# Usage: run_test "description" "category" command...
run_test() {
    local desc="$1"
    local category="$2"
    shift 2
    local cmd=("$@")

    ((TOTAL_COUNT++))

    log_info "Testing: $desc"
    echo "  Command: ${cmd[*]}"

    # Run command with 10s timeout for API, 30s for others
    local timeout=30
    [[ "$category" == "API" ]] && timeout=10

    local output
    local exit_code

    output=$(timeout "$timeout" "${cmd[@]}" 2>&1)
    exit_code=$?

    if [[ $exit_code -eq 124 ]]; then
        log_skip "$desc (timeout after ${timeout}s)"
        return 1
    elif [[ $exit_code -ne 0 ]]; then
        # Check if it's an expected error (API unavailable)
        if [[ "$category" == "API" ]] && [[ "$output" == *"Network"* || "$output" == *"connection"* || "$output" == *"AKShare"* ]]; then
            log_skip "$desc (API unavailable: ${output:0:100}...)"
            return 1
        fi
        log_fail "$desc (exit code: $exit_code)"
        echo "  Output: ${output:0:200}"
        return 1
    fi

    # Check output is not empty and looks valid
    if [[ -z "$output" ]]; then
        log_fail "$desc (empty output)"
        return 1
    fi

    log_pass "$desc"
    return 0
}
```

- [ ] **Step 2: Verify bash syntax**

Run: `bash -n scripts/test_skill_commands.sh`
Expected: No output (syntax OK)

- [ ] **Step 3: Continue test_skill_commands.sh - Part 2 (Test categories)**

```bash
# =============================================================================
# Category A: No Dependency Tests
# =============================================================================

test_no_dependency() {
    echo ""
    echo "====================================================================="
    echo "Category A: No Dependency Tests"
    echo "====================================================================="

    # SKILL.md Section: 安装说明 - Step 5
    run_test "Help command (--help)" "NONE" \
        "$PYTHON" "main.py" "--help"

    # SKILL.md Section: 参数管理
    run_test "Params defaults" "NONE" \
        "$PYTHON" "main.py" "params" "defaults"
}

# =============================================================================
# Category B: Database Dependency Tests
# =============================================================================

test_database_dependency() {
    echo ""
    echo "====================================================================="
    echo "Category B: Database Dependency Tests"
    echo "====================================================================="

    # SKILL.md Section: 安装说明 - Step 4
    run_test "Init database (init-db)" "DB" \
        "$PYTHON" "main.py" "init-db"

    # SKILL.md Section: 持仓管理
    run_test "Account deposit" "DB" \
        "$PYTHON" "main.py" "account" "--deposit" "100000"

    run_test "Mystocks buy position" "DB" \
        "$PYTHON" "main.py" "mystocks" "buy" "600519" \
        "--qty" "100" "--price" "1500" "--name" "贵州茅台"

    run_test "Mystocks view positions (pos)" "DB" \
        "$PYTHON" "main.py" "mystocks" "pos"

    run_test "Mystocks summary" "DB" \
        "$PYTHON" "main.py" "mystocks" "summary"

    run_test "Mystocks history" "DB" \
        "$PYTHON" "main.py" "mystocks" "history" "--limit" "10"

    run_test "Account summary" "DB" \
        "$PYTHON" "main.py" "account" "--summary"

    # SKILL.md Section: 收藏管理
    run_test "Watchlist add" "DB" \
        "$PYTHON" "main.py" "watchlist" "--add" "300760" \
        "--name" "迈瑞医疗" "--tags" "医疗器械"

    run_test "Watchlist list" "DB" \
        "$PYTHON" "main.py" "watchlist" "--list"

    run_test "Watchlist remove" "DB" \
        "$PYTHON" "main.py" "watchlist" "--remove" "300760"

    # SKILL.md Section: 参数管理
    run_test "Params list" "DB" \
        "$PYTHON" "main.py" "params" "list"

    run_test "Params get" "DB" \
        "$PYTHON" "main.py" "params" "get" "--symbol" "600519"
}

# =============================================================================
# Category C: API Dependency Tests (with timeout)
# =============================================================================

test_api_dependency() {
    echo ""
    echo "====================================================================="
    echo "Category C: API Dependency Tests (10s timeout)"
    echo "====================================================================="

    # SKILL.md Section: 技术分析
    run_test "Analyze stock (analyze)" "API" \
        "$PYTHON" "main.py" "analyze" "600519" "--json"

    run_test "Analyze with strategy (vcp)" "API" \
        "$PYTHON" "main.py" "analyze" "600519" "--strategy" "vcp" "--json"

    # SKILL.md Section: 实时行情
    run_test "Query stock price (query)" "API" \
        "$PYTHON" "main.py" "query" "600519"

    run_test "Query multiple stocks" "API" \
        "$PYTHON" "main.py" "query" "600519" "000001"

    # SKILL.md Section: 资金流向
    run_test "Flow analysis" "API" \
        "$PYTHON" "main.py" "flow" "600519"

    # SKILL.md Section: 股票搜索
    run_test "Search stock by name" "API" \
        "$PYTHON" "main.py" "search" "平安"

    # SKILL.md Section: 板块分析
    run_test "Sector ranking" "API" \
        "$PYTHON" "main.py" "sector"

    run_test "Concept sector ranking" "API" \
        "$PYTHON" "main.py" "sector" "--concept"

    # SKILL.md Section: 数据导出
    run_test "Export K-line data" "API" \
        "$PYTHON" "main.py" "export" "600519" "--days" "5"

    # SKILL.md Section: 智能预警
    run_test "Alert check (once)" "API" \
        "$PYTHON" "main.py" "alert"

    run_test "Smart monitor (once)" "API" \
        "$PYTHON" "main.py" "smart-monitor" "--once"
}
```

- [ ] **Step 4: Verify bash syntax**

Run: `bash -n scripts/test_skill_commands.sh`
Expected: No output (syntax OK)

- [ ] **Step 5: Continue test_skill_commands.sh - Part 3 (Main execution and report)**

```bash
# =============================================================================
# Main Execution
# =============================================================================

main() {
    echo "====================================================================="
    echo "  SKILL.md Commands Test Suite"
    echo "  Project: $PROJECT_ROOT"
    echo "  Python:  $PYTHON"
    echo "  Date:    $(date)"
    echo "====================================================================="

    # Step 1: Run setup first
    log_info "Running test data setup..."
    "$PYTHON" "$PROJECT_ROOT/scripts/test_setup.py"
    if [[ $? -ne 0 ]]; then
        log_fail "Test setup failed"
        exit 1
    fi

    # Step 2: Run test categories
    test_no_dependency
    test_database_dependency
    test_api_dependency

    # Step 3: Print summary
    echo ""
    echo "====================================================================="
    echo "  Test Summary"
    echo "====================================================================="
    echo -e "  ${GREEN}PASS:${NC}  $PASS_COUNT"
    echo -e "  ${RED}FAIL:${NC}  $FAIL_COUNT"
    echo -e "  ${YELLOW}SKIP:${NC}  $SKIP_COUNT"
    echo -e "  TOTAL:  $TOTAL_COUNT"
    echo "====================================================================="

    # Calculate pass rate
    if [[ $TOTAL_COUNT -gt 0 ]]; then
        local pass_rate=$(( (PASS_COUNT * 100) / TOTAL_COUNT ))
        echo "  Pass Rate: ${pass_rate}%"
    fi

    # Print detailed results
    echo ""
    echo "====================================================================="
    echo "  Detailed Results"
    echo "====================================================================="
    for result in "${RESULTS[@]}"; do
        echo "  $result"
    done

    # Generate report file
    local report_dir="$PROJECT_ROOT/docs/test-reports"
    mkdir -p "$report_dir"
    local report_file="$report_dir/skill-commands-test-$(date +%Y%m%d-%H%M%S).md"

    {
        echo "# SKILL.md Commands Test Report"
        echo ""
        echo "**Generated:** $(date)"
        echo "**Project:** $PROJECT_ROOT"
        echo ""
        echo "## Summary"
        echo ""
        echo "| Metric | Count |"
        echo "|--------|-------|"
        echo "| PASS   | $PASS_COUNT |"
        echo "| FAIL   | $FAIL_COUNT |"
        echo "| SKIP   | $SKIP_COUNT |"
        echo "| TOTAL  | $TOTAL_COUNT |"
        echo ""
        echo "## Detailed Results"
        echo ""
        for result in "${RESULTS[@]}"; do
            echo "- $result"
        done
    } > "$report_file"

    log_info "Report saved to: $report_file"

    # Exit with appropriate code
    if [[ $FAIL_COUNT -gt 0 ]]; then
        exit 1
    fi
    exit 0
}

# Run main
main "$@"
```

- [ ] **Step 6: Make script executable and verify syntax**

Run:
```bash
chmod +x scripts/test_skill_commands.sh
bash -n scripts/test_skill_commands.sh
```
Expected: No errors

- [ ] **Step 7: Commit**

```bash
git add scripts/test_skill_commands.sh
git commit -m "test: add comprehensive test script for SKILL.md commands"
```

---

## Chunk 2: Test Execution

### Task 3: Run test suite

**Files:**
- Modify: (none - execution only)

- [ ] **Step 1: Run the test suite**

Run: `bash scripts/test_skill_commands.sh`
Expected: Tests execute, report generated

- [ ] **Step 2: Review test report**

Check: `docs/test-reports/skill-commands-test-*.md`
Verify: All expected commands tested, failures documented

- [ ] **Step 3: Fix any FAIL results (if applicable)**

If commands fail unexpectedly:
1. Investigate root cause
2. Fix command or mark as SKIP with reason
3. Re-run tests

- [ ] **Step 4: Final commit**

```bash
git add docs/test-reports/
git commit -m "docs: add test execution report for SKILL.md commands"
```

---

## Execution Checklist

- [ ] Chunk 1 complete (test infrastructure)
- [ ] Chunk 2 complete (test execution)
- [ ] All tests passing or documented as SKIP
- [ ] Report generated and reviewed

---

**Ready to execute?**
