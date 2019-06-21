# Use an official Python runtime as a parent image
FROM python:3

WORKDIR /app

COPY ./app/requirements.txt ./

RUN pip install -r requirements.txt

COPY ./app ./

# Run bot.py when the container launches
CMD ["python", "rutracker_notifier_bot.py"]
