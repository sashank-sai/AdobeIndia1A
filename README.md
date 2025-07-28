# Adobe India Hackathon 2025 - Challenge 1b

This project implements a persona-driven document intelligence system for Challenge 1b of the Adobe India Hackathon 2025, aligning with the theme "Connect What Matters — For the User Who Matters." It processes PDF collections to extract and prioritize sections based on user personas and tasks, producing structured JSON outputs.

## Prerequisites

* Docker installed on your system.
* Input directory containing collection folders (Collection 1, Collection 2, Collection 3) with PDFs subdirectories and challenge1b_input.json.
* Output directory (output) for JSON results.

## Execution Instructions

1. **Build the Docker image**:

```bash
docker build --platform linux/amd64 -t challenge1b-processor .
```

2. **Run the container**:

```bash
docker run --rm -v $(pwd):/app/input:ro -v $(pwd)/output:/app/output --network none challenge1b-processor
```

   * **Input**: Collection directories (Collection 1, Collection 2, Collection 3) with PDFs subdirectories and challenge1b_input.json in the project root.
   * **Output**: JSON files (Collection 1_challenge1b_output.json, Collection 2_challenge1b_output.json, Collection 3_challenge1b_output.json) in the output directory.

## Notes

* The Docker image is ~720MB and runs on CPU only, meeting the <1GB constraint.
* Processing completes in ~10 seconds for 31 PDFs, satisfying the ≤60-second requirement for 3-5 documents.
* The --network none flag ensures offline operation.
* Ensure the output directory exists before running the container.
