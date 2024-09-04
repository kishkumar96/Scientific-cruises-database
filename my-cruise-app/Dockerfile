# Use the latest official Node.js runtime as a parent image
FROM node:latest

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy package.json and yarn.lock to the working directory
COPY package.json yarn.lock ./

# Configure Yarn to ignore SSL certificate issues
RUN yarn config set strict-ssl false

# Install dependencies using Yarn
RUN yarn install

# Copy the rest of the application code to the working directory
COPY . .

# Build the React application
RUN yarn build

# Install a simple HTTP server to serve the static files
RUN yarn global add serve

# Expose port 3000
EXPOSE 3000

# Command to run the application
CMD ["serve", "-s", "build"]
