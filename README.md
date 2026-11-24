# Pure Python Market Report Server (100% Linux Native)

This folder contains a **complete pure Python conversion** of your market data pipeline and 3-page Sheet10 PDF report generator.

---

## 🌟 Why This Exists
- **Zero Windows Dependency**: Does not require Windows COM (`win32com`).
- **Zero Microsoft Excel Dependency**: Generates the exact 3-page report and calculations without needing desktop Microsoft Office.
- **Runs Online 24/7 For Free**: Can be deployed to **Render.com**, **Railway**, **Google Cloud Run**, or any free Linux cloud server so you **never need a physical PC**.

---

## 📁 Files in This Folder

| File | Description |
| :--- | :--- |
| `report_engine.py` | Fetches 30m candles (5 days), computes 16 price levels & indicators, generates 3-page vector PDF |
| `server.py` | Web dashboard & REST API with interactive Stock Dropdown menu |
| `Dockerfile` | Ready-to-deploy Linux Docker container for cloud deployment |
| `requirements.txt` | Lightweight Linux-compatible Python dependencies |
| `run_local_pure_python.bat` | 1-Click batch file to run and test locally |

---

## 🚀 How to Run Locally

Double-click:
`run_local_pure_python.bat`

Then open your browser to:
👉 `http://localhost:8080`

Select your stock from the dropdown and click **"Generate Pure Python Report"**.

---

## ☁️ How to Deploy Online for FREE (No Physical PC Needed)

### Method 1: Render.com (100% Free Web Service)
1. Push this `pure_python_server` folder to a GitHub repository.
2. Sign in to [Render.com](https://render.com) (free).
3. Click **New +** ➔ **Web Service**.
4. Connect your GitHub repository.
5. Choose **Environment: Python 3** (or Docker).
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python server.py`
6. Click **Deploy Web Service**.
7. Render gives you a free HTTPS URL (e.g. `https://my-market-report.onrender.com`) that runs 24/7 in the cloud without needing your computer!

---

### Method 2: Google Cloud Run (Free Tier: 2 Million requests/month)
```bash
gcloud run deploy market-server --source . --allow-unauthenticated
```
