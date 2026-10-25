# RCDome Figure 4: 53-entity coverage — log2 bars + REAL gene count labels (V027)
library(magick)

df <- readRDS('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/output databases/Phase 2C output/unified_gene_rcd_matrix_V027.rds')

agg <- aggregate(gene_symbol ~ rcd_form_canonical + rcdome_level, data = df,
                 FUN = function(x) length(unique(x)))
names(agg)[3] <- 'genes'
agg <- agg[order(agg$genes), ]

lg <- log2(agg$genes)

lvl <- c('L1' = '#FCBB18',
         'L2' = '#5DADE2',
         'L3' = '#58D68D',
         'L4' = '#AF7AC5',
         'L5' = '#F1948A')
lvl_name <- c('L1' = 'L1 Modalities',
              'L2' = 'L2 Subtypes',
              'L3' = 'L3 Triggers',
              'L4' = 'L4 Functional/contextual',
              'L5' = 'L5 Generic/umbrella/taxon')
cols <- unname(lvl[agg$rcdome_level])
dark <- '#1F2937'
out <- 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures_A4/Figure_4_entity_coverage_A4'

# write data CSV
write.csv(agg[, c('rcd_form_canonical', 'rcdome_level', 'genes')],
          'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures_A4/Figure_4_entity_coverage_data.csv',
          row.names = FALSE)

ticks <- c(1, 4, 16, 64, 256, 1024, 4096)

draw <- function() {
  par(mar = c(4, 13, 3, 5), family = 'Helvetica', cex = 1.1)
  bp <- barplot(lg, horiz = TRUE, names.arg = agg$rcd_form_canonical,
          col = cols, border = dark, las = 1, cex.names = 0.68,
          axes = FALSE, xlim = c(0, 13.8),
          main = 'Gene coverage of the 53 canonicalized RCD-related entities', col.main = dark, font.main = 2)
  axis(1, at = log2(ticks), labels = ticks, las = 1, col = dark, col.axis = dark)
  text(lg + 0.06, bp, labels = format(agg$genes, big.mark = ','), pos = 4, cex = 0.68, col = dark)
  mtext('Genes associated with the entity  (log2 scale)', side = 1, line = 2.5, col = dark)
  legend('bottomright', legend = unname(lvl_name), fill = unname(lvl), border = dark,
         bty = 'n', cex = 0.85, text.col = dark, title = 'Ontological level', title.col = dark)
}

tryCatch({
  pdf(paste0(out, '.pdf'), width = 8.27, height = 11.69, family = 'Helvetica')
  draw()
  dev.off()
}, error = function(e) cat('PDF skipped (locked?):', conditionMessage(e), '\n'))

png('tmp_entity.png', width = 8.27, height = 11.69, units = 'in', res = 600)
draw()
dev.off()
img <- image_read('tmp_entity.png', density = '600x600')
image_write(img, path = paste0(out, '.tiff'), format = 'tiff', compression = 'lzw')
file.copy('tmp_entity.png', paste0(out, '.png'), overwrite = TRUE)
file.remove('tmp_entity.png')
cat('Figure 4 regenerated (V027)\n')
