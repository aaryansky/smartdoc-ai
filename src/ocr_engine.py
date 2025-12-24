import os
import shutil
import easyocr
import fitz  # PyMuPDF
import numpy as np
import subprocess

class OCREngine:
    def __init__(self):
        print("Initializing EasyOCR...")
        # gpu=False ensures stability on standard laptops
        self.reader = easyocr.Reader(['en'], gpu=False)

    def extract_with_paddle(self, file_path):
        """
        Main extraction function. 
        Detects if input is an Image or PDF and handles accordingly.
        """
        print(f"Processing {file_path}...")
        
        # Check file extension
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self._extract_from_pdf(file_path)
        else:
            return self._extract_from_image(file_path)

    def _extract_from_image(self, image_path):
        """Helper for single images"""
        try:
            result = self.reader.readtext(image_path, detail=0, paragraph=True)
            return "\n".join(result) if result else "No text detected."
        except Exception as e:
            return f"Image OCR Error: {str(e)}"

    def _extract_from_pdf(self, pdf_path):
        """Helper for PDFs: Converts pages to images -> OCR"""
        try:
            doc = fitz.open(pdf_path)
            full_text = []
            print(f"PDF has {len(doc)} pages.")

            for page_num, page in enumerate(doc):
                print(f"Scanning Page {page_num + 1}...")
                
                # 1. Render page to image (Zoom 2x for better quality)
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                
                # 2. Convert to bytes for EasyOCR
                img_bytes = pix.tobytes("png")
                
                # 3. Run OCR
                page_text = self.reader.readtext(img_bytes, detail=0, paragraph=True)
                
                # 4. Format Output
                if page_text:
                    full_text.append(f"--- Page {page_num + 1} ---")
                    full_text.extend(page_text)
                    full_text.append("\n") # Add spacing between pages

            doc.close()
            
            if not full_text:
                return "No text detected in PDF."
                
            return "\n".join(full_text)

        except Exception as e:
            return f"PDF Error: {str(e)}"

    def extract_with_chandra(self, image_path, output_root="data/outputs"):
        # Keep existing Chandra code exactly as is
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        target_dir = os.path.join(output_root, base_name)
        if os.path.exists(target_dir): shutil.rmtree(target_dir)
        
        command = f"chandra {image_path} {output_root}"
        
        try:
            subprocess.run(command, shell=True, check=True)
            md_file = os.path.join(target_dir, f"{base_name}.md")
            if os.path.exists(md_file):
                with open(md_file, 'r', encoding='utf-8') as f: return f.read()
            return "Error: Chandra output file not found."
        except Exception as e:
            return f"Error using ChandraOCR: {str(e)}"