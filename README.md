# ENEL POC LLM IDENTIFIER

A Flask application for validating project structures using OpenAI's API.

## Table of Contents

- [Project Description](#project-description)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Endpoints](#endpoints)
- [Project Structure](#project-structure)
- [License](#license)

## Project Description

This Flask application helps in validating structures within different projects. The application allows users to upload photos of structures, and then it utilizes OpenAI's API to validate and analyze these images, providing detailed summaries and validation statuses for the structures.

## Setup Instructions

### Prerequisites

- Python 3.x
- Flask
- OpenAI API Key

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Configuration

1. Copy `.env.example` to `.env` and set your OpenAI API key:
    ```sh
    cp .env.example .env
    ```

    Update `.env` with your OpenAI API key:
    ```
    OPENAI_API_KEY=YOUR_OPENAI_API_KEY
    ```

2. Configure pylint settings by copying `.pylintrc`:
    ```sh
    cp .pylintrc.example .pylintrc
    ```

## Usage

### Running the Application

1. Run the Flask application:
    ```sh
    python main.py
    ```

2. Open your browser and navigate to `http://127.0.0.1:5000/`.

### Endpoints

- **Home** (`/`): Displays a list of projects and allows selection and PDF opening actions.
- **Project Summary** (`/project_summary`): Returns a summary of the project validation status.
- **Select Structure** (`/select_structure`): Allows selection of a structure within a project for validation.
- **Validate Project** (`/validate_project`): Validates all structures within a selected project.
- **Open PDF** (`/open_pdf`): Opens and displays a PDF file related to a project.
- **Upload Photo** (`/upload_photo`): Handles the upload and validation of a photo for a specific structure in a project.
- **Results** (`/results`): Displays the validation results of a structure and handles validation actions.
- **Check Validation Status** (`/check_validation_status`): Checks if there are any unvalidated structures in a project.

## Project Structure

```
ENEL-POC-LLM-IDENTIFIER/
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── utils.py
│   ├── templates/
│   │   ├── home.html
│   │   ├── error.html
│   │   ├── results.html
│   │   ├── select_structure.html
│   │   ├── upload_photo.html
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── images/
│   │   ├── js/
│   │   │   └── script.js
│   │   └── uploads/
│   ├── instance/
│   │   ├── projetos.json
│   │   ├── validation.json
│   │   ├── output.json
│   │   ├── output.txt
│   │   ├── pdfs/
├── .env.example
├── .pylintrc
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
