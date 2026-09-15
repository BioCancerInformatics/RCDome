RCDome Digital Molecular RCD Board - Zima Package (master)
=========================================================

CONTENTS
- board/run_board_benchmark.py     : full benchmark (26 golden + 53 census + model comparison + stats)
- board/smoke_test.py               : ONE-pair smoke test (~15s) -- RUN THIS FIRST
- board/RCD_Board_Governance.md     : governance v2 (prose + 4 tiers + domain boundary)
- board/RCD_Board_DeepSeek_Prompt.md: the DeepSeek system prompt
- board/RCD_Board_Benchmark.md      : benchmark spec (9 tests, n computed, CI 95%)
- data/unified_gene_rcd_matrix_V026.csv : matrix V026 (22,473 x 71)
- data/RCDome_Decoder_53.csv        : decoder (53 x 39)

POLICY (mandatory sequence)
1. Run the SMOKE TEST first (1 pair, ~15s) to verify the narrative output is correct.
2. ONLY after the smoke test is approved, run the FULL benchmark.

COMMANDS (run from the board/ folder, in order)
  export DEEPSEEK_KEY="sk-..."
  nix-shell -p python3Packages.pandas python3Packages.requests python3Packages.scipy
  python3 smoke_test.py        # <-- FIRST: see the narrative
  python3 run_board_benchmark.py  # <-- only after smoke test is OK
  exit
