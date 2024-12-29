# Project Title

## Requirements
- Docker
- Docker Compose

## Setup

To set up and run the project with Docker, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
    ```

2. Build and start the containers:
    ```bash
    docker-compose down && docker-compose up --build
    ```

This will stop any running containers, remove them, rebuild the images, and then start the containers.

## Stopping the containers
To stop the containers, use the following command:
```bash
docker-compose down
