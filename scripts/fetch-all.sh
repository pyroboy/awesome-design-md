#!/bin/bash
# fetch-all.sh — fetch all DESIGN.md files from getdesign.md using the getdesign CLI
# Saves to: design-md/{brand}/DESIGN.md in the fork

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FORK_DIR="$(dirname "$SCRIPT_DIR")"
BRANDS=(
  airbnb airtable apple bmw cal claude clay clickhouse cohere
  coinbase composio cursor elevenlabs expo ferrari figma framer
  hashicorp ibm intercom kraken lamborghini linear.app lovable
  minimax mintlify miro mistral.ai mongodb notion nvidia ollama
  opencode.ai pinterest posthog raycast renault replicate resend
  revolut runwayml sanity semrush sentry spacex spotify stripe
  supabase superhuman tesla together.ai uber vercel voltagent
  warp webflow wise x.ai zapier
)

OK=0
FAIL=0

for brand in "${BRANDS[@]}"; do
  OUT_DIR="$FORK_DIR/design-md/$brand"
  mkdir -p "$OUT_DIR"

  echo -n "[$brand] Fetching... "

  npx getdesign@latest add "$brand" --out "$OUT_DIR/DESIGN.md" --force 2>&1 | grep -v "^\s*$" | grep -v "npm warn" | tail -1

  if [ -f "$OUT_DIR/DESIGN.md" ] && [ $(wc -c < "$OUT_DIR/DESIGN.md") -gt 500 ]; then
    echo "✓ ( $(wc -c < "$OUT_DIR/DESIGN.md") bytes)"
    ((OK++))
  else
    echo "✗ FAILED (file missing or too small)"
    ((FAIL++))
  fi

  # Rate limit: be polite to getdesign.md
  sleep 0.5
done

echo ""
echo "=== DONE ==="
echo "OK: $OK / ${#BRANDS[@]}"
echo "Failed: $FAIL / ${#BRANDS[@]}"
