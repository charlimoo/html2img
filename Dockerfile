FROM python:3.9
WORKDIR /app
COPY app.py .
RUN pip install flask html2image pillow gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
