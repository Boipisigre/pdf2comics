# Technical Specification: PDF to CBZ Conversion Script (AVIF)

## Purpose

This script converts one or more PDF files into CBZ files, converting each page (or image) into AVIF format, with conversion statistics logged.

## Features

- Support for a single PDF file or a directory containing multiple PDFs.
- Convert pages to AVIF images.
- Archive AVIF images as CBZ files.
- Measure processing time for each file.
- Calculate size before and after processing.
- Count the number of pages per document.
- Display a summary table in the console.
- Generate a log file containing statistics (date, size, time, etc.).

## Use

```bash
./pdftocbz <quality> < <width> <height> path_in> <path_out>
```

### Settings

1. **quality** : Integer from 1 to 100, defines AVIF compression quality.
4. **width**: Target image width.
5. **height**: Target height of images.
2. **path_entry** :
   - Single PDF file.
   - Or directory containing PDF files.
3. **output** path:
   - File `.cbz` if input is a file.
   - Directory if input is a folder.


## Processing details

- Pages containing a single image are extracted directly.
- Other pages are rendered as images (via PyMuPDF).
- Resize and convert to AVIF via Wand (ImageMagick).
- AVIF images are added to a ZIP file renamed to `.cbz`.

## Output summary

A table displayed at the end of the script contains :

| File | Pages | Initial size (Kb) | Final size (Kb) | Time (s) |
| ------- | ----- | -------------------- | ------------------ | --------- |

## Log file

- Name: `conversion_stats_YYYYMMDD_HHMMSS.txt`
- Contents: identical to the table displayed, with timestamp at the top.
- Simple text format, UTF-8 encoding.

## Technical requirements

- Python 3
- Libraries :
  - fitz` (PyMuPDF)
  - wand` (ImageMagick bindings)
  - `argparse`, `os`, `time`, `zipfile`, `shutil`, `datetime`

## Error handling

- Check that directories exist.
- Check that the output path is a file or folder, depending on the context.
- Stop with explicit message in case of path or file type problem.

## Example

```bash
./pdftocbz 90 1600 2560 livre.pdf sortie.cbz
./pdftocbz 85 1024 1600 docs/ cbz_output/
```
