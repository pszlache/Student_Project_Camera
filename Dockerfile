FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app/src
# system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libv4l-dev \
    && rm -rf /var/lib/apt/lists/*

# copy project
COPY . .

# install python deps
RUN pip install --no-cache-dir -r requirements.txt

# folders for runtime data
RUN mkdir -p recordings snapshots logs

# expose flask
EXPOSE 5000

CMD ["python", "main.py"]