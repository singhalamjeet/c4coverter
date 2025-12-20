import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

# Configuration from environment variables
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
CONVERT_TIMEOUT_SEC = int(os.getenv("CONVERT_TIMEOUT_SEC", "120"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

app = FastAPI(title="PDF to DOCX Converter", version="1.0.0")


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


# Mount static files for favicon
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


@app.get("/robots.txt")
async def robots():
    """Serve robots.txt for search engines."""
    robots_path = Path(__file__).parent.parent / "robots.txt"
    return FileResponse(robots_path, media_type="text/plain")


@app.get("/sitemap.xml")
async def sitemap():
    """Serve sitemap.xml for search engines."""
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
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PDF file."
        )
    
    # Read file content and validate size
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_MB}MB."
        )
    
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
                detail="Conversion completed but output file not found."
            )
        
        # Generate output filename
        original_name = file.filename.rsplit('.', 1)[0]
        output_filename = f"{original_name}.docx"
        
        # Return the converted file
        return FileResponse(
            path=docx_path,
            filename=output_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            background=None
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
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


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "service": "pdf2docx"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
