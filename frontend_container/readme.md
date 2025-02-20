# Frontend container

## Overview

This container is designed to host the frontend of our application. It includes all the necessary dependencies and configurations to run the frontend smoothly.

## Features

- **Streamlit**: A framework for creating interactive web applications using Python.

- **Running Streamlit**: To run the Streamlit application, use the following command:

```sh
streamlit run streamlit_app.py
```
Replace `streamlit_app.py` with the name of your Streamlit application file.

## Getting Started

### Prerequisites

- Docker installed on your machine.

### Installation

1. Navigate to the project directory:
   
    ```sh
    cd frontend_container
    ```
1. Build the Docker image:
   
    ```sh
    docker build -t cap_comparer-frontend .
    ```

### Running the Container

1. Start the container:
    ```sh
    docker run -p 3000:3000 frontend-container
    ```
2. Open your browser and navigate to `http://localhost:3000` to see the application running.

## Development

### Debugging

To debug the application, you can use the next configuration from the `launch.json`

´´´json
        {
            "name": "Streamlit",
            "type": "debugpy",
            "request": "launch",
            "module": "streamlit",
            "console": "integratedTerminal",
            "justMyCode": true,
            "jinja": true,
            "cwd": "${workspaceFolder}/frontend_container/app",
            "args": [
                "run",
                "${workspaceFolder}/frontend_container/app/streamlit_app.py",
            ]
        }
´´´


