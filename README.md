<img width="1920" height="1080" alt="preview" src="https://github.com/user-attachments/assets/1532cdc9-b933-448b-b489-27d4d2af18d4" />
# StageViewer

A lightweight desktop viewer built in Python (`pywebview`) designed to inspect and compare images generated across sequential transformation steps (`.jpg`, `.jpeg`, and `.png`).

## Features

- **Grid Overview:** The first tab displays all images of the current batch simultaneously for quick comparison. Clicking any thumbnail opens that specific phase tab.
- **Detailed Inspection (Zoom & Pan):** Individual tabs support *Zoom In*, *Zoom Out*, *Zoom Window* (rectangle selection), *Zoom Extent* (fit to window), and *Pan* (drag with mouse).
- **Batch Pagination:** Loads images in customizable blocks (default of 10 at a time) with circular navigation forward and backward, preventing high memory usage in large directories.
- **Auto-Refresh:** Monitors the selected folder and automatically reloads images when modified or added on disk, preserving the active tab and zoom level.
- **Smooth Navigation:** Dedicated buttons to move forward/backward between tabs with intelligent horizontal centering.

## How to Run

1. Install the required dependency:
   ```bash
   pip install pywebview

2. Run the application with:
  ```bash
  python visualizador.py
  ```

3. Build Standalone Executable (Windows)
  To bundle the application and the HTML interface into a single .exe file, run:
  ```bash
  pip install pyinstallerpyinstaller --noconfirm --onefile --windowed --name "StageViewer" --add-data "interface.html;." visualizador.py
  ```
The executable will be generated inside the dist/ folder.

License
Distributed under the MIT License. See the LICENSE file for more details.
