# Regenerate matrix RDS with VCD reclassified L4 -> L5 (preserving structure)
prov <- paste0(
  "Treat as a morphology/context label unless a taxon-specific mechanism is provided. ",
  "Expert adjudication (sentinel 2026-09): reclassified L4->L5 (TAXON); vacuolization is ",
  "a phenotype, not a mechanism (atg1 disruption reveals a hidden non-vacuolar death); ",
  "founding evidence fungal (yeast)."
)

for (f in c("output databases/Phase 2C output/unified_gene_rcd_matrix_V026.rds",
            "Shiny app/RCDome_Atlas/APP/data/unified_gene_rcd_matrix_V026.rds")) {
  m <- readRDS(f)
  mm <- !is.na(m$rcd_form_canonical) & m$rcd_form_canonical == "Vacuolar cell death"
  cat(f, ": VCD rows =", sum(mm), "\n")
  if (sum(mm) > 0) {
    m$rcdome_level[mm] <- "L5"
    m$rcdome_level_name[mm] <- "L5 Generic/umbrella/legacy/taxon/emerging"
    m$decoder_category[mm] <- "TAXON"
    m$elic_onto_rcd_type[mm] <- "TAXON_SPECIFIC"
    m$elic_onto_operational_note[mm] <- prov
    saveRDS(m, f)
    cat("  -> updated\n")
  }
}
