FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV  GOOGLE_API_KEY="AIzaSyC3aexAD7EKh5_Op5UXSq3uH38hcl7gFgA"
ENV GOOGLE_GENAI_USE_VERTEXAI=FALSE

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

