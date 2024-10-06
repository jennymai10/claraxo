# Step 1: Use an official Node.js runtime as a parent image
FROM node:18.12.1-alpine
RUN mkdir -p /app
COPY ./ /app
# Step 2: Set the working directory in the container
WORKDIR /app
RUN npm install -g npm@9.3.0
RUN npm install -g serve
RUN npm i
RUN npm run build

# Step 3: Expose the port your app will run on
EXPOSE 3000

# Step 4: Run serve when the container launches
CMD ["serve", "-s", "build", "-l", "3000"]
