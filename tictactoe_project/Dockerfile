FROM python:3.10.13

RUN mkdir -p /app
COPY ./ /app
# Step 2: Set the working directory in the container
WORKDIR /app
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Step 3: Expose the port your app will run on
EXPOSE 8000

CMD [ "make", "all"]