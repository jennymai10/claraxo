# Use an official Python runtime as a parent image
FROM python:3.12.7

# Create a directory to hold the application code inside the container
RUN mkdir -p /app

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./ /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Django will run on
EXPOSE 8000

# Run the necessary Django commands: makemigrations, migrate, and runserver
CMD ["sh", "-c", "python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"]

# # Copy entrypoint script to container root
# COPY entrypoint.sh /app/entrypoint.sh

# # Ensure entrypoint.sh is executable
# RUN chmod +x /app/entrypoint.sh

# # Set the entrypoint
# ENTRYPOINT ["/app/entrypoint.sh"]