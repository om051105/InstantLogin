# 🚀 InstantLogin

**Machine Learning Based Login Failure Detection and Automated Resolution System**

[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

InstantLogin is a robust, highly-scalable backend-focused authentication platform designed to provide a secure and reliable login experience. It goes beyond simple "Invalid username or password" errors by systematically tracking authentication behavior to detect and mitigate malicious activity, account lockouts, and brute-force attacks.

This repository currently contains **Phase 1**, establishing a secure end-to-end authentication infrastructure. Phase 2 will introduce an advanced Machine Learning Module to detect anomalous login behaviors based on the telemetry gathered.

---

## ✨ Features (Phase 1)

### Security & Authentication
- **JWT Authentication**: Highly secure access token and refresh token rotation system.
- **Robust Password Hashing**: Utilizes `bcrypt` for secure credential storage.
- **Dynamic Rate Limiting**: Built-in sliding window rate limiter backed by Redis. Automatically blocks IPs or users after 5 failed attempts per minute.
- **Account Lockouts**: Accounts are automatically locked after successive failed login attempts (Security Events).

### Session & Audit Management
- **Live Session Tracking**: Users can view all active sessions, including IP and device footprint.
- **Session Revocation**: Ability to instantly revoke individual sessions or all active sessions globally.
- **Detailed Audit Trails**: Every login attempt (successful or failed) is stored in the database with rich telemetry (Response time, IP, browser) to feed the future ML model.

### Modern Frontend Experience
- **Glassmorphism UI**: Beautiful, premium dark-mode interface built with React and Tailwind CSS.
- **Real-time Feedback**: Dynamic password strength meters, error badges, and real-time toast notifications.

### Enterprise Infrastructure
- **Containerized Stack**: Entire infrastructure runs natively in Docker.
- **Nginx Reverse Proxy**: Load balances API traffic and securely serves the static frontend.
- **High-Performance Caching**: Redis integration for sub-millisecond rate-limit checks.

---

## 🏗️ Architecture & Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons, Axios
- **Backend API**: Python 3.11, FastAPI, Pydantic, python-jose, passlib
- **Database (Persistence)**: MySQL 8.0, SQLAlchemy (ORM), Alembic
- **Cache (In-memory)**: Redis 7
- **Proxy/Web Server**: Nginx
- **Orchestration**: Docker, Docker Compose

---

## 🚀 Getting Started

Follow these steps to run the complete InstantLogin platform locally on your machine.

### 1. Prerequisites
You must have [Docker](https://www.docker.com/products/docker-desktop/) and Docker Compose installed and **running** on your system.

### 2. Configure Environment
Clone the repository and set up your environment variables:
```bash
git clone https://github.com/om051105/InstantLogin.git
cd InstantLogin
cp .env.example .env
```
*(You can modify the `.env` file to customize passwords and JWT secrets).*

### 3. Build and Start the Platform
Run the following command to orchestrate the MySQL database, Redis cache, FastAPI backend, and React frontend:
```bash
docker-compose up -d --build
```
*Note: The initial build may take a couple of minutes as it downloads the database images and compiles the React application.*

### 4. Access the Application
The Nginx proxy exposes the platform on port **8080** to avoid conflicts with Windows system services.
- **Web Dashboard**: [http://localhost:8080](http://localhost:8080)
- **API Swagger Documentation**: [http://localhost:8080/api/docs](http://localhost:8080/api/docs)
- **API Health Check**: [http://localhost:8080/health](http://localhost:8080/health)

### Demo Account
The database is automatically seeded with an administrator account so you can test the dashboard immediately:
- **Email**: `admin@instantlogin.dev`
- **Password**: `Admin@1234`

---

## 💻 Local Development Setup

If you prefer to run the services individually without Docker (useful for local debugging):

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
The backend includes a comprehensive unit test suite:
```bash
cd backend
pytest tests/
```

---

## 🔮 Roadmap
- [x] **Phase 1**: Core Authentication, Session Management, Infrastructure, UI.
- [ ] **Phase 2**: Machine Learning Module (Anomaly detection, automated unblocking, failure classification).
- [ ] **Phase 3**: Horizontal scaling, CI/CD pipeline, and Kubernetes deployment.
