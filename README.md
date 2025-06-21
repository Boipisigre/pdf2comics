# PDF to CBZ Converter (AVIF)

This Python script converts one or multiple PDF files into CBZ archives using AVIF image format for comic book file size optimization.

## Features

- Support for single PDF file or directory of PDFs
- Page/image conversion to AVIF
- CBZ archive generation
- Execution time tracking
- Input/output size reporting
- Page count analysis
- Summary table displayed in terminal
- Log file generation with timestamp

## Requirements

- Python 3
- Dependencies (see `requirements.txt`)
- ImageMagick installed (required for `wand`)

## Installation

```bash
pip install -r requirements.txt
```

Make sure ImageMagick is installed and accessible via command line (e.g., `convert`, `magick`).

## Usage

### Single PDF File

```bash
./pdftocbz <quality> <width> <height> <input.pdf> <output.cbz>
```

### Directory of PDFs

```bash
./pdftocbz <quality>  <width> <height> <input_folder> <output_folder>
```

### Example

```bash
./pdftocbz 50  1600 2560 book.pdf output.cbz
./pdftocbz 60  1024 1600 books/ cbz_output/
```

## Output

- `.cbz` file for each PDF
- A log file `conversion_stats_YYYYMMDD_HHMMSS.txt` with:
  - File name
  - Page count
  - Input/output size
  - Conversion time

## License

MIT License
