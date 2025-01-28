# Use Node.js image
FROM node:18

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the development server port
EXPOSE 4200
RUN node set-env.js
# Start the Angular development server
CMD ["npm", "run", "start", "--", "--host", "0.0.0.0"]
