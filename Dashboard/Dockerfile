FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    g++ \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_DATA=/usr/share/gdal

# Get GDAL version and set it for pip install
RUN gdalinfo --version | cut -d' ' -f2 > gdal_version.txt && \
    export GDAL_VERSION=$(cat gdal_version.txt)

# Set working directory
WORKDIR /app

# Create data directory structure and logs directory
RUN mkdir -p data/trips data/shapes data/population data/processed logs

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies with specific versions
RUN pip install --no-cache-dir \
    fiona==1.9.5 \
    pyproj==3.6.1 \
    shapely==2.0.2 \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code and data
COPY src/ ./src/
COPY data/ ./data/

# Expose port
EXPOSE 8050

# Run the dashboard with logging
CMD ["python", "-u", "src/dashboard.py"]
