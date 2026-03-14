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
