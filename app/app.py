import os
import tempfile
from pathlib import Path
from typing import Optional, List
import io
import zipfile

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PyPDF2 import PdfWriter, PdfReader
from pdf2image import convert_from_path
from PIL import Image

# Configuration from environment variables
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
CONVERT_TIMEOUT_SEC = int(os.getenv("CONVERT_TIMEOUT_SEC", "120"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
MAX_MERGE_FILES = 10
MAX_MERGE_TOTAL_MB = 100  # Maximum total size for merge operations

app = FastAPI(title="C4Converter - PDF Tools", version="2.0.0")


# Helper function for PDF validation
def validate_pdf_file(file: UploadFile) -> bytes:
    """Validate PDF file type and size."""
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PDF file."
        )
    return file

async def read_and_validate_pdf(file: UploadFile, max_size: int = MAX_UPLOAD_BYTES) -> bytes:
    """Read PDF content and validate size."""
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {max_size // (1024*1024)}MB."
        )
    return content


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML upload page."""
    html_path = Path(__file__).parent / "templates" / "index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/about", response_class=HTMLResponse)
async def about():
    """Serve the about page."""
    html_path = Path(__file__).parent / "templates" / "about.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy():
    """Serve the privacy policy page."""
    html_path = Path(__file__).parent / "templates" / "privacy-policy.html"
    with open(html_path, "r", encoding="utf-8") as f:
       

 return HTMLResponse(content=f.read())


@app.get("/terms", response_class=HTMLResponse)
async def terms():
    """Serve the terms of service page."""
    html_path = Path(__file__).parent / "templates" / "terms.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/how-it-works", response_class=HTMLResponse)
async def how_it_works():
    """Serve the how it works page."""
    html_path = Path(__file__).parent / "templates" / "how-it-works.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/faq", response_class=HTMLResponse)
async def faq():
    """Serve the FAQ page."""
    html_path = Path(__file__).parent / "templates" / "faq.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/contact", response_class=HTMLResponse)
async def contact():
    """Serve the contact page."""
    html_path = Path(__file__).parent / "templates" / "contact.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/robots.txt")
async def robots():
    """Serve robots.txt for SEO."""
    robots_path = Path(__file__).parent.parent / "robots.txt"
    return FileResponse(robots_path, media_type="text/plain")


@app.get("/sitemap.xml")
async def sitemap_xml():
    """Serve sitemap.xml for SEO."""
    sitemap_path = Path(__file__).parent.parent / "sitemap.xml"
    return FileResponse(sitemap_path, media_type="application/xml")

@app.get("/sitemap")
async def sitemap_html(request: Request):
    # For now, serve a simple HTML response or redirect
    # If a templating engine is set up, this would use templates.TemplateResponse
    html_path = Path(__file__).parent / "templates" / "sitemap.html"
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    else:
        # Fallback if sitemap.html doesn't exist yet
        return HTMLResponse(content="<h1>Sitemap HTML Page (Coming Soon)</h1><p>This page will list all available content.</p>")

# SEO Content Pages
@app.get("/how-to-convert-pdf-to-word", response_class=HTMLResponse)
async def how_to_convert():
    """Serve the how-to tutorial page."""
    html_path = Path(__file__).parent / "templates" / "how-to-convert-pdf-to-word.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/is-pdf-conversion-safe", response_class=HTMLResponse)
async def is_safe():
    """Serve the safety guide page."""
    html_path = Path(__file__).parent / "templates" / "is-pdf-conversion-safe.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/pdf-vs-docx", response_class=HTMLResponse)
async def pdf_vs_docx():
    """Serve the format comparison page."""
    html_path = Path(__file__).parent / "templates" / "pdf-vs-docx.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/free-pdf-to-docx", response_class=HTMLResponse)
async def free_converter():
    """Serve the free converter page."""
    html_path = Path(__file__).parent / "templates" / "free-pdf-to-docx.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/pdf-to-docx-converter-online", response_class=HTMLResponse)
async def online_converter():
    """Serve the online converter page."""
    html_path = Path(__file__).parent / "templates" / "pdf-to-docx-converter-online.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/convert")
async def convert_pdf_to_docx(file: UploadFile = File(...)):
    """
    Convert uploaded PDF to DOCX format using pdf2docx library.
    
    Process:
    1. Validate file type and size
    2. Save uploaded PDF to temp file
    3. Convert using pdf2docx Python library
    4. Stream DOCX back to client
    5. Clean up temp files
    """
    
    # Validate file type
    validate_pdf_file(file)
    
    # Read file content and validate size
    content = await read_and_validate_pdf(file)
    
    # Create temporary directory for conversion
    temp_dir = None
    pdf_path = None
    docx_path = None
    
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        
        # Save uploaded PDF
        pdf_path = os.path.join(temp_dir, "input.pdf")
        with open(pdf_path, "wb") as f:
            f.write(content)
        
        # Output DOCX path
        docx_path = os.path.join(temp_dir, "output.docx")
        
        # Convert using pdf2docx library
        try:
            from pdf2docx import Converter
            
            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Conversion failed: {str(e)}"
            )
        
        # Check if DOCX was created
        if not os.path.exists(docx_path):
            raise HTTPException(
                status_code=500,
                detail="Conversion completed but output file was not created."
            )
        
        # Generate output filename
        original_name = file.filename.rsplit('.', 1)[0] if file.filename else "document"
        output_filename = f"{original_name}.docx"
        
        # Return the file
        return FileResponse(
            path=docx_path,
            filename=output_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
    
    finally:
        # Cleanup will happen when OS cleans /tmp
        pass


@app.post("/merge")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    """
    Merge multiple PDF files into a single PDF.
    
    Process:
    1. Validate all files are PDFs
    2. Check file count and total size limits
    3. Merge using PyPDF2
    4. Return merged PDF
    """
    
    # Validate file count
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least 2 PDF files to merge."
        )
    
    if len(files) > MAX_MERGE_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_MERGE_FILES} files allowed for merge."
        )
    
    # Validate and read all files
    pdf_contents = []
    total_size = 0
    
    for file in files:
        validate_pdf_file(file)
        content = await file.read()
        total_size += len(content)
        
        if total_size > MAX_MERGE_TOTAL_MB * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"Total size exceeds {MAX_MERGE_TOTAL_MB}MB limit."
            )
        
        pdf_contents.append(content)
    
    # Merge PDFs
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        merger = PdfWriter()
        
        # Add each PDF to merger
        for i, content in enumerate(pdf_contents):
            pdf_path = os.path.join(temp_dir, f"input_{i}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(content)
            
            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    merger.add_page(page)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error reading PDF file {i+1}: {str(e)}"
                )
        
        # Write merged PDF
        output_path = os.path.join(temp_dir, "merged.pdf")
        with open(output_path, "wb") as output_file:
            merger.write(output_file)
        merger.close()
        
        # Return merged PDF
        return FileResponse(
            path=output_path,
            filename="merged.pdf",
            media_type="application/pdf"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Merge failed: {str(e)}"
        )
    finally:
        pass


@app.post("/split")
async def split_pdf(
    file: UploadFile = File(...),
    pages: str = Form(...)
):
    """
    Split PDF by extracting specific pages.
    
    Process:
    1. Validate PDF file
    2. Parse page range (e.g., "1-5,8,10-12")
    3. Extract specified pages
    4. Return ZIP with split PDFs
    
    Page format examples:
    - "1-5" = pages 1 to 5
    - "1,3,5" = pages 1, 3, and 5
    - "1-5,8,10-12" = pages 1-5, 8, and 10-12
    """
    
    # Validate file
    validate_pdf_file(file)
    content = await read_and_validate_pdf(file)
    
    # Parse page ranges
    try:
        page_numbers = parse_page_ranges(pages)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid page format: {str(e)}"
        )
    
    # Process PDF
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        
        # Save input PDF
        input_path = os.path.join(temp_dir, "input.pdf")
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Read PDF
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        # Validate page numbers
        invalid_pages = [p for p in page_numbers if p < 1 or p > total_pages]
        if invalid_pages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid page numbers: {invalid_pages}. PDF has {total_pages} pages."
            )
        
        # Create ZIP with extracted pages
        zip_path = os.path.join(temp_dir, "split_pages.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for page_num in sorted(page_numbers):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num - 1])  # 0-indexed
               
                page_path = os.path.join(temp_dir, f"page_{page_num}.pdf")
                with open(page_path, "wb") as page_file:
                    writer.write(page_file)
                
                zf.write(page_path, f"page_{page_num}.pdf")
        
        # Return ZIP
        return FileResponse(
            path=zip_path,
            filename="split_pages.zip",
            media_type="application/zip"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Split failed: {str(e)}"
        )
    finally:
        pass


@app.post("/pdf-to-images")
async def pdf_to_images(
    file: UploadFile = File(...),
    format: str = Form("png"),
    dpi: int = Form(200)
):
    """
    Convert PDF pages to images.
    
    Process:
    1. Validate PDF file
    2. Convert each page to image using pdf2image
    3. Return ZIP with all images
    
    Parameters:
    - format: 'png' or 'jpg' (default: png)
    - dpi: Image resolution 72-300 (default: 200)
    """
    
    # Validate parameters
    if format.lower() not in ['png', 'jpg', 'jpeg']:
        raise HTTPException(
            status_code=400,
            detail="Format must be 'png' or 'jpg'."
        )
    
    if dpi < 72 or dpi > 300:
        raise HTTPException(
            status_code=400,
            detail="DPI must be between 72 and 300."
        )
    
    # Validate file
    validate_pdf_file(file)
    content = await read_and_validate_pdf(file)
    
    # Process PDF
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        
        # Save input PDF
        input_path = os.path.join(temp_dir, "input.pdf")
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Convert PDF to images
        try:
            images = convert_from_path(input_path, dpi=dpi)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"PDF to image conversion failed: {str(e)}"
            )
        
        # Create ZIP with images
        zip_path = os.path.join(temp_dir, "pdf_images.zip")
        img_format = 'PNG' if format.lower() == 'png' else 'JPEG'
        file_ext = 'png' if format.lower() == 'png' else 'jpg'
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for i, image in enumerate(images, start=1):
                img_path = os.path.join(temp_dir, f"page_{i}.{file_ext}")
                image.save(img_path, img_format)
                zf.write(img_path, f"page_{i}.{file_ext}")
        
        # Return ZIP
        return FileResponse(
            path=zip_path,
            filename=f"pdf_images.zip",
            media_type="application/zip"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image conversion failed: {str(e)}"
        )
    finally:
        pass


def parse_page_ranges(pages_str: str) -> List[int]:
    """
    Parse page range string into list of page numbers.
    
    Examples:
    - "1-5" → [1, 2, 3, 4, 5]
    - "1,3,5" → [1, 3, 5]
    - "1-3,5,7-9" → [1, 2, 3, 5, 7, 8, 9]
    """
    page_numbers = set()
    parts = pages_str.replace(' ', '').split(',')
    
    for part in parts:
        if '-' in part:
            # Range like "1-5"
            try:
                start, end = part.split('-')
                start_num = int(start)
                end_num = int(end)
                if start_num > end_num:
                    raise ValueError(f"Invalid range: {part}")
                page_numbers.update(range(start_num, end_num + 1))
            except ValueError:
                raise ValueError(f"Invalid range format: {part}")
        else:
            # Single page like "3"
            try:
                page_numbers.add(int(part))
            except ValueError:
                raise ValueError(f"Invalid page number: {part}")
    
    return list(page_numbers)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "service": "c4converter"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
