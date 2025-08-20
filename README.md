# PDF Text Extractor

A simple web application that extracts text from PDF files using ChatGPT Vision API.

## Features

- Upload PDF files via web interface
- Convert PDF pages to images
- Extract text using ChatGPT Vision (GPT-4V)
- Display extracted text with page markers
- Copy extracted text to clipboard

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API key:**
   - Edit `.env` file and replace `your_openai_api_key_here` with your actual OpenAI API key
   - You can get an API key from: https://platform.openai.com/api-keys

3. **Install poppler (required for pdf2image):**
   - **macOS:** `brew install poppler`
   - **Ubuntu/Debian:** `sudo apt-get install poppler-utils`
   - **Windows:** Download from https://github.com/oschwartz10612/poppler-windows

## Running the Application

```bash
python run.py
```

Then open your browser and go to: http://localhost:8000

## How it Works

1. User uploads a PDF file
2. PDF is converted to images (one per page)
3. Each image is sent to ChatGPT Vision API
4. GPT-4V extracts all text content from each image
5. Results are combined and displayed

## Project Structure

```
pdf_text_extractor/
├── app/
│   ├── main.py              # FastAPI application
│   ├── pdf_converter.py     # PDF to images conversion
│   └── gpt_extractor.py     # ChatGPT Vision integration
├── static/
│   ├── index.html           # Web interface
│   └── style.css            # Styling
├── uploads/                 # Temporary file storage
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── run.py                   # Application runner
```

## Notes

- The application requires an active OpenAI API key
- Processing time depends on the number of pages in the PDF
- GPT-4V API calls have associated costs
- Temporary files are automatically cleaned up after processing