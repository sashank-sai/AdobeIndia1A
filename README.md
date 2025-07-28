# Adobe India Hackathon 2025 - Challenge 1a

This repository contains a rule-based document intelligence system developed for the Adobe India Hackathon. The solution takes PDF files as input, analyzes their structure and content, and outputs a detailed JSON file for each document, summarizing its metadata, content hierarchy, and key statistics.

The entire process is encapsulated within a Docker container for seamless, dependency-free execution.

## Features

*   **Structural Analysis**: Identifies document elements like titles, headings, paragraphs, and lists using heuristics based on font size and text patterns.
*   **Content Extraction**: Parses and extracts text content, document metadata (title, author), tables, and figures.
*   **Structured Output**: Generates a well-formed JSON object for each PDF, making the extracted data machine-readable and easy to integrate with other systems.
*   **Containerized**: Uses Docker to provide a consistent and isolated runtime environment, simplifying setup and execution.

## How It Works

The core logic resides in `process_pdfs.py`, which utilizes the `PyMuPDF` library. The script processes each PDF page by page:

1.  **Block Extraction**: Text blocks are extracted along with their formatting information, such as font size, font name, and bounding box.
2.  **Block Classification**: Each block is classified as a `title`, `heading`, `paragraph`, `list_item`, etc., using a set of rules based on its formatting and content.
3.  **Structure Assembly**: The classified blocks are organized into a hierarchical structure of sections and subsections.
4.  **Asset Detection**: The script performs simple heuristic-based detection for tables and extracts image information to identify figures.
5.  **JSON Generation**: The final structured data, including metadata and statistics, is serialized into a JSON file.

## Prerequisites

*   Docker must be installed and running on your system.

## Execution Instructions

Follow these steps to process your PDF files.

1.  **Place PDFs in the Input Directory**:
    This container is configured to read PDF files from the `/app/input` directory. When running the `docker` command, you will mount your local `input` directory to this path. Create an `input` directory in the project root and place your PDF files inside it.

2.  **Build the Docker Image**:
    Open a terminal in the project's root directory and run the following command. The `--platform` flag is recommended to ensure compatibility, especially on ARM-based machines like Apple Silicon Macs.

    ```bash
    docker build --platform linux/amd64 -t pdf-processor .
    ```

3.  **Run the Processing Container**:
    Execute the following command to run the container. This will mount your local `input` directory as a read-only volume and your `output` directory as the destination for the JSON files. The `output` directory will be created if it doesn't exist.

    ```bash
    docker run --rm -v "$(pwd)/input":/app/input:ro -v "$(pwd)/output":/app/output --network none pdf-processor
    ```
    *   **Input**: PDF files located in the `input` directory.
    *   **Output**: JSON files will be created in the `output` directory, with each JSON file corresponding to an input PDF.

## Output JSON Structure

Each output JSON file contains three main keys: `metadata`, `content`, and `statistics`.

```json
{
  "metadata": {
    "filename": "file01.pdf",
    "total_pages": 1,
    "title": "Microsoft Word - LTC_CLAIM_FORMS .doc",
    "author": "nicsi",
    "subject": "",
    "creator": "PScript5.dll Version 5.2.2"
  },
  "content": {
    "title": "",
    "sections": [
      {
        "heading": "Content",
        "level": 1,
        "content": [
          {
            "type": "paragraph",
            "text": "Application form for grant of LTC advance",
            "page": 1
          }
        ],
        "subsections": [],
        "page": 1
      }
    ],
    "tables": [
      {
        "type": "table_row",
        "content": "S.No | Name | Age | Relationship",
        "page": 1,
        "columns": 4
      }
    ],
    "figures": [],
    "footnotes": [],
    "references": []
  },
  "statistics": {
    "word_count": 221,
    "paragraph_count": 26,
    "section_count": 1
  }
}
