# RCDome Supplementary Figure S2: database contribution (20 sources) + corroboration
library(magick)

df <- readRDS('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/output databases/Phase 2C output/unified_gene_rcd_matrix_V027.rds')

# --- per-source association counts ---
src <- unlist(strsplit(df$source_databases, ';'))
src <- trimws(src)
tab <- sort(table(src))                    # ascending -> bottom to top

clean <- c('Rodrigues2025' = 'Rodrigues et al. 2025', 'NCBI_Gene' = 'NCBI Gene',
           'Elicit_Phase3' = 'Elicit Phase 3', 'Elicit_Alert' = 'Elicit Alert')
nms <- ifelse(names(tab) %in% names(clean), clean[names(tab)], names(tab))

# --- corroboration: number of sources per association ---
ns <- as.integer(df$num_sources)
ns <- ns[ns >= 1 & ns <= 14]
nsd <- table(factor(ns, levels = 1:14))

dark <- '#1F2937'
out <- 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Submission FAI/Figures_A4/Figure_S1_database_contribution_A4'

ticks <- c(2, 8, 32, 128, 512, 2048, 8192)

pdf(paste0(out, '.pdf'), width = 8.27, height = 11.69, family = 'Helvetica')
par(mfrow = c(2, 1), mar = c(4, 12, 3, 4), family = 'Helvetica', cex = 1.1)

# Panel A: per-source contribution (log2 + real counts)
lg <- log2(as.numeric(tab))
bp <- barplot(lg, horiz = TRUE, names.arg = nms, col = '#AED6F1', border = dark,
              las = 1, cex.names = 0.8, axes = FALSE, xlim = c(0, 15.3),
              main = '')
axis(1, at = log2(ticks), labels = ticks, las = 1, col = dark, col.axis = dark)
text(lg + 0.06, bp, labels = format(as.numeric(tab), big.mark = ','), pos = 4, cex = 0.9, col = dark)
mtext('Gene\u2013RCD associations (log2 scale)', side = 1, line = 2.5, col = dark)
mtext('Associations contributed by each source database', side = 3, line = 1.2, at = grconvertX(0.5, 'ndc', 'user'), adj = 0.5, font = 2, cex = 1.1, col = dark)
mtext('(A)', side = 3, line = 0.8, at = grconvertX(0.02, 'ndc', 'user'), adj = 0, xpd = NA, font = 2, cex = 1.25, col = dark)

# Panel B: corroboration (num_sources distribution)
bp2 <- barplot(as.numeric(nsd), names.arg = 1:14, col = '#F9E79F', border = dark,
               las = 1, cex.names = 1.05, axes = FALSE, ylim = c(0, 11000),
               main = '')
axis(2, at = seq(0, 10000, 2000), las = 1, col = dark, col.axis = dark)
text(bp2, as.numeric(nsd) + 200, labels = format(as.numeric(nsd), big.mark = ','), cex = 0.9, col = dark)
mtext('Number of sources', side = 1, line = 2.5, col = dark)
mtext('Gene\u2013RCD associations', side = 2, line = 3.2, col = dark)
mtext('Number of source databases per association', side = 3, line = 1.2, at = grconvertX(0.5, 'ndc', 'user'), adj = 0.5, font = 2, cex = 1.1, col = dark)
mtext('(B)', side = 3, line = 0.8, at = grconvertX(0.02, 'ndc', 'user'), adj = 0, xpd = NA, font = 2, cex = 1.25, col = dark)

dev.off()

png('tmp_db.png', width = 8.27, height = 11.69, units = 'in', res = 600)
par(mfrow = c(2, 1), mar = c(4, 12, 3, 4), family = 'Helvetica', cex = 1.1)
lg <- log2(as.numeric(tab))
bp <- barplot(lg, horiz = TRUE, names.arg = nms, col = '#AED6F1', border = dark,
              las = 1, cex.names = 0.8, axes = FALSE, xlim = c(0, 15.3),
              main = '')
axis(1, at = log2(ticks), labels = ticks, las = 1, col = dark, col.axis = dark)
text(lg + 0.06, bp, labels = format(as.numeric(tab), big.mark = ','), pos = 4, cex = 0.9, col = dark)
mtext('Gene\u2013RCD associations (log2 scale)', side = 1, line = 2.5, col = dark)
mtext('Associations contributed by each source database', side = 3, line = 1.2, at = grconvertX(0.5, 'ndc', 'user'), adj = 0.5, font = 2, cex = 1.1, col = dark)
mtext('(A)', side = 3, line = 0.8, at = grconvertX(0.02, 'ndc', 'user'), adj = 0, xpd = NA, font = 2, cex = 1.25, col = dark)
bp2 <- barplot(as.numeric(nsd), names.arg = 1:14, col = '#F9E79F', border = dark,
               las = 1, cex.names = 1.05, axes = FALSE, ylim = c(0, 11000),
               main = '')
axis(2, at = seq(0, 10000, 2000), las = 1, col = dark, col.axis = dark)
text(bp2, as.numeric(nsd) + 200, labels = format(as.numeric(nsd), big.mark = ','), cex = 0.9, col = dark)
mtext('Number of sources', side = 1, line = 2.5, col = dark)
mtext('Gene\u2013RCD associations', side = 2, line = 3.2, col = dark)
mtext('Number of source databases per association', side = 3, line = 1.2, at = grconvertX(0.5, 'ndc', 'user'), adj = 0.5, font = 2, cex = 1.1, col = dark)
mtext('(B)', side = 3, line = 0.8, at = grconvertX(0.02, 'ndc', 'user'), adj = 0, xpd = NA, font = 2, cex = 1.25, col = dark)
dev.off()

img <- image_read('tmp_db.png', density = '600x600')
image_write(img, path = paste0(out, '.tiff'), format = 'tiff', compression = 'lzw')
image_write(image_convert(img, format = 'png'), path = paste0(out, '.png'))
file.remove('tmp_db.png')

write.csv(data.frame(source = nms, associations = as.numeric(tab)), paste0(out, '_data.csv'), row.names = FALSE)
cat('saved Figure_S2_database_contribution (2 panels, 600 DPI)\n')
