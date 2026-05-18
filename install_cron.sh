#!/usr/bin/env bash
# Install all cron jobs for AI Auto-Earn Toolkit
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
PY=python3

# Auto Trader - every 15 min
cat <<'CRON' | crontab -
# AI Auto-Earn Toolkit
*/15 * * * * cd $DIR && $PY scripts/auto_trader.py >> /tmp/auto_trader.log 2>&1
*/30 * * * * cd $DIR && $PY scripts/market_monitor.py >> /tmp/market_monitor.log 2>&1
0 */3 * * * cd $DIR && $PY scripts/bounty_scanner.py >> /tmp/bounty_scanner.log 2>&1
0 8,12,16,20 * * * cd $DIR && $PY scripts/agenthansa-autopilot.py >> /tmp/agenthansa.log 2>&1
0 22 * * * cd $DIR && echo "Daily Earnings Summary:" && cat /tmp/auto_trader.log | tail -10
CRON

echo "✅ Cron jobs installed"
echo "   - Auto Trader:  every 15 min"
echo "   - Market Watch: every 30 min"
echo "   - Bounty Scan:  every 3 hours"
echo "   - AgentHansa:   4x daily"
echo "   - Daily Report: 10 PM"
