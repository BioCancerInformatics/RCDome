# ─── organ_disease_map.R ──────────────────────────────────────────────────
# Mapa curado órgão ⇄ grupo de doença usando nomes reais do SVG anatômico.

organ_group_map <- data.frame(
  group = c(
    "Cancer","Cancer","Cancer","Cancer","Cancer","Cancer","Cancer","Cancer",
    "Cancer","Cancer","Cancer","Cancer",
    "Neurodegenerative diseases","Neurodegenerative diseases",
    "Cardiovascular diseases","Cardiovascular diseases","Cardiovascular diseases",
    "Cerebrovascular diseases","Cerebrovascular diseases",
    "Infectious diseases","Infectious diseases","Infectious diseases","Infectious diseases",
    "Autoimmune diseases","Autoimmune diseases","Autoimmune diseases","Autoimmune diseases",
    "Chronic inflammatory diseases","Chronic inflammatory diseases",
    "Chronic inflammatory diseases","Chronic inflammatory diseases",
    "Kidney diseases",
    "Liver diseases",
    "Metabolic diseases","Metabolic diseases","Metabolic diseases",
    "Respiratory diseases",
    "Ischemia-reperfusion injury","Ischemia-reperfusion injury",
    "Ischemia-reperfusion injury","Ischemia-reperfusion injury",
    "Muscle diseases",
    "Ocular diseases","Ocular diseases",
    "Hematological diseases","Hematological diseases","Hematological diseases",
    "Developmental diseases","Developmental diseases"
  ),
  organ = c(
    "breast","lung","liver","ovary","colon","stomach","pancreas",
    "thyroid gland","kidney","urinary bladder","uterus","esophagus",
    "brain","nerve",
    "heart","artery","aorta",
    "brain","artery",
    "lung","liver","lymph node","spleen",
    "skin","nerve","thyroid gland","pancreas",
    "colon","stomach","bone","skin",
    "kidney",
    "liver",
    "liver","pancreas","adipose tissue",
    "lung",
    "heart","kidney","liver","brain",
    "skeletal muscle",
    "eye","retina",
    "bone marrow","blood","spleen",
    "placenta","uterus"
  ),
  stringsAsFactors = FALSE
)

normalize_organ <- function(x) {
  x <- tolower(trimws(as.character(x)))
  gsub("\\s+", " ", x)
}

format_organ_label <- function(x) {
  x <- gsub("_", " ", normalize_organ(x), fixed = TRUE)
  tools::toTitleCase(x)
}

organ_group_map$organ <- normalize_organ(organ_group_map$organ)


build_bodymap_data <- function(counts_by_group, anatogram_key, aggregate_fun = sum) {
  counts_df <- data.frame(
    group = names(counts_by_group),
    count = as.numeric(counts_by_group),
    stringsAsFactors = FALSE
  )

  merged <- merge(organ_group_map, counts_df, by = "group", all.x = TRUE)
  merged$count[is.na(merged$count)] <- 0

  agg <- aggregate(count ~ organ, data = merged, FUN = aggregate_fun)

  positive <- merged[merged$count > 0 & !is.na(merged$group), , drop = FALSE]
  if (nrow(positive) > 0) {
    labels <- aggregate(
      group ~ organ,
      data = positive,
      FUN = function(g) paste(unique(g), collapse = ", ")
    )
  } else {
    labels <- data.frame(
      organ = character(0),
      group = character(0),
      stringsAsFactors = FALSE
    )
  }

  out <- merge(agg, labels, by = "organ", all.x = TRUE)
  out$group[is.na(out$group)] <- ""

  # all.x = TRUE mantém todos os órgãos do anatograma, inclusive os sem grupo.
  key <- anatogram_key[, c("organ", "type", "colour")]
  key$organ <- normalize_organ(key$organ)

  plot_df <- merge(key, out, by = "organ", all.x = TRUE, sort = FALSE)
  plot_df$count[is.na(plot_df$count)] <- 0
  plot_df$group[is.na(plot_df$group)] <- ""

  # ponytail: keep only mapped organs, add when more organ-disease links are curated
  visible_organs <- c("aorta", "bone", "brain", "breast", "colon", "esophagus",
                      "heart", "kidney", "liver", "lung", "nerve", "pancreas",
                      "skin", "spleen", "stomach")
  plot_df <- plot_df[plot_df$organ %in% visible_organs, , drop = FALSE]

  names(plot_df)[names(plot_df) == "count"] <- "value"
  names(plot_df)[names(plot_df) == "group"] <- "group_label"

  plot_df$organ_label <- format_organ_label(plot_df$organ)
  plot_df$hover_text <- paste0(
    "<b>", plot_df$organ_label, "</b>",
    "<br>Evidence: ", format(plot_df$value, trim = TRUE, scientific = FALSE),
    ifelse(
      nzchar(plot_df$group_label),
      paste0("<br>Disease groups: ", plot_df$group_label),
      "<br>Disease groups: not mapped"
    )
  )

  plot_df
}


groups_for_organ <- function(organ_name) {
  key <- normalize_organ(organ_name)
  unique(organ_group_map$group[organ_group_map$organ == key])
}


bodymap_colors_for_counts <- function(
  counts_by_group,
  low = "#f7ede2",
  high = "#c2410c",
  default_color = "#e7e5e4"
) {
  counts_df <- data.frame(
    group = names(counts_by_group),
    count = as.numeric(counts_by_group),
    stringsAsFactors = FALSE
  )

  merged <- merge(organ_group_map, counts_df, by = "group", all.x = TRUE)
  merged$count[is.na(merged$count)] <- 0
  agg <- aggregate(count ~ organ, data = merged, FUN = sum)

  max_val <- max(agg$count, 1e-9)
  ramp <- grDevices::colorRamp(c(low, high))
  hex <- apply(
    ramp(pmin(agg$count / max_val, 1)),
    1,
    function(rgb) grDevices::rgb(
      rgb[1], rgb[2], rgb[3], maxColorValue = 255
    )
  )

  colors <- stats::setNames(as.list(hex), agg$organ)

  list(
    colors = colors,
    groupOrgans = unique(organ_group_map$organ),
    defaultColor = default_color
  )
}
