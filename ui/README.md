# HEARTSIGHT Frontend

React-based user interface for the HEARTSIGHT AI ECG Analysis system.

## Features

- 📁 **Drag-and-Drop CSV Upload**: Easy file upload for ECG data
- 📊 **ECG Visualization**: Real-time visualization of Lead I and Lead II signals using Recharts
- 🤖 **AI-Powered Predictions**: Get instant ECG classification with confidence scores
- 💬 **Interactive Chat**: Ask follow-up questions about your ECG results using RAG-powered responses
- 🎨 **Modern UI**: Beautiful, responsive design with gradient backgrounds

## Quick Start

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Production Build

```bash
npm run build
```

## Usage

1. **Upload ECG Data**: Drag and drop a CSV file containing ECG signal data (12 channels)
2. **Enter Patient Info** (optional): Add patient age and sex for personalized explanations
3. **View Results**: See the AI prediction, confidence scores, and ECG visualizations
4. **Ask Questions**: Use the chat widget to ask follow-up questions about your results

## Sample Data

Use the `sample_upload_TEST_PATIENT.csv` file in the project root to test the application.

## API Endpoints

The frontend communicates with the following backend endpoints:

- `POST /predict` - ECG signal prediction
- `POST /chat` - Follow-up questions about results

## Technology Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Recharts** - ECG signal visualization
- **Axios** - HTTP client
- **PapaParse** - CSV parsing
