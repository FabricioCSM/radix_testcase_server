# radix_testcase_server

Sensor Readings API Backend
This project provides a FastAPI-based backend for managing and retrieving sensor data, with endpoints for creating sensor readings, retrieving statistics, and updating sensor values from a CSV file.

### Pre-requisites
Ensure you have the following installed:

 - Docker and Docker Compose
 - Git

* Sample Data:

This backend includes a sample dataset for initial testing.
The data will auto-load into the database on the first startup if the sensor_readings table is empty.

### Run the Docker Containers:

To start the backend server and database using Docker Compose:

`docker compose up --build`

Docker will set up the FastAPI server, database, and any additional services required.

Install Additional Python Dependencies:

- If you need to install dependencies, enter the container:

`docker compose exec api bash`

- Install the lib

`pip install <Lib you want to install>`


### API Endpoints

* After starting the server, access the API documentation at http://localhost:8000/docs.
