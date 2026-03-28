# FraudSense 🛡️

**FraudSense** is an AI-powered fraud detection system designed to identify and monitor fraudulent transactions in real-time. It leverages advanced Machine Learning models to detect anomalies and provides a comprehensive dashboard for monitoring.

## 🚀 Features

- **Real-time Detection:** Process and analyze transactions as they happen.
- **AI-Powered:** Utilizes Deep Learning models (Autoencoders) for anomaly detection.
- **Monitoring Dashboard:** Interactive React-based UI to visualize fraud trends.
- **Scalable Architecture:** Modular design with a Python Flask backend and Vite-powered frontend.

## 📁 Project Structure

```text
FraudSense/
├── backend/        # Flask API, ML Models, and Logic
├── frontend/       # React (Vite) Dashboard UI
├── data/           # Dataset storage (raw and processed)
├── .gitignore      # Root configuration for excluded files
└── README.md       # Project documentation
```

## 🛠️ Installation & Setup

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Flask server:
   ```bash
   python app.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## 📊 Dataset
This project uses the IEEE-CIS Fraud Detection dataset. Note that large `.csv` and `.pkl` files are excluded from this repository via `.gitignore` to maintain performance.
