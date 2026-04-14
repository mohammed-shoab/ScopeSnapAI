# ── ScopeSnap API — Dockerfile ────────────────────────────────────────────────
# Local dev + Cloud Run compatible
# Build: docker build -t scopesnap-api .

FROM python:3.12-slim

WORKDIR /app

# System deps for WeasyPrint (PDF) + psycopg2 + OpenCV (YOLO requires libGL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (cached layer — only rebuilds if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create uploads directory for local file storage
RUN mkdir -p /app/uploads

# Create models directory — .pkl files come from git (COPY . . above)
# .pt files are downloaded from R2 at container startup via scripts/download_models.py
RUN mkdir -p /app/models

# Make startup script executable
RUN chmod +x /app/scripts/start.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# start.sh runs migrations then starts uvicorn
CMD ["/app/scripts/start.sh"]
