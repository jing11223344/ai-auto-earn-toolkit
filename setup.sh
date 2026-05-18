#!/usr/bin/env bash
set -e

echo "=========================================="
echo "  AI Auto-Earn Toolkit v1 - One-Click Setup"
echo "=========================================="

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python3 not found. Install it first."
    exit 1
fi
echo "✅ Python3 found: $(python3 --version)"

# Check curl
if ! command -v curl &>/dev/null; then
    echo "❌ curl not found. Install it: apt install curl -y"
    exit 1
fi
echo "✅ curl found"

# Setup .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "📝 Created .env from template."
    echo "   Edit it now: nano .env"
    echo "   Fill in your OKX API keys and GitHub token."
else
    echo "✅ .env already exists"
fi

# Make scripts executable
chmod +x scripts/*.py
echo "✅ Scripts ready"

echo ""
echo "=========================================="
echo "  ✅ Setup complete!"
echo ""
echo "  Quick start:"
echo "  1. Edit .env with your keys: nano .env"
echo "  2. Test trading:    python3 scripts/auto_trader.py"
echo "  3. Test bounty:     python3 scripts/bounty_scanner.py"
echo "  4. Set up cron:     bash install_cron.sh"
echo "=========================================="
