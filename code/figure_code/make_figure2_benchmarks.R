# RCDome benchmark figure — Helvetica + pastel palette, A4 portrait, 600 DPI
# 3 panels in EXECUTION ORDER: DeepSeek (Phase 2) -> Elicit (Phase 3) -> Consensus (Phase 2G)
library(magick)

palegreen   <- "#98FB98"
lightsalmon <- "#FFA07A"
dark        <- "#1F2937"

# ---- Panel A: DeepSeek model selection (26-pair ground truth) ----
arms_a <- c("deepseek-chat", "deepseek-reasoner", "tool-call loop\n+ reference", "self-provided\nCoT loop")
acc_a  <- c(81, 73, 100, 100)
fp_a   <- c(38, 25, 0, 0)

# ---- Panel B: Elicit post-export governance (784 records, 3 forms) ----
metrics_b <- c("Allow-list\ncompliance", "Unsupported EXECUTOR\nrate", "Traceability\n(PMID → DOI)")
before_b  <- c(75.4, 53, 24)
after_b   <- c(100, 0, 98)

# ---- Panel C: Consensus query formulation (26-pair ground truth) ----
arms_c <- c("form-biased query", "neutral query")
acc_c  <- c(92, 100)
fp_c   <- c(12, 0)

draw_panel <- function(arms, s1, s2, title, note, col1, col2, leg1, leg2, leg_title, panel_label) {
  m <- rbind(s1, s2)
  bp <- barplot(m, beside = TRUE, col = c(col1, col2), border = dark,
                ylim = c(0, 145), yaxt = "n", axes = FALSE)
  # panel label pinned a few mm inside the LEFT figure border (title stays centered)
  mtext(panel_label, side = 3, line = 0.8, at = grconvertX(0.02, 'ndc', 'user'), adj = 0, xpd = NA, font = 2, cex = 1.25, col = dark)
  mtext(title, side = 3, line = 0.8, adj = 0.5, font = 2, cex = 0.9, col = dark)
  axis(2, at = seq(0, 100, 20), las = 1, col = dark, col.axis = dark)
  axis(1, at = colMeans(bp), labels = arms, tick = FALSE, line = 0,
       col.axis = dark, cex.axis = 0.95, padj = 0.5)
  # percentage values: inside bars (white) for tall bars, above (dark) for short bars — never touches the legend
  place_vals <- function(x, v) {
    hi <- v >= 15
    if (any(hi))  text(x[hi],  v[hi] - 6, labels = paste0(v[hi],  "%"), cex = 0.8, font = 2, col = dark)
    if (any(!hi)) text(x[!hi], v[!hi] + 4, labels = paste0(v[!hi], "%"), cex = 0.8, font = 2, col = dark)
  }
  place_vals(bp[1, ], s1)
  place_vals(bp[2, ], s2)
  mtext("Percent (%)", side = 2, line = 3, cex = 0.9, col = dark)
  mtext(note, side = 1, line = 4.2, cex = 0.68, col = dark)
  legend("topleft", legend = c(leg1, leg2), fill = c(col1, col2),
         border = dark, bty = "n", cex = 0.85, text.col = dark, inset = 0.02,
         title = leg_title, title.col = dark)
}

out <- "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures_A4/Figure_2_benchmarks_A4"

# ---- vector PDF ----
pdf(paste0(out, ".pdf"), width = 8.27, height = 11.69, family = "Helvetica")
par(mfrow = c(3, 1), mar = c(5.2, 4.2, 3.6, 1.5), family = "Helvetica", cex = 1.0)
draw_panel(arms_a, acc_a, fp_a,
           "DeepSeek model-selection benchmark (26-pair ground truth)",
           "18 positive executor/regulator pairs + 8 form-mismatch negative controls (Supplementary Note S5)",
           palegreen, lightsalmon, "Combined accuracy", "False positives", "Metric", "(A)")
draw_panel(metrics_b, before_b, after_b,
           "Elicit post-export governance benchmark (784 records, 3 forms)",
           "192 EXECUTOR\u2192REGULATOR downgrades; all five governance gates passed (Table S14)",
           lightsalmon, palegreen, "Before governance", "After governance", "Elicit", "(B)")
draw_panel(arms_c, acc_c, fp_c,
           "Consensus query-formulation benchmark (26-pair ground truth)",
           "Neutral query (\u201cgene cell death\u201d) removes form-name priming (Supplementary Note S3)",
           palegreen, lightsalmon, "Combined accuracy", "False positives", "Metric", "(C)")
dev.off()

# ---- 600-DPI TIFF ----
png("benchmark_tmp.png", width = 8.27, height = 11.69, units = "in", res = 600)
par(mfrow = c(3, 1), mar = c(5.2, 4.2, 3.6, 1.5), family = "Helvetica", cex = 1.0)
draw_panel(arms_a, acc_a, fp_a,
           "DeepSeek model-selection benchmark (26-pair ground truth)",
           "18 positive executor/regulator pairs + 8 form-mismatch negative controls (Supplementary Note S5)",
           palegreen, lightsalmon, "Combined accuracy", "False positives", "Metric", "(A)")
draw_panel(metrics_b, before_b, after_b,
           "Elicit post-export governance benchmark (784 records, 3 forms)",
           "192 EXECUTOR\u2192REGULATOR downgrades; all five governance gates passed (Table S14)",
           lightsalmon, palegreen, "Before governance", "After governance", "Elicit", "(B)")
draw_panel(arms_c, acc_c, fp_c,
           "Consensus query-formulation benchmark (26-pair ground truth)",
           "Neutral query (\u201cgene cell death\u201d) removes form-name priming (Supplementary Note S3)",
           palegreen, lightsalmon, "Combined accuracy", "False positives", "Metric", "(C)")
dev.off()

img <- image_read("benchmark_tmp.png", density = "600x600")
image_write(img, path = paste0(out, ".tiff"), format = "tiff", compression = "lzw")
image_write(image_convert(img, format = "png"), path = paste0(out, ".png"))
file.remove("benchmark_tmp.png")

cat("saved Figure_2_benchmarks.tiff/.pdf/.png (3 panels, A/B/C labels)\n")
