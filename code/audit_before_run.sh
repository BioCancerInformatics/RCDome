#!/usr/bin/env bash
# RCDome pre-run audit — run BEFORE launching the app after any amendment.
# Usage: bash audit_before_run.sh
set -u
APP="D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Shiny app/RCDome_Atlas/APP"
RSCRIPT="C:/Program Files/R/R-4.2.3/bin/Rscript.exe"
cd "$APP" || exit 1

echo "=== 1. SCOPE (git diff stat) ==="
(cd "D:/RCDome_github" && git diff --stat HEAD -- app | tail -20)

echo ""
echo "=== 2. SYNTAX: R parse ==="
"$RSCRIPT" -e 'for (f in c("ui.R","server.R","global.R","R/utils.R", list.files("R", pattern="[.]R$", full.names=TRUE), list.files("modules", pattern="[.]R$", full.names=TRUE))) { tryCatch(parse(f), error=function(e) cat("PARSE FAIL:", f, conditionMessage(e), "\n")); }; cat("R parse done\n")' 2>&1 | grep -E "PARSE FAIL|done" | tail -20

echo ""
echo "=== 3. STRUCTURAL: empty args / dead code ==="
echo "-- list(, / c(, / , , --"
grep -rn "list(,\|c(,\|, ," R modules ui.R server.R global.R 2>/dev/null || echo "none"
echo "-- create/createFilter leftovers --"
grep -rn "create = TRUE\|createFilter\|rcdome_create" R modules ui.R server.R 2>/dev/null || echo "none"
echo "-- not_found_guard leftover --"
grep -rn "not_found_guard\|rcdome_not_found" R modules ui.R server.R www 2>/dev/null || echo "none"

echo ""
echo "=== 4. FUNCTIONAL-PRESERVATION markers ==="
for marker in "navigate_to_gene_page" "geneJump" "entityJump" "mod_board_ui" "mod_board_qa_ui"; do
  if grep -rq "$marker" . ; then echo "OK   $marker"; else echo "MISS $marker"; fi
done

echo ""
echo "=== 5. RUN TEST (30s) ==="
(nohup "$RSCRIPT" -e "shiny::runApp('.', port=8891, launch.browser=FALSE)" > /tmp/rcdome_audit_run.log 2>&1 &)
sleep 28
if grep -q "Listening on" /tmp/rcdome_audit_run.log && ! grep -q "Error in\|Warning: Error" /tmp/rcdome_audit_run.log; then
  echo "RUN OK: $(grep 'Listening on' /tmp/rcdome_audit_run.log | tail -1)"
else
  echo "RUN FAIL — see /tmp/rcdome_audit_run.log"
  grep -E "Error in|Warning: Error" /tmp/rcdome_audit_run.log | head -10
fi
PID=$(netstat -ano | grep ":8891" | grep LISTENING | awk '{print $5}' | head -1)
[ -n "$PID" ] && taskkill //PID "$PID" //F >/dev/null 2>&1

echo ""
echo "=== 6. ECHO (manual) ==="
echo "Verify any data/stat change against its source (matrix/decoder/benchmark JSON)."

echo ""
echo "=== AUDIT COMPLETE ==="
