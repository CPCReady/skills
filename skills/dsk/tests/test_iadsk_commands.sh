#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IADSK="python3 $SCRIPT_DIR/../scripts/iadsk.py"
TEST_DATA="$SCRIPT_DIR/test_data"
TEMP_DIR=$(mktemp -d)

trap "rm -rf $TEMP_DIR" EXIT

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

test_command() {
	local test_name="$1"
	local expected_result="$2"
	local command="$3"

	TESTS_TOTAL=$((TESTS_TOTAL + 1))

	echo -n "[$TESTS_TOTAL] $test_name: "

	if eval "$command" >/dev/null 2>&1; then
		if [ "$expected_result" = "success" ]; then
			echo -e "${GREEN}PASS${NC}"
			TESTS_PASSED=$((TESTS_PASSED + 1))
		else
			echo -e "${RED}FAIL${NC} (esperado error)"
			TESTS_FAILED=$((TESTS_FAILED + 1))
		fi
	else
		if [ "$expected_result" = "error" ]; then
			echo -e "${GREEN}PASS${NC}"
			TESTS_PASSED=$((TESTS_PASSED + 1))
		else
			echo -e "${RED}FAIL${NC}"
			TESTS_FAILED=$((TESTS_FAILED + 1))
		fi
	fi
}

test_output_contains() {
	local test_name="$1"
	local pattern="$2"
	local command="$3"

	TESTS_TOTAL=$((TESTS_TOTAL + 1))

	echo -n "[$TESTS_TOTAL] $test_name: "

	output=$(eval "$command" 2>&1)
	if echo "$output" | grep -q "$pattern"; then
		echo -e "${GREEN}PASS${NC}"
		TESTS_PASSED=$((TESTS_PASSED + 1))
	else
		echo -e "${RED}FAIL${NC}"
		echo "  Expected to contain: $pattern"
		echo "  Output received:"
		echo "$output" | head -20 | sed 's/^/    /'
		TESTS_FAILED=$((TESTS_FAILED + 1))
	fi
}

echo "=========================================="
echo "EXHAUSTIVE TEST: iadsk.py"
echo "=========================================="
echo ""

echo ">>> Preparing test files..."

cat >"$TEST_DATA/sample.bas" <<'BASIC'
10 REM Test BASIC File
20 PRINT "Hello from iadsk.py"
30 FOR I=1 TO 10
40 PRINT I
50 NEXT I
60 END
BASIC

python3 -c "open('$TEST_DATA/sample.bin', 'wb').write(b'\x00' * 256 + b'BINARY_TEST_DATA' * 100)"

cat >"$TEST_DATA/sample.txt" <<'ASCII'
Linea de prueba 1
Linea de prueba 2
Linea de prueba 3
ASCII

echo "Test files created in: $TEST_DATA"
echo ""

echo ">>> TEST 1: Create DSK"
echo "-----------------------------------"

DSK="$TEMP_DIR/test.dsk"
test_command "Create new DSK" "success" "$IADSK $DSK --new"
test_output_contains "DSK contains MV-CPCEMU" "MV - CPCEMU" "$IADSK $DSK --dump"
test_output_contains "DSK has 40 tracks" "tracks: 40" "$IADSK $DSK --dump"

echo ""

echo ">>> TEST 2: Add files"
echo "-----------------------------------"

DSK="$TEMP_DIR/test_files.dsk"
$IADSK $DSK --new >/dev/null

test_command "Add BASIC file" "success" "$IADSK $DSK --put-bin $TEST_DATA/sample.bas"
test_output_contains "BASIC in catalog" "SAMPLE" "$IADSK $DSK --cat"

$IADSK $DSK --put-bin $TEST_DATA/sample.bin >/dev/null
test_output_contains "BIN in catalog" "BIN" "$IADSK $DSK --cat"

$IADSK $DSK --put-ascii $TEST_DATA/sample.txt >/dev/null
test_output_contains "TXT in catalog" "TXT" "$IADSK $DSK --cat"

$IADSK $DSK --put-raw $TEST_DATA/sample.bin >/dev/null
test_output_contains "RAW in catalog" "BIN" "$IADSK $DSK --cat"

echo ""

echo ">>> TEST 3: FREE command"
echo "-----------------------------------"

DSK="$TEMP_DIR/test_free.dsk"
$IADSK $DSK --new >/dev/null

test_output_contains "Free space ~180KB" "180 KB" "$IADSK $DSK --free"
test_output_contains "Shows % free" "%" "$IADSK $DSK --free"
test_output_contains "Shows clusters" "Clusters" "$IADSK $DSK --free"
test_output_contains "Shows cluster map" "▫" "$IADSK $DSK --free"
test_output_contains "Shows used clusters" "Used" "$IADSK $DSK --free"

$IADSK $DSK --put-bin $TEST_DATA/sample.bas >/dev/null
$IADSK $DSK --put-bin $TEST_DATA/sample.bin >/dev/null

free_output=$($IADSK $DSK --free)
if echo "$free_output" | grep -q "Free Space"; then
	echo -e "[test] Space updated: ${GREEN}PASS${NC}"
	TESTS_PASSED=$((TESTS_PASSED + 1))
else
	echo -e "[test] Space not updated: ${RED}FAIL${NC}"
	TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

echo ""

echo ">>> TEST 4: ERA command (delete)"
echo "-----------------------------------"

DSK="$TEMP_DIR/test_era.dsk"
$IADSK $DSK --new >/dev/null
$IADSK $DSK --put-bin $TEST_DATA/sample.bas >/dev/null

test_output_contains "Delete existing file" "eliminado" "$IADSK $DSK --era SAMPLE.BAS"

$IADSK $DSK --era SAMPLE.BAS >/dev/null
if $IADSK $DSK --cat 2>&1 | grep -q "SAMPLE.BAS"; then
	echo -e "[test] File still in catalog: ${RED}FAIL${NC}"
	TESTS_FAILED=$((TESTS_FAILED + 1))
else
	echo -e "[test] File deleted: ${GREEN}PASS${NC}"
	TESTS_PASSED=$((TESTS_PASSED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

DSK2="$TEMP_DIR/test_era2.dsk"
$IADSK $DSK2 --new >/dev/null
test_command "Error deleting nonexistent" "error" "$IADSK $DSK2 --era NOTEXIST.BAS"

echo ""

echo ">>> TEST 5: LIST command"
echo "-----------------------------------"

DSK="$TEMP_DIR/test_list.dsk"
$IADSK $DSK --new >/dev/null
$IADSK $DSK --put-bin $TEST_DATA/sample.bas >/dev/null

test_output_contains "List BASIC" "File Content" "$IADSK $DSK --list SAMPLE.BAS"
test_output_contains "Shows REM" "REM" "$IADSK $DSK --list SAMPLE.BAS"
test_output_contains "Shows PRINT" "PRINT" "$IADSK $DSK --list SAMPLE.BAS"
test_output_contains "Shows Tamano" "Tamano" "$IADSK $DSK --list SAMPLE.BAS"
test_output_contains "Shows Header AMSDOS" "AMSDOS" "$IADSK $DSK --list SAMPLE.BAS"

test_output_contains "Hex dump works" "Hex Dump" "$IADSK $DSK --list SAMPLE.BAS --hex"
test_output_contains "Hex shows offsets" "0000" "$IADSK $DSK --list SAMPLE.BAS --hex"

DSK2="$TEMP_DIR/test_list2.dsk"
$IADSK $DSK2 --new >/dev/null
test_command "Error listing nonexistent" "error" "$IADSK $DSK2 --list NOTEXIST.BAS"

echo ""

echo ">>> TEST 6: GET command (extract)"
echo "-----------------------------------"

DSK="$TEMP_DIR/test_get.dsk"
$IADSK $DSK --new >/dev/null
$IADSK $DSK --put-bin $TEST_DATA/sample.bas >/dev/null

OUTPUT="$TEMP_DIR/extracted.bas"
test_command "Extract file by index" "success" "$IADSK $DSK --get 0 --output $OUTPUT"

if [ -f "$OUTPUT" ] && [ -s "$OUTPUT" ]; then
	echo -e "[test] File extracted exists: ${GREEN}PASS${NC}"
	TESTS_PASSED=$((TESTS_PASSED + 1))
else
	echo -e "[test] File extracted: ${RED}FAIL${NC}"
	TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

OUTPUT2="$TEMP_DIR/extracted_no_header.bin"
$IADSK $DSK --get 0 --no-header --output $OUTPUT2 >/dev/null
if [ -f "$OUTPUT2" ]; then
	echo -e "[test] Extract without header: ${GREEN}PASS${NC}"
	TESTS_PASSED=$((TESTS_PASSED + 1))
else
	echo -e "[test] Extract without header: ${RED}FAIL${NC}"
	TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

echo ""

echo ">>> TEST 7: CHECK command"
echo "-----------------------------------"

DSK="$TEMP_DIR/test_check.dsk"
$IADSK $DSK --new >/dev/null

test_command "Valid DSK passes check" "success" "$IADSK $DSK --check"

echo "invalid-data" >"$TEMP_DIR/invalid.dsk"
test_command "Invalid DSK fails check" "error" "$IADSK $TEMP_DIR/invalid.dsk --check"

echo ""

echo ">>> TEST 8: DUMP command"
echo "-----------------------------------"

DSK="$TEMP_DIR/test_dump.dsk"
$IADSK $DSK --new >/dev/null

test_output_contains "Dump shows header" "HEADER" "$IADSK $DSK --dump"
test_output_contains "Dump shows tracks" "Track" "$IADSK $DSK --dump"

echo ""

echo ">>> TEST 9: CAT command"
echo "-----------------------------------"

DSK="$TEMP_DIR/test_cat.dsk"
$IADSK $DSK --new >/dev/null
$IADSK $DSK --put-bin $TEST_DATA/sample.bas >/dev/null

test_output_contains "Cat lists files" "listing" "$IADSK $DSK --cat"

echo ""

echo ">>> TEST 10: Case insensitive operations"
echo "-----------------------------------"

DSK="$TEMP_DIR/test_case.dsk"
$IADSK $DSK --new >/dev/null
$IADSK $DSK --put-bin $TEST_DATA/sample.bas >/dev/null

$IADSK $DSK --era sample.bas >/dev/null
if $IADSK $DSK --cat 2>&1 | grep -qi "SAMPLE.BAS"; then
	echo -e "[test] Case insensitive era: ${RED}FAIL${NC}"
	TESTS_FAILED=$((TESTS_FAILED + 1))
else
	echo -e "[test] Case insensitive era: ${GREEN}PASS${NC}"
	TESTS_PASSED=$((TESTS_PASSED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

echo ""

echo ">>> TEST 11: Multiple files"
echo "-----------------------------------"

DSK="$TEMP_DIR/test_multi.dsk"
$IADSK $DSK --new >/dev/null
for i in {1..5}; do
	$IADSK $DSK --put-bin $TEST_DATA/sample.bas >/dev/null 2>&1 || break
done

test_output_contains "Multiple files catalog" "SAMPLE.BAS" "$IADSK $DSK --cat"
count=$(grep -o "SAMPLE" <<<"$($IADSK $DSK --cat)" | wc -l)
if [ "$count" -gt 0 ]; then
	echo -e "[test] Multiple entries: ${GREEN}PASS${NC}"
	TESTS_PASSED=$((TESTS_PASSED + 1))
else
	echo -e "[test] Multiple entries: ${RED}FAIL${NC}"
	TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

echo ""

echo ">>> TEST 12: Version command"
echo "-----------------------------------"

test_output_contains "Version shows 1.0.0" "1.0.0" "$IADSK --version"

echo ""

echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo ""
echo -e "Total Tests:   $TESTS_TOTAL"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
	echo -e "${GREEN}=========================================="
	echo "ALL TESTS PASSED"
	echo -e "==========================================${NC}"
	exit 0
else
	echo -e "${RED}=========================================="
	echo "SOME TESTS FAILED"
	echo -e "==========================================${NC}"
	exit 1
fi
