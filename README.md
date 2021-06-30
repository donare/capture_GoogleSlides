# About
The goal of this repository is to save Google Slide Presentations, even if they were set as unavailable for download. This is done by taking screenshots or downloading the svg content.
  
# Output
![sc](https://user-images.githubusercontent.com/58103830/85630159-29331600-b6ae-11ea-8517-de937caa8d38.png)

# Capturing slides as images

use `python capture_private_gslide.py <gslide_url> <save_folder>`.

This will capture svg and png images of the slides at `gslide_url`.

# Converting images to pdf

Execute `python parse_pdf.py <source_path> <destination_file>`.

The images in <source_path> need to be raster images in a format supported by PIL.

# Using OCR

For OCR, using [OCRmyPDF](https://github.com/jbarlow83/OCRmyPDF) ist recommended. Install according their instructions and use to convert the previously generated pdf.
