FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for the app and Playwright browsers.
# We explicitly install the runtime libraries Playwright needs instead of
# relying on `playwright install --with-deps` which may try to install
# packages that aren't available on some ARM-based Debian variants.
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    wget \
    ca-certificates \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    fonts-liberation \
    fonts-unifont \
    fonts-noto-color-emoji \
    libxss1 \
    libxrender1 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgdk-pixbuf-2.0-0 \
    libdrm2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright Python is installed via pip; install browsers separately but
# don't use `--with-deps` (we already installed the system deps above).
RUN NODE_TLS_REJECT_UNAUTHORIZED=0 playwright install chromium

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
