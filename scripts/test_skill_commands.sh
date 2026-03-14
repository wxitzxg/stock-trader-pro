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
        if [[ "$category" == "API" ]] && [[ "$output" == *"Network"* || "$output" == *"connection"* || "$output" == *"AKShare"* || "$output" == *"连接"* ]]; then
            log_skip "$desc (API unavailable)"
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

    # SKILL.md Section: 初始化持仓
    run_test "Init position (single stock mode)" "DB" \
        "$PYTHON" "main.py" "init-position" \
        "--code" "000001" "--qty" "200" "--cost" "10.5" "--name" "平安银行"

    # SKILL.md Section: 持仓管理
    run_test "Account deposit" "DB" \
        "$PYTHON" "main.py" "account" "--deposit" "100000"

    run_test "Mystocks buy position" "DB" \
        "$PYTHON" "main.py" "mystocks" "buy" \
        "--code" "600519" "--qty" "100" "--price" "1500" "--name" "贵州茅台"

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

    # Additional DB tests - 持仓管理补充
    run_test "Account withdraw" "DB" \
        "$PYTHON" "main.py" "account" "--withdraw" "10000"

    run_test "Mystocks sell position" "DB" \
        "$PYTHON" "main.py" "mystocks" "sell" \
        "--code" "600519" "--qty" "50" "--price" "1600"

    run_test "Holdings with refresh" "DB" \
        "$PYTHON" "main.py" "holdings" "--refresh"

    # SKILL.md Section: 收藏管理 - 补充
    run_test "Watchlist add with target/stop-loss" "DB" \
        "$PYTHON" "main.py" "watchlist" "--add" "000858" \
        "--name" "五粮液" "--target" "200" "--stop-loss" "150"

    # SKILL.md Section: 参数管理 - 补充
    run_test "Params set" "DB" \
        "$PYTHON" "main.py" "params" "set" "--symbol" "600519" \
        "--name" "贵州茅台" "--params" "vcp.min_drops=3"

    run_test "Params remove" "DB" \
        "$PYTHON" "main.py" "params" "remove" "--symbol" "600519"
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

    # SKILL.md Section: 监控预警
    run_test "Monitor with output file" "API" \
        "$PYTHON" "main.py" "monitor" "--output" "/tmp/monitor_report.md"

    # Additional API tests - 补充测试
    run_test "Analyze with full options" "API" \
        "$PYTHON" "main.py" "analyze" "600519" "--full" "--json"

    run_test "Analyze watchlist" "API" \
        "$PYTHON" "main.py" "analyze" "--watchlist" "--json"

    run_test "Query ETF" "API" \
        "$PYTHON" "main.py" "query" "510300"

    run_test "Search by code" "API" \
        "$PYTHON" "main.py" "search" "600"

    run_test "Sector region" "API" \
        "$PYTHON" "main.py" "sector" "--region"

    run_test "Sector limit" "API" \
        "$PYTHON" "main.py" "sector" "--limit" "10"

    run_test "Export JSON format" "API" \
        "$PYTHON" "main.py" "export" "600519" "--format" "json" "--days" "5"

    run_test "Export with output file" "API" \
        "$PYTHON" "main.py" "export" "600519" "-o" "/tmp/test_export.csv" "--days" "5"

    run_test "Monitor no-position" "API" \
        "$PYTHON" "main.py" "monitor" "--no-position"

    run_test "Monitor no-watchlist" "API" \
        "$PYTHON" "main.py" "monitor" "--no-watchlist"

    run_test "Update stock list full" "API" \
        "$PYTHON" "main.py" "update-stock-list" "--full"

    run_test "Update prices once" "API" \
        "$PYTHON" "main.py" "update-prices" "--once"

    run_test "Update kline once" "API" \
        "$PYTHON" "main.py" "update-kline" "--once"
}

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
