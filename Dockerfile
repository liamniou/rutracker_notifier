# Use an official Python runtime as a parent image
FROM python:3

# Copy the application directory contents into the container at /app
RUN mkdir -p /app

WORKDIR /app

COPY ./app ./

RUN pip install -r requirements.txt

# Run bot.py when the container launches
# CMD ["python", "rutracker_notifier_bot.py"]
CMD ["/bin/sh", "-c", "python rutracker_notifier_bot.py > /app/rutracker_notifier_bot.log 2>&1"]
