# ─── Shared RCD modal ────────────────────────────────────────────────────────
# Used by mod_rcd_grid and mod_network to show RCD pathway details.

rcd_normalize <- function(x) {
  x <- tolower(x)
  x <- gsub("_", " ", x)
  x <- gsub("\\s+", " ", x, perl = TRUE)
  trimws(x)
}

rcd_colors <- c(
  "#e74c3c", "#e67e22", "#f39c12", "#2ecc71", "#3498db",
  "#9b59b6", "#1abc9c", "#e91e63", "#00bcd4", "#ff5722",
  "#4caf50", "#ff9800", "#795548", "#607d8b", "#3f51b5",
  "#e74c3c", "#f39c12", "#16a085", "#2980b9", "#27ae60",
  "#d35400", "#c0392b", "#8e44ad", "#cddc39", "#536dfe"
)

#' Show RCD pathway modal. Safe to call from any module.
#' @param rcd_name Character, the pathway name (e.g. "Apoptosis")
#' @param rcd_base_dir Path to "data/RCD modulo"
show_rcd_modal <- function(rcd_name, rcd_base_dir) {

  desc_dir <- file.path(rcd_base_dir, "descricao RCDs")
  fig_dir  <- file.path(rcd_base_dir, "figuras RCDs")

  desc_files <- list.files(desc_dir, pattern = "\\.txt$")
  base_names <- gsub("\\.txt$", "", desc_files)

  # Find matching RCD entry
  bn_norm <- rcd_normalize(rcd_name)
  all_norm <- rcd_normalize(base_names)
  idx <- which(all_norm == bn_norm)[1]

  if (is.na(idx)) {
    showNotification(paste0("RCD pathway '", rcd_name, "' not found."), type = "warning")
    return()
  }

  bn <- base_names[idx]
  color <- rcd_colors[[min(idx, length(rcd_colors))]]

  # Description
  desc_path <- file.path(desc_dir, paste0(bn, ".txt"))
  desc_text <- if (file.exists(desc_path)) {
    txt <- tryCatch(
      paste(readLines(desc_path, warn = FALSE, encoding = "UTF-8"), collapse = "\n"),
      error = function(e) "Description not available."
    )
    if (nchar(trimws(txt)) == 0) "Description not available." else txt
  } else "Description not available."

  # Figure
  fig_files <- list.files(fig_dir, pattern = "\\.png$", ignore.case = TRUE)
  fig_norm <- rcd_normalize(gsub("\\.png$", "", fig_files, ignore.case = TRUE))
  fig_idx <- which(fig_norm == bn_norm)[1]
  fig_src  <- if (!is.na(fig_idx)) paste0("rcd_figs/", fig_files[fig_idx]) else ""

  showModal(modalDialog(
    title = tags$div(tags$strong(bn), style = paste0("color: ", color, ";")),
    size = "l",
    easyClose = TRUE,
    footer = tagList(
      if (nzchar(fig_src)) tags$a(
        href = fig_src,
        download = paste0("RCDome_", bn, "_fig.png"),
        class = "rcd-download-btn",
        "Download PNG"
      ),
      modalButton("Close")
    ),
    tags$p(style = "line-height: 1.7; font-size: 15px;", desc_text),
    if (nzchar(fig_src)) {
      tags$div(
        style = "text-align: center; margin-top: 16px;",
        tags$img(src = fig_src, style = "max-width: 100%; max-height: 450px; border-radius: 8px;"))
    }
  ))
}
