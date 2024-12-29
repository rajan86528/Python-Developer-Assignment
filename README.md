# Python Developer Assignment

This repository contains a project for the Python Developer assignment. It is set up with Docker and Docker Compose for easy deployment.

## Requirements
- Docker
- Docker Compose

## Setup

To set up and run the project using Docker Compose, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/rajan86528/Python-Developer-Assignment.git
    cd Python-Developer-Assignment
    ```

2. Build and start the containers:
    ```bash
    docker-compose down && docker-compose up --build
    ```

    This command will:
    - Stop any running containers (`docker-compose down`).
    - Build the Docker images (`docker-compose up --build`).
    - Start the containers for the project.

## Stopping the Containers
To stop the containers, use the following command:
```bash
docker-compose down
