Here’s a clean and well-structured `README.md` for your project that explains the functionality, structure, and installation/setup steps clearly:

---

# 🎵 Reels Music Discovery App

A full-stack mobile app prototype that mimics the TikTok/Instagram Reels experience — designed to let users upload short-form music videos ("Reels"), discover content, and interact with a personalized social feed. Built using **React Native (Expo)** for the frontend and **Flask** for the backend.

---

## 📱 Features

### ✅ Core Functionalities
- **User Authentication** using JWT (JSON Web Tokens)
- **Upload Reels** with caption, genre, and location metadata
- **Scrollable Home Feed** of all uploaded Reels
- **User Profiles** with the list of uploaded content

### 🧠 Backend (Flask)
- JWT-protected API endpoints
- PostgreSQL (AWS RDS) for data persistence
- Secure password hashing via `werkzeug.security`
- SQLAlchemy ORM with migration support
- S3 integration for video uploads & streaming via public URLs

---

## 📁 Project Structure

```
reels-app/
├── frontend/          # React Native app (Expo)
│   ├── App.js
│   ├── ...
│   └── package.json   # Snapshot of node modules
├── backend/           # Flask server
│   ├── app.py
│   ├── routes/
│   ├── models/
│   ├── ...
│   └── requirements.txt
├── README.md
└── ...
```

---

## 🚀 Getting Started

Follow the instructions below to set up both the frontend and backend environments on your local machine.

### 1. Clone the Repository

```bash
git clone [https://github.com/asish-kun/Spotify-Reels-App.git]
cd Spotify-Reels-App
```

---

## ⚙️ Backend Setup (Flask)

### 🔧 Prerequisites

- Python 3.8+
- PostgreSQL (or use AWS RDS instance)
- AWS CLI credentials configured (for S3 access)

### 🔨 Setup Instructions

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Your Flask server should now be running at `http://127.0.0.1:5000`.

---

## 📱 Frontend Setup (React Native with Expo)

### 🔧 Prerequisites

- Node.js and npm
- Expo CLI: Install it globally using `npm install -g expo-cli`
- Expo Go app on your iOS/Android device (for testing)

### 🔨 Setup Instructions

```bash
cd frontend
npm install  # Installs based on package snapshot
npx expo start
```

This will open an Expo Developer Tools window in your browser with a QR code. Scan it using the Expo Go app to launch the app on your phone.

---

## 🛠 Tech Stack

- **Frontend**: React Native (Expo)
- **Backend**: Python Flask
- **Database**: PostgreSQL (AWS RDS)
- **Authentication**: JWT
- **Storage**: Amazon S3
- **ORM**: SQLAlchemy
- **Password Security**: Werkzeug

---

## 🌐 API Overview (Backend)

| Endpoint              | Method | Description                      |
|-----------------------|--------|----------------------------------|
| `/api/auth/login`     | POST   | Login user and return JWT        |
| `/api/auth/register`  | POST   | Register a new user              |
| `/api/posts`          | GET    | Get all Reels                    |
| `/api/posts`          | POST   | Upload a new Reel                |
| `/api/user/<id>`      | GET    | Get user's Reels by user ID      |

---

## 📸 Demo Preview
> Youtube Live Demo Link: https://youtu.be/x62lA0f9a6U
