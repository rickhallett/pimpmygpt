# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN flask --app pimpmygpt init-db

# Make port 8000 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV OPENAI_API_KEY=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
ENV OPENAI_ORG=org-arjEfAsu33nzjAa2JdvG9lfS

# Copy the entrypoint script into the container
# COPY entrypoint.sh ./

# Give execute permission to the entrypoint script
# RUN chmod +x ./entrypoint.sh

# ENTRYPOINT [ "./entrypoint.sh" ]

# Run Gunicorn with one worker for simplicity
CMD ["gunicorn", "--workers", "4", "--timeout", "180", "-b", "0.0.0.0:8080", "pimpmygpt:create_app()"]