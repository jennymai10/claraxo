# Use an official Node.js runtime as a parent image
FROM node:18.12.1-alpine
RUN mkdir -p /app
COPY ./ /app
WORKDIR /app

# Install dependencies
RUN npm install -g npm@9.3.0
RUN npm install -g serve
RUN npm i

# Build the React app
RUN npm run build

# Expose port 3000 for the frontend
EXPOSE 3000

# Serve the React app using `serve` with fallback to `index.html` for React Router
CMD ["serve", "-s", "build", "-l", "3000", "--single"]