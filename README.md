# FellowGoer

A web app where Go Transit commuters can connect, meet up and grow friendships during their daily commutes.

## What Does It Do?

- Create an account and log in
- Find other commuters on the same Go Transit routes as you
- Chat with fellow commuters to plan meetups
- Browse and save your regular transit routes

## Running Locally

### Step 1: Set up the Backend (Server)

1. Create a file named `.env` in the main folder with this line:
```
SECRET_KEY=<Add a secret key here>
```

2. Open a terminal and run:
```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend will start at `http://localhost:5000`

### Step 2: Set up the Frontend (Website)

1. Open a new terminal and run:
```bash
cd frontend
npm install
npm start
```

The webapp will open at `http://localhost:3000`

