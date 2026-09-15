# save_matrix_excel_rds.R
# Read RCDome V014 matrix and save as Excel (.xlsx) and RDS (.rds)
# Run: Rscript save_matrix_excel_rds.R

suppressPackageStartupMessages({
  library(readr)    # fast, encoding-safe CSV read
  library(writexl)  # write_xlsx
})

# --- Paths (adjust if needed) ---
csv_path <- file.path(
  "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript",
  "output databases", "Phase 2C output",
  "unified_gene_rcd_matrix_V014.csv"
)

out_dir <- dirname(csv_path)
xlsx_path <- file.path(out_dir, "unified_gene_rcd_matrix_V014.xlsx")
rds_path  <- file.path(out_dir, "unified_gene_rcd_matrix_V014.rds")

# --- Read ---
message("Reading: ", csv_path)
m <- read_csv(
  csv_path,
  col_types = cols(.default = col_character()),
  locale = locale(encoding = "UTF-8"),
  name_repair = "unique",
  show_col_types = FALSE
)

message("Rows: ", nrow(m), " | Columns: ", ncol(m))

# --- Basic integrity checks (auditable) ---
stopifnot(nrow(m) == 24834)
stopifnot(ncol(m) == 43)
stopifnot("rcdome_level" %in% names(m))
stopifnot("rcdome_level_name" %in% names(m))
stopifnot("rodr_category" %in% names(m))
stopifnot(all(m$rcdome_level %in% c("L1","L2","L3","L4","L5")))

lv <- table(m$rcdome_level)
message("Level distribution (rows):")
print(lv)

# --- Save Excel ---
message("Writing: ", xlsx_path)
write_xlsx(m, xlsx_path)
message("Excel saved.")

# --- Save RDS ---
message("Writing: ", rds_path)
saveRDS(m, rds_path, compress = "xz")
message("RDS saved.")

# --- Verify round-trip ---
m2 <- readRDS(rds_path)
stopifnot(identical(dim(m), dim(m2)))
message("Round-trip verified: ", nrow(m2), " x ", ncol(m2))

cat("\nDone.\n",
    "Excel: ", xlsx_path, "\n",
    "RDS:   ", rds_path, "\n", sep = "")
