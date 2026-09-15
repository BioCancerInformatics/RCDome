# Results count recompute — manuscript vs V026 matrix

| metric | manuscript (before) | matrix (after) | delta |
|---|---|---|---|
| matrix_rows | 22,473 | 22,473 | +0 |
| unique_pairs | 21,568 | 21,568 | +0 |
| unique_genes | 9,265 | 9,265 | +0 |
| entities | 53 | 53 | +0 |
| EXECUTOR | 469 | 580 | +111 |
| REGULATOR | 9,489 | 9,971 | +482 |
| MARKER | 5 | 6 | +1 |
| UNCERTAIN | 11,605 | 11,916 | +311 |
| PROMOTES | 5,070 | 5,452 | +382 |
| PROTECTS | 4,755 | 4,964 | +209 |
| UNCLEAR | 11,743 | 12,057 | +314 |
| T1 | 2,862 | 2,864 | +2 |
| T2 | 5,686 | 5,686 | +0 |
| T3 | 8,213 | 8,212 | -1 |
| T4 | 5,711 | 5,711 | +0 |

Tier sum (before): 22,472
Tier sum (after):  22,473

Direction (after) = PROMOTES 5,452 + PROTECTS 4,964 = 10,416
Role (after) = EXECUTOR 580 + REGULATOR 9,971 + MARKER 6 + UNCERTAIN 11,916 = 22,473

## Role x direction (matrix)

| role | PROMOTES | PROTECTS | UNCLEAR |
|---|---|---|---|
| EXECUTOR | 580 | 0 | 0 |
| MARKER | 0 | 0 | 6 |
| REGULATOR | 4826 | 4964 | 181 |
| UNCERTAIN | 46 | 0 | 11870 |
