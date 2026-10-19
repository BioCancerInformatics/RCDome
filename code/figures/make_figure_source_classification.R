# RCDome Supplementary Figure S3 (V027): mechanistic associations per source,
# STACKED by RCD entity ontological level (L1-L5), concordant RCDome palette.
# Note: canonical generator is make_figure_s2_stacked_by_level.py (Python);
# this R script mirrors it for environments with R + magick.
library(magick)

df <- readRDS('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/output databases/Phase 2C output/unified_gene_rcd_matrix_V027.rds')

# mechanistic associations only
mech <- df[df$final_mechanistic == 'YES', ]

# explode source_databases (semicolon-separated)
src <- strsplit(mech$source_databases, ';')
src <- trimws(unlist(src))
src <- src[src != '']
lvl <- rep(mech$rcdome_level, lengths(strsplit(mech$source_databases, ';')))

# source x level count matrix
mat <- table(src, lvl)
mat <- mat[, c('L1','L2','L3','L4','L5')]
mat <- mat[order(rowSums(mat)), ]  # ascending -> bottom to top

clean <- c('Rodrigues2025' = 'Rodrigues et al. 2025', 'NCBI_Gene' = 'NCBI Gene',
           'Elicit_Phase3' = 'Elicit Phase 3', 'Elicit_Alert' = 'Elicit Alert')
rownames(mat) <- ifelse(rownames(mat) %in% names(clean), clean[rownames(mat)], rownames(mat))

# CONCORDANT ontological palette (strictly identical to Figure 4)
palette <- c('L1' = '#FCBB18',
             'L2' = '#5DADE2',
             'L3' = '#58D68D',
             'L4' = '#AF7AC5',
             'L5' = '#F1948A')
lvl_names <- c('L1' = 'L1 Modalities (16)',
               'L2' = 'L2 Subtypes (5)',
               'L3' = 'L3 Triggers (2)',
               'L4' = 'L4 Functional/contextual (11)',
               'L5' = 'L5 Generic/umbrella/legacy/taxon/emerging (19)')
dark <- '#1F2937'
out <- 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure_S3_source_classification'

draw <- function() {
  par(mar = c(4, 13, 3, 5), family = 'Helvetica', cex = 0.9)
  bp <- barplot(t(mat), horiz = TRUE, col = unname(palette), border = dark,
                las = 1, cex.names = 0.65, axes = FALSE,
                xlim = c(0, max(rowSums(mat)) * 1.16),
                main = 'Mechanistic associations per source, stacked by RCD entity ontological level',
                col.main = dark, font.main = 2)
  axis(1, col = dark, col.axis = dark)
  # total count labels
  text(rowSums(mat) + max(rowSums(mat)) * 0.01, bp,
       labels = format(rowSums(mat), big.mark = ','), pos = 4, cex = 0.5, col = dark)
  legend('bottomright', legend = lvl_names, fill = unname(palette),
         border = dark, cex = 0.55, bty = 'n', title = 'Ontological level',
         title.col = dark, text.col = dark)
  mtext('Mechanistic associations (final_mechanistic = YES)', side = 1, line = 2.5, col = dark, cex = 0.8)
}

tryCatch({
  pdf(paste0(out, '.pdf'), width = 8.27, height = 11.69, family = 'Helvetica')
  draw(); dev.off()
}, error = function(e) cat('PDF skipped:', conditionMessage(e), '\n'))

png('tmp_src.png', width = 8.27, height = 11.69, units = 'in', res = 600)
draw(); dev.off()
img <- image_read('tmp_src.png', density = '600x600')
image_write(img, path = paste0(out, '.tiff'), format = 'tiff', compression = 'lzw')
image_write(image_convert(img, format = 'png'), path = paste0(out, '.png'))
file.remove('tmp_src.png')

write.csv(as.data.frame.matrix(mat), paste0(out, '_data.csv'), row.names = TRUE)
cat('saved Figure_S3_source_classification (stacked by ontological level, V027)\n')
