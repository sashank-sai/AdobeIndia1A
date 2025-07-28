#!/usr/bin/env python3
"""
Adobe Hackathon 2025 - Challenge 1a: PDF Processing Solution
Rule-based PDF content extraction and JSON generation
"""

import json
import re
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.input_dir = Path("/app/input")
        self.output_dir = Path("/app/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Font size thresholds for classification
        self.title_font_threshold = 16
        self.heading_font_threshold = 14
        self.subheading_font_threshold = 12
        
    def process_all_pdfs(self):
        """Process all PDF files in the input directory"""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing: {pdf_file.name}")
                structured_data = self.extract_pdf_content(pdf_file)
                self.save_json_output(structured_data, pdf_file.stem)
                logger.info(f"Completed: {pdf_file.name}")
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {str(e)}")
                # Create empty output to maintain consistency
                self.save_json_output(self.create_empty_structure(), pdf_file.stem)
    
    def extract_pdf_content(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract structured content from a PDF file"""
        doc = fitz.open(str(pdf_path))
        
        # Initialize structured data
        structured_data = {
            "metadata": {
                "filename": pdf_path.name,
                "total_pages": len(doc),
                "title": "",
                "author": "",
                "subject": "",
                "creator": ""
            },
            "content": {
                "title": "",
                "sections": [],
                "tables": [],
                "figures": [],
                "footnotes": [],
                "references": []
            },
            "statistics": {
                "word_count": 0,
                "paragraph_count": 0,
                "section_count": 0
            }
        }
        
        # Extract metadata
        self.extract_metadata(doc, structured_data["metadata"])
        
        # Process each page
        all_text_blocks = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_blocks = self.extract_page_content(page, page_num + 1)
            all_text_blocks.extend(page_blocks)
        
        # Analyze and structure content
        self.analyze_document_structure(all_text_blocks, structured_data)
        
        # Extract tables and figures
        self.extract_tables_and_figures(doc, structured_data)
        
        # Calculate statistics
        self.calculate_statistics(structured_data)
        
        doc.close()
        return structured_data
    
    def extract_metadata(self, doc, metadata: Dict[str, Any]):
        """Extract PDF metadata"""
        pdf_metadata = doc.metadata
        metadata.update({
            "title": pdf_metadata.get("title", ""),
            "author": pdf_metadata.get("author", ""),
            "subject": pdf_metadata.get("subject", ""),
            "creator": pdf_metadata.get("creator", "")
        })
    
    def extract_page_content(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Extract text blocks from a single page with formatting information"""
        blocks = []
        
        # Get text blocks with formatting
        text_dict = page.get_text("dict")
        
        for block in text_dict["blocks"]:
            if "lines" in block:  # Text block
                block_text = ""
                font_sizes = []
                font_names = []
                
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"]
                        font_sizes.append(span["size"])
                        font_names.append(span["font"])
                    block_text += line_text + " "
                
                if block_text.strip():
                    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
                    primary_font = max(set(font_names), key=font_names.count) if font_names else ""
                    
                    blocks.append({
                        "text": block_text.strip(),
                        "page": page_num,
                        "font_size": avg_font_size,
                        "font_name": primary_font,
                        "bbox": block["bbox"],
                        "type": self.classify_text_block(block_text.strip(), avg_font_size)
                    })
        
        return blocks
    
    def classify_text_block(self, text: str, font_size: float) -> str:
        """Classify text block based on content and formatting"""
        text_lower = text.lower().strip()
        
        # Title detection
        if font_size >= self.title_font_threshold and len(text) < 200:
            return "title"
        
        # Heading detection
        if font_size >= self.heading_font_threshold:
            return "heading"
        
        # Subheading detection
        if font_size >= self.subheading_font_threshold and (
            text.isupper() or 
            re.match(r'^\d+\.?\s+[A-Z]', text) or
            re.match(r'^[A-Z][a-z]+\s*:?\s*$', text)
        ):
            return "subheading"
        
        # Reference detection
        if re.match(r'^\[\d+\]', text) or text_lower.startswith('reference'):
            return "reference"
        
        # Footnote detection
        if re.match(r'^\d+\s+', text) and len(text) < 500:
            return "footnote"
        
        # List item detection
        if re.match(r'^[\•\-\*]\s+', text) or re.match(r'^\d+[\.\)]\s+', text):
            return "list_item"
        
        # Default to paragraph
        return "paragraph"
    
    def analyze_document_structure(self, blocks: List[Dict[str, Any]], structured_data: Dict[str, Any]):
        """Analyze blocks and create document structure"""
        current_section = None
        
        for block in blocks:
            block_type = block["type"]
            text = block["text"]
            
            if block_type == "title" and not structured_data["content"]["title"]:
                structured_data["content"]["title"] = text
                
            elif block_type in ["heading", "subheading"]:
                # Create new section
                current_section = {
                    "heading": text,
                    "level": 1 if block_type == "heading" else 2,
                    "content": [],
                    "subsections": [],
                    "page": block["page"]
                }
                structured_data["content"]["sections"].append(current_section)
                
            elif block_type == "reference":
                structured_data["content"]["references"].append({
                    "text": text,
                    "page": block["page"]
                })
                
            elif block_type == "footnote":
                structured_data["content"]["footnotes"].append({
                    "text": text,
                    "page": block["page"]
                })
                
            elif block_type in ["paragraph", "list_item"]:
                if current_section:
                    current_section["content"].append({
                        "type": block_type,
                        "text": text,
                        "page": block["page"]
                    })
                else:
                    # Create a default section for orphaned content
                    if not structured_data["content"]["sections"]:
                        structured_data["content"]["sections"].append({
                            "heading": "Content",
                            "level": 1,
                            "content": [],
                            "subsections": [],
                            "page": block["page"]
                        })
                        current_section = structured_data["content"]["sections"][-1]
                    
                    current_section["content"].append({
                        "type": block_type,
                        "text": text,
                        "page": block["page"]
                    })
    
    def extract_tables_and_figures(self, doc, structured_data: Dict[str, Any]):
        """Extract tables and figures from the document"""
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Simple table detection based on layout
            tables = self.detect_tables(page, page_num + 1)
            structured_data["content"]["tables"].extend(tables)
            
            # Simple figure detection based on images
            figures = self.detect_figures(page, page_num + 1)
            structured_data["content"]["figures"].extend(figures)
    
    def detect_tables(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Detect tables in the page (simple implementation)"""
        tables = []
        
        # Get text with layout information
        text_dict = page.get_text("dict")
        
        # Look for tabular patterns
        lines_by_y = defaultdict(list)
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    y_coord = round(line["bbox"][1])  # Top y-coordinate
                    line_text = " ".join([span["text"] for span in line["spans"]])
                    if line_text.strip():
                        lines_by_y[y_coord].append({
                            "text": line_text.strip(),
                            "x": line["bbox"][0]
                        })
        
        # Check for table-like structures
        for y_coord, line_items in lines_by_y.items():
            if len(line_items) >= 3:  # Potential table row
                # Sort by x-coordinate
                line_items.sort(key=lambda x: x["x"])
                row_text = " | ".join([item["text"] for item in line_items])
                
                # Simple heuristic: if it looks like a table row
                if len([item for item in line_items if item["text"]]) >= 2:
                    tables.append({
                        "type": "table_row",
                        "content": row_text,
                        "page": page_num,
                        "columns": len(line_items)
                    })
        
        return tables
    
    def detect_figures(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Detect figures/images in the page"""
        figures = []
        
        # Get images from the page
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            figures.append({
                "type": "image",
                "page": page_num,
                "index": img_index,
                "description": f"Figure {len(figures) + 1} on page {page_num}"
            })
        
        return figures
    
    def calculate_statistics(self, structured_data: Dict[str, Any]):
        """Calculate document statistics"""
        word_count = 0
        paragraph_count = 0
        
        # Count words in sections
        for section in structured_data["content"]["sections"]:
            for content_item in section["content"]:
                if content_item["type"] == "paragraph":
                    words = len(content_item["text"].split())
                    word_count += words
                    paragraph_count += 1
                elif content_item["type"] == "list_item":
                    words = len(content_item["text"].split())
                    word_count += words
        
        structured_data["statistics"].update({
            "word_count": word_count,
            "paragraph_count": paragraph_count,
            "section_count": len(structured_data["content"]["sections"])
        })
    
    def create_empty_structure(self) -> Dict[str, Any]:
        """Create empty structure for failed processing"""
        return {
            "metadata": {
                "filename": "",
                "total_pages": 0,
                "title": "",
                "author": "",
                "subject": "",
                "creator": ""
            },
            "content": {
                "title": "",
                "sections": [],
                "tables": [],
                "figures": [],
                "footnotes": [],
                "references": []
            },
            "statistics": {
                "word_count": 0,
                "paragraph_count": 0,
                "section_count": 0
            }
        }
    
    def save_json_output(self, data: Dict[str, Any], filename: str):
        """Save structured data as JSON file"""
        output_file = self.output_dir / f"{filename}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved: {output_file}")
        except Exception as e:
            logger.error(f"Error saving {output_file}: {str(e)}")

def main():
    """Main processing function"""
    logger.info("Starting PDF processing...")
    
    processor = PDFProcessor()
    processor.process_all_pdfs()
    
    logger.info("PDF processing completed!")

if __name__ == "__main__":
    main()