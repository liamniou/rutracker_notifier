# Use an official Python runtime as a parent image
FROM python:3
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./ ./
CMD ["python", "main.py"]