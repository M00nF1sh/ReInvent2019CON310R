FROM python:latest

COPY src/server.py /
CMD ["python", "/server.py"]