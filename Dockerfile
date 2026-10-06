FROM python:3.12-slim
WORKDIR /benchmark
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "python/evaluate.py", "--help"]
