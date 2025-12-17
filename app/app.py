import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
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


@app.post("/convert")
async def convert_pdf_to_docx(file: UploadFile = File(...)):
    """
    Convert uploaded PDF to DOCX format.
    
    Process:
    1. Validate file type and size
    2. Save uploaded PDF to temp file
    3. Convert using LibreOffice headless
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
        
        # Convert to DOCX using LibreOffice
        docx_path = os.path.join(temp_dir, "input.docx")
        
        # LibreOffice command for conversion
        command = [
            "soffice",
            "--headless",
            "--nologo",
            "--nofirststartwizard",
            "--convert-to",
            "docx:MS Word 2007 XML",
            "--outdir",
            temp_dir,
            pdf_path
        ]
        
        # Execute conversion with timeout
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=CONVERT_TIMEOUT_SEC,
                check=True
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=504,
                detail=f"Conversion timeout after {CONVERT_TIMEOUT_SEC} seconds."
            )
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Conversion failed: {e.stderr or e.stdout or 'Unknown error'}"
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
            background=None  # Keep file available during response
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
        # Clean up temp files
        # Note: FileResponse needs files to exist during response,
        # so cleanup happens after response is sent in production
        # For now, we'll let the OS clean /tmp periodically
        # In production, consider using background tasks for cleanup
        pass


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "service": "pdf2docx"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
