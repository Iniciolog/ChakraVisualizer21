# Kirlian Platform - Биорезонансная диагностика

## Overview

Kirlian Platform is a specialized biofield analysis and chakra visualization application that processes bioresonance diagnostic data to create visual representations of human energy systems. The platform integrates medical diagnostic reports with spiritual/energetic visualization concepts, offering both 2D and 3D chakra visualizations, organ state mapping, and aura photography capabilities. It's built primarily as a Streamlit web application with an Electron desktop wrapper for cross-platform distribution.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Application Framework
The main application (`main.py`) is built using **Streamlit** for rapid web-based prototyping and user interface development. This choice enables quick iteration and easy deployment while providing interactive data visualization capabilities. The application uses session state management to maintain user data across interactions, including language preferences, view modes, and energy values.

### Data Processing and Analysis
The platform employs a sophisticated diagnostic analysis system (`diagnostic_analyzer.py`) that processes PDF-based medical reports using **PyPDF** for text extraction. The system maps medical parameters from bioresonance diagnostic reports to chakra energy values through predefined parameter-to-chakra mappings. This approach bridges traditional medical diagnostics with alternative energy-based visualizations.

### Visualization Architecture
The application offers multiple visualization modes:
- **2D Chakra Visualization** (`chakra_visualization.py`) using matplotlib for traditional flat representations
- **3D Biofield Visualization** (`chakra_visualization_3d.py`) using Plotly for interactive 3D models with camera controls and dynamic lighting
- **Organ Visualization** (`organs_visualization.py`) that overlays diagnostic data onto anatomical images
- **Aura Photography** (`aura_photo.py`) using OpenCV and PIL for energy field visualization

### Desktop Application Layer
The platform includes an **Electron-based desktop application** (`desktop-app/`) that wraps the Streamlit web interface into a native desktop experience. This hybrid approach maintains the rapid development benefits of Streamlit while providing users with a traditional desktop application experience, complete with custom icons, menus, and proper OS integration.

### Asset Management
The system uses a structured asset organization with separate directories for images, chakra data (`assets/chakra_info.py`), and styling (`styles.css`). The chakra information is centralized in a data structure that supports multilingual content (Russian and English).

### Image Processing Pipeline
Computer vision operations are handled through **OpenCV** for advanced image processing, **PIL** for basic image manipulations, and **matplotlib** for scientific plotting. The aura visualization system applies color transformations based on energy values with brightness correction algorithms to enhance visibility of low-energy states.

## External Dependencies

### Core Python Libraries
- **Streamlit**: Primary web framework for the user interface
- **OpenCV (cv2)**: Computer vision operations for aura photography and image processing
- **Matplotlib**: 2D plotting and scientific visualizations
- **Plotly**: Interactive 3D visualizations with advanced graphics
- **PIL (Pillow)**: Image processing and manipulation
- **NumPy**: Numerical computing and array operations
- **PyPDF**: PDF text extraction for diagnostic report processing

### Desktop Application Dependencies
- **Electron**: Cross-platform desktop application framework
- **Node.js**: Runtime environment for the desktop wrapper
- **electron-builder**: Build toolchain for creating distributable desktop applications

### Visualization and UI Libraries
- **Plotly Graph Objects**: 3D plotting and interactive visualizations
- **Matplotlib Patches**: Custom shapes and annotations for anatomical overlays
- **CSS**: Custom styling for dark theme and mystical aesthetics

### File Format Support
- **JSON**: Session data storage and configuration management
- **PDF**: Medical diagnostic report processing
- **WebP, JPEG, PNG**: Multi-format image support for organs and anatomical references

### Development and Build Tools
The desktop application uses standard Node.js build toolchain with electron-builder for creating platform-specific installers for Windows and macOS, enabling distribution as native applications rather than requiring users to run Python/Streamlit manually.