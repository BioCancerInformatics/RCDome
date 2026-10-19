# Load necessary libraries
library(readxl)
library(writexl)

# Function to append new data to existing Excel file
append_to_excel <- function(new_data, file_path) {
  if (file.exists(file_path)) {
    existing_data <- read_excel(file_path)
    # Ensure columns match
    if (!all(names(existing_data) == names(new_data))) {
      stop("Column names do not match between existing data and new data.")
    }
    combined_data <- rbind(existing_data, new_data)
  } else {
    combined_data <- new_data
  }
  write_xlsx(combined_data, file_path)
}

# Updated Batch 8 Results with an extra column for Cancer_Type
updated_batch_8_results <- data.frame(
  Gene_Symbol = c("MTF1", "GLS", "LIAS", "LIPT1", "PDHA1", "PDHB", "FDX1", "DLD", "DLAT", "CDKN2A"),
  Cancer_Type = c(NA, "Hepatocellular Carcinoma", NA, NA, NA, NA, "Hepatocellular Carcinoma", NA, NA, NA),
  RCD_Involvement = c("no direct evidence", "pro-ferroptosis", "no direct evidence", "no direct evidence", "no direct evidence", "no direct evidence", "pro-ferroptosis", "no direct evidence", "no direct evidence", "no direct evidence"),
  Quote = c("no direct evidence", 
            "Glutaminase 2 (GLS2) regulates glutamine metabolism by binding to P53, decreasing the antioxidant capacity of reduced glutathione and reducing ROS levels, which in turn enhances the tumor-suppressive function of ferroptosis.", 
            "no direct evidence", "no direct evidence", "no direct evidence", "no direct evidence", 
            "FDX1 has been shown to enhance ferroptosis by increasing the availability of ferrous iron, which catalyzes lipid peroxidation.", 
            "no direct evidence", "no direct evidence", "no direct evidence"),
  Document_Title = c(NA, 
                     "Typing and modeling of hepatocellular carcinoma based on disulfidptosis-related amino acid metabolism genes for predicting prognosis and guiding individualized treatment", 
                     NA, NA, NA, NA, 
                     "Targeting the TCA cycle through cuproptosis confers synthetic lethality on ARID1A-deficient hepatocellular carcinoma", 
                     NA, NA, NA),
  Page = c(NA, 2, NA, NA, NA, NA, 10, NA, NA, NA),
  Link = c(NA, 
           "https://myaidrive.com/3DHCPLEsbtU7FcE5PUQ4Yi/Chen-2023-Ty.pdf?pdfPage=2", 
           NA, NA, NA, NA, 
           "https://myaidrive.com/x3fEyJwyQXGWFr3aonJaUL/Xing-2023-Ta.pdf?pdfPage=10", 
           NA, NA, NA)
)

# Path to the existing Excel file
file_path <- "D:/Pré-artigo 5-optosis model/Gene_Implication_Results.xlsx"

# Append new data to the Excel file
append_to_excel(updated_batch_8_results, file_path)
