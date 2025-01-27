# Use the official Node.js image as the base image
FROM node:18

# Set the working directory
WORKDIR /docs

# Install http-server globally
RUN npm install -g http-server

# Copy the docs directory contents into the container
COPY . .

# Expose port 4201
EXPOSE 4201

# Start the http-server
CMD ["http-server", "--port", "4201"]