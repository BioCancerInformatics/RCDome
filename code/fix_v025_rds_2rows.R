df <- readRDS('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/output databases/Phase 2C output/unified_gene_rcd_matrix_V025.rds')

m1 <- df$gene_symbol == 'NLRX1' & df$rcd_form_canonical == 'MPT-driven necrosis'
df$llm_status[m1] <- 'NEEDS_CONTEXT'
df$llm_pmids[m1] <- '41739553'
df$llm_evidence_force[m1] <- '1'
df$mechanistic_class[m1] <- 'CONTEXT_GAP'

m2 <- df$gene_symbol == 'PPIF' & df$rcd_form_canonical == 'MPT-driven necrosis'
df$llm_status[m2] <- 'CONFIRMED'
df$llm_pmids[m2] <- '15800627'
df$llm_evidence_force[m2] <- '1'
df$mechanistic_class[m2] <- 'MECHANISTIC'

saveRDS(df, 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/output databases/Phase 2C output/unified_gene_rcd_matrix_V025.rds')

i <- which(df$gene_symbol %in% c('NLRX1','PPIF') & df$rcd_form_canonical == 'MPT-driven necrosis')
print(df[i, c('gene_symbol','llm_status','mechanistic_class','llm_pmids')], row.names = FALSE)
cat('NaN mechanistic_class:', sum(is.na(df$mechanistic_class)), '\n')
cat('RDS saved\n')
