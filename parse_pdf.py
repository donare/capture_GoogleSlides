#!/usr/bin/env python

import sys
import os

from PIL import Image
from fpdf import FPDF
import tempfile

if __name__ == "__main__":
    args = sys.argv

    source_path = args[1]
    destination_file = args[2]

    with tempfile.TemporaryDirectory() as tmp_dir:
        sample_image = Image.open(os.path.join(source_path, os.listdir(source_path)[0]))
        
        pdf = FPDF(unit="pt", format=[sample_image.width, sample_image.height])

        for file_name in os.listdir(source_path):
            pdf.add_page()
            image = Image.open(os.path.join(source_path, file_name))
            
            rgb_image = image.convert("RGB")
            
            tmp_file_path = os.path.join(tmp_dir, file_name.replace("png", "jpg"))

            rgb_image.save(tmp_file_path, "jpeg", quality=90)

            pdf.image(tmp_file_path, 0, 0, image.width, image.height)

        pdf.output(destination_file, "F")
