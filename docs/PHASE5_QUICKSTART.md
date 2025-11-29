# Phase 5: Quick Start Guide

## 🚀 Getting Started with the HEARTSIGHT Website

### Prerequisites
- ✅ Backend API running (Phase 1 & 2 complete)
- ✅ Node.js 18+ installed
- ✅ Dependencies installed (`npm install` in `ui/` directory)

### Step 1: Start the Backend API

```bash
python manage.py dev
```

The API will be available at `http://localhost:8000`

### Step 2: Start the Frontend

In a **new terminal window**:

```bash
python manage.py ui
```

OR manually:

```bash
cd ui
npm run dev
```

The website will be available at `http://localhost:3000`

### Step 3: Test with Sample Data

1. Open `http://localhost:3000` in your browser
2. You should see the HEARTSIGHT upload interface
3. Drag and drop `sample_upload_TEST_PATIENT.csv` (from project root) onto the upload area
4. Optionally enter patient age and sex
5. Click or wait for automatic processing
6. View the results:
   - ECG visualization (Lead I and Lead II)
   - AI prediction with confidence
   - AI-generated explanation
   - Interactive chat widget

### Step 4: Test the Chat Feature

1. After getting results, scroll to the chat widget
2. Ask questions like:
   - "What lifestyle changes should I make?"
   - "What does this condition mean?"
   - "What should I do next?"

## 🎯 What to Expect

### Upload Section
- Drag-and-drop CSV file upload
- Patient metadata input (age, sex)
- Loading indicators

### Visualization Section
- Two charts showing Lead I and Lead II signals
- Time-series plots with proper scaling

### Prediction Section
- Diagnosis badge (color-coded)
- Confidence bar
- Class probabilities breakdown
- AI explanation

### Chat Section
- Interactive chat interface
- Context-aware responses
- Typing indicators

## 🐛 Troubleshooting

### Frontend won't start
- Check Node.js is installed: `node --version`
- Install dependencies: `cd ui && npm install`
- Check port 3000 is available

### API connection errors
- Ensure backend is running on port 8000
- Check CORS is configured (already done)
- Verify `.env` file has `HUGGINGFACEHUB_API_TOKEN`

### CSV upload fails
- Ensure CSV has 12 channel columns
- Check CSV format matches PTB-XL structure
- Verify file is not corrupted

### Chat not working
- Check backend `/chat` endpoint is accessible
- Verify RAG engine is initialized
- Check browser console for errors

## ✅ Verification Checklist

- [ ] Backend API running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can upload CSV file
- [ ] ECG visualization displays
- [ ] Prediction results show
- [ ] Chat widget responds

## 🎉 Success!

If all steps work, Phase 5 is complete! You now have a fully functional web interface for ECG analysis.
