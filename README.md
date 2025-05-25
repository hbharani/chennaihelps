# Disaster Help Platform

## About The Project

The Disaster Help Platform is a web application designed to connect individuals needing assistance with those who can offer help during disaster situations. Users can share their location and specify the type of commodity they are offering (e.g., food, clothing, shelter) or requesting. The platform visualizes these requests and offers on a map, facilitating easier coordination of aid.

This project was originally built with Flask and has been migrated to FastAPI.

## Key Features

*   **Request Help:** Users can submit requests for essential commodities or services.
*   **Offer Help:** Users can list commodities or services they are willing to provide.
*   **Map-Based Visualization:** View help requests and offers geographically on an interactive map.
*   **Detailed Information:** Click on map points to see details of specific requests or offers.

## Technology Stack

*   **Backend:** FastAPI, Python 3
*   **Data Validation:** Pydantic
*   **Database:** MongoDB
*   **ASGI Server:** Uvicorn
*   **Frontend:** HTML, CSS, JavaScript, Google Maps API
*   **Testing:** Pytest

## Prerequisites

Before you begin, ensure you have the following installed:
*   Python 3.8+
*   MongoDB server (running locally or accessible)

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **MongoDB Configuration:**
    *   The application connects to a MongoDB database named `Disaster_Help`.
    *   It uses a collection named `chennai` within this database.
    *   For optimal performance with geospatial queries, ensure a `2dsphere` index is created on the `geometry` field of the `chennai` collection. You can create this index using the MongoDB shell:
        ```mongo
        use Disaster_Help
        db.chennai.createIndex({ "geometry": "2dsphere" })
        ```
        The application might attempt to function without it, but map queries will be inefficient or may not work as expected.

## Running the Application

1.  **Start the development server:**
    ```bash
    python run.py
    ```
    The script `run.py` uses Uvicorn to serve the application. By default, it will be available at `http://192.168.0.3:8000`.
    You can set environment variables `APP_HOST` and `APP_PORT` to change the host and port.

## Running Unit Tests

To run the automated tests, execute the following command from the project root directory:

```bash
pytest
```

## Project Structure (Overview)

*   `main.py`: The main FastAPI application file, including route definitions.
*   `run.py`: Script to start the Uvicorn server.
*   `helpchennai/`: Directory containing core application logic.
    *   `models.py`: Pydantic models for data validation.
    *   `templates/`: HTML templates for the user interface.
    *   `static/`: Static assets (CSS, JavaScript, images).
*   `tests/`: Contains unit tests for the application.
*   `requirements.txt`: Lists Python dependencies.
*   `README.md`: This file.

---
*This README was updated after migrating the application from Flask to FastAPI.*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
