#!/bin/bash

# Pre-Push GitHub Verification Script
# Ensures no sensitive data is about to be committed

echo "🔒 IBIS Pre-Push Security Verification"
echo "======================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

# Check 1: Verify .gitignore exists
echo "✓ Checking .gitignore..."
if [ ! -f ".gitignore" ]; then
    echo -e "${RED}✗ .gitignore not found${NC}"
    FAILED=$((FAILED + 1))
else
    echo -e "${GREEN}✓ .gitignore found${NC}"
fi

# Check 2: Verify sensitive files are ignored
echo ""
echo "✓ Verifying sensitive files are in .gitignore..."

SENSITIVE_FILES=(
    "ibis/keys.env"
    "data/ibis_true_state.json"
    "data/ibis_true_memory.json"
    "data/ibis_unified.db"
    ".env"
)

for file in "${SENSITIVE_FILES[@]}"; do
    if git check-ignore "$file" &>/dev/null; then
        echo -e "${GREEN}✓ $file is properly ignored${NC}"
    else
        echo -e "${YELLOW}⚠ $file may not be properly ignored${NC}"
    fi
done

# Check 3: Look for staged files that shouldn't be there
echo ""
echo "✓ Checking staged files..."
STAGED=$(git diff --cached --name-only)
FOUND_BAD=0

if echo "$STAGED" | grep -E "\.env|keys\.env" > /dev/null; then
    echo -e "${RED}✗ Found .env file in staging${NC}"
    FOUND_BAD=1
    FAILED=$((FAILED + 1))
fi

if echo "$STAGED" | grep -E "data/.*\.(json|db)" > /dev/null; then
    echo -e "${RED}✗ Found state/data file in staging${NC}"
    FOUND_BAD=1
    FAILED=$((FAILED + 1))
fi

if echo "$STAGED" | grep -E "\.log" > /dev/null; then
    echo -e "${RED}✗ Found log file in staging${NC}"
    FOUND_BAD=1
    FAILED=$((FAILED + 1))
fi

if [ $FOUND_BAD -eq 0 ]; then
    echo -e "${GREEN}✓ No sensitive files in staging${NC}"
fi

# Check 4: Scan for secrets in code
echo ""
echo "✓ Scanning staged code for exposed secrets..."
SECRETS=$(git diff --cached | grep -iE "api[_-]?key|secret[_-]?key|password|token.*=|Authorization|Bearer" || true)

if [ -n "$SECRETS" ]; then
    echo -e "${YELLOW}⚠ Found potential secrets in code:${NC}"
    echo "$SECRETS" | head -5
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        FAILED=$((FAILED + 1))
    fi
fi

# Check 5: Verify real metrics not in staged files
echo ""
echo "✓ Checking for real trading metrics in staged files..."
METRICS=$(git diff --cached | grep -E "50\.8|49\.28|61.*trade|recycle_profit.*100" || true)

if [ -n "$METRICS" ]; then
    echo -e "${YELLOW}⚠ Found potential real metrics:${NC}"
    echo "$METRICS" | head -5
    echo ""
    echo "These may be internal doc references (acceptable if in internal docs)"
    echo "but not in user-facing docs like README.md or DEPLOYMENT.md"
fi

# Check 6: Summary
echo ""
echo "======================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Pre-push verification PASSED${NC}"
    echo -e "${GREEN}Safe to push to GitHub${NC}"
    exit 0
else
    echo -e "${RED}✗ Pre-push verification FAILED${NC}"
    echo -e "${RED}Please fix issues before pushing${NC}"
    exit 1
fi

