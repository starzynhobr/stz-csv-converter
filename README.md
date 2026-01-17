# STZ CSV Converter

STZ CSV Converter is a desktop tool developed in Python using PySide6 (Qt for Python) and QML designed to process, clean, and convert contact CSV files, preparing them for import into other systems, with a special focus on the Google Contacts format.

## Features

The application provides a graphical interface to streamline CSV conversion, featuring:

- **File Selection**: Allows selection of a generic CRM CSV file and/or a Google Contacts CSV file as input.
- **Output Directory**: Users can choose where the processed files will be saved.
- **Configurable Processing**: Offers various options to customize data processing:
    - **Phone Normalization**: Adds a default IDD (International Direct Dialing) code, removes invalid characters, and standardizes number formats.
    - **Deduplication**: Identifies and merges duplicate contacts based on phone numbers.
    - **Name Enrichment**: Preserves well-formatted names and renames entries that look like phone numbers.
    - **Contact "Explosion"**: Creates multiple contact entries from a single line containing multiple phone numbers.
    - **Column Mapping**: Enables users to specify which columns in the input CSV correspond to fields like `Name`, `Phone`, `IDD`, `Tags`, etc.
- **Data Validation**: Before full processing, the tool performs a quick validation:
    - Displays a preview of how data will be read.
    - Detects potential character encoding issues (mojibake).
    - Shows information about detected columns.
- **Background Execution**: File processing is performed in a separate thread to ensure the UI remains responsive.
- **Execution Modes**:
    - **Dry Run**: Executes the entire processing pipeline without saving output files, allowing users to verify results and logs.
    - **Run**: Processes data and saves the converted CSV files to the output directory.
- **Detailed Reports**: Generates a JSON report upon completion containing statistics, warnings, and a list of "suspicious" contacts that may require manual correction. A summary is also displayed on the screen.

## How to Use (Development)

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the application**:
    ```bash
    python main.py
    ```

## How to Use (Executable Version)

1.  Download the `.zip` file from the latest release.
2.  Extract the file contents to a folder on your computer.
3.  Run the `main.exe` file located inside the `main.dist` folder.

## Project Structure

- `main.py`: Application entry point. Initializes the Qt/QML environment.
- `app/`: Contains the GUI logic.
    - `controller.py`: Main class connecting the QML interface with business logic (backend).
    - `models.py`: Data models to populate lists and tables in the QML interface.
    - `worker.py`: Workers that execute validation and the processing pipeline in separate threads.
- `core/`: Contains the core business logic for data processing.
    - `pipeline.py`: Orchestrates reading, normalization, merging, and writing steps.
    - `io/`: Modules for reading and writing CSV files.
    - `normalize/`: Modules for data normalization (names, phones, etc.).
    - `merge/`: Modules for contact deduplication and merging.
    - `config.py`: Configuration classes.
- `ui/qml/`: QML files defining the user interface.
    - `Main.qml`: Main interface file.
    - `pages/`: Different application screens (pages).
    - `components/`: Reusable interface components.
- `tests/`: Unit tests for business logic.
- `dist/`: Contains the compiled version files (executable).
- `requirements.txt`: Application dependencies.
