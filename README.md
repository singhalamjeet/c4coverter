# PDF to DOCX Converter

A simple, secure, and production-ready web application that converts PDF files to DOCX format using LibreOffice headless engine. Designed for seamless deployment with Coolify.

## ✨ Features

- 🚀 **Fast Conversion**: Powered by LibreOffice headless engine
- 🎨 **Beautiful UI**: Modern, responsive interface with drag-and-drop support
- 🔒 **Secure**: No file storage, no database, stateless operation
- 📦 **Containerized**: Docker-ready for easy deployment
- ⚙️ **Configurable**: Environment-based settings for limits and timeouts
- 🌐 **Coolify-Ready**: Deploy directly from Git repository

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Conversion Engine**: LibreOffice (soffice)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Deployment**: Docker container
- **Storage**: Temporary files in `/tmp` (auto-cleaned)

## 📋 Requirements

- Docker (for containerized deployment)
- OR: Python 3.11+ and LibreOffice (for local development)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Build the image
docker build -t pdf2docx .

# Run the container
docker run -p 8000:8000 pdf2docx
```

Access the application at `http://localhost:8000`

### Option 2: Local Development

```bash
# Install LibreOffice (Ubuntu/Debian)
sudo apt-get install libreoffice-writer libreoffice-core

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python app/app.py
```

## 🌍 Coolify Deployment

### Step 1: Push to Git

```bash
# Initialize git (if not already done)
git init

# Add remote repository
git remote add origin https://github.com/singhalamjeet/c4coverter.git

# Commit and push
git add .
git commit -m "Initial commit"
git push -u origin main
```

### Step 2: Deploy on Coolify

1. **Create New Resource**
   - Log into your Coolify dashboard
   - Click "New Resource" → "Application"

2. **Configure Source**
   - Select "Public Repository"
   - Enter: `https://github.com/singhalamjeet/c4coverter.git`
   - Branch: `main`

3. **Build Configuration**
   - Build Pack: **Dockerfile**
   - Dockerfile Location: `./Dockerfile`

4. **Environment Variables** (Optional)
   ```
   MAX_UPLOAD_MB=50
   CONVERT_TIMEOUT_SEC=120
   ```

5. **Deploy**
   - Click "Deploy"
   - Coolify will automatically build and deploy your container

6. **Access Your App**
   - Use the generated URL or configure a custom domain

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_UPLOAD_MB` | `50` | Maximum upload file size in MB |
| `CONVERT_TIMEOUT_SEC` | `120` | Conversion timeout in seconds |

### Example with Custom Limits

```bash
docker run -p 8000:8000 \
  -e MAX_UPLOAD_MB=100 \
  -e CONVERT_TIMEOUT_SEC=180 \
  pdf2docx
```

## 📁 Project Structure

```
pdf2docx/
├── app/
│   ├── app.py              # FastAPI application
│   └── templates/
│       └── index.html      # Frontend UI
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── .dockerignore          # Docker build exclusions
└── README.md             # This file
```

## 🔒 Security Considerations

- ✅ No persistent storage
- ✅ No user data retention
- ✅ Files deleted after conversion
- ✅ Runs as non-root user in container
- ✅ Input validation and size limits
- ✅ Timeout protection

### For Public Deployment

Consider adding:
- Rate limiting (e.g., using nginx or Cloudflare)
- Authentication/API keys
- CAPTCHA for abuse prevention
- Resource monitoring

## 🐛 Troubleshooting

### Issue: Conversion fails

- **Check**: LibreOffice is properly installed
- **Solution**: Rebuild Docker image or reinstall LibreOffice

### Issue: Timeout errors

- **Check**: File is too complex or large
- **Solution**: Increase `CONVERT_TIMEOUT_SEC` environment variable

### Issue: Upload fails

- **Check**: File size exceeds limit
- **Solution**: Increase `MAX_UPLOAD_MB` or reduce file size

### Issue: Container won't start

- **Check**: Port 8000 is not already in use
- **Solution**: Use different port: `docker run -p 9000:8000 pdf2docx`

## 📊 Performance Notes

- **Memory**: LibreOffice can use 200-500MB per conversion
- **Recommended**: Single instance deployment
- **Scaling**: Use load balancer with session affinity if needed
- **Processing Time**: Typically 2-10 seconds per PDF (varies with complexity)

## 🔧 API Endpoints

### `GET /`
Serves the HTML upload interface

### `POST /convert`
Converts PDF to DOCX
- **Request**: `multipart/form-data` with PDF file
- **Response**: DOCX file download
- **Errors**: 400 (invalid file), 413 (too large), 504 (timeout), 500 (conversion error)

### `GET /health`
Health check endpoint
- **Response**: `{"status": "ok", "service": "pdf2docx"}`

## 📝 License

This project is open source and available for use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📞 Support

For issues or questions:
- Create an issue on GitHub
- Check troubleshooting section above

---

**Made with ❤️ for seamless PDF to DOCX conversion**
