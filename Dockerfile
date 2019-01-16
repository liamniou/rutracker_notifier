# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory to /app
RUN mkdir -p /app/logs
WORKDIR /app/

# Copy the application directory contents into the container at /app
ADD /app/ /app/

# RUN apt-get update
# RUN apt-get install -qy python3
# RUN apt-get install -qy python3-pip
# RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
# RUN python get-pip.py
RUN pip install -r /app/requirements.txt

# Run bot.py when the container launches
CMD ["python", "/app/rutracker_notifier_bot.py", "> /app/logs/bot.py_log"]

