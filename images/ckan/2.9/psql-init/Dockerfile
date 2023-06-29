
# Start with a lightweight base image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /srv

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY psql-init/  .

CMD ["sleep", "1000"]