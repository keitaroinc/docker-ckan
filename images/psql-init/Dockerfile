
# Start with a lightweight base image
FROM python:3.9-alpine

# Used by Github Actions to tag the image with
ENV IMAGE_TAG=0.0.1

# Set the working directory in the container
WORKDIR /srv

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY psql-init/  .

CMD ["python", "/srv/psql-init.py"]

