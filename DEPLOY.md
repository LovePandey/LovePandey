# Deploying FP&A Analytics Dashboard to Production

## Option 1: Streamlit Community Cloud (Recommended)

### Prerequisites
- GitHub repo with this code pushed
- Free Streamlit Cloud account at https://share.streamlit.io

### Steps

**1. Push code to GitHub** (already done)

**2. Deploy on Streamlit Cloud**
- Go to https://share.streamlit.io
- Click "New app"
- Select your repo: `LovePandey/LovePandey`
- Branch: `claude/excel-analytics-tool-a9iuL` (or `main` after merge)
- Main file: `app.py`
- Click "Deploy"

**3. Set up password protection**
- In Streamlit Cloud dashboard, go to your app → Settings → Secrets
- Add:
```toml
password = "your-secure-password-here"
```
- Share this password with your org. Everyone uses the same URL + password.

**4. Share the URL**
- Your app will be live at: `https://your-app-name.streamlit.app`
- Share with your finance team

### Streamlit Cloud Limits (Free Tier)
- 1 GB RAM
- Apps sleep after inactivity (wake on visit)
- Public URL (password-protected via the app)

---

## Option 2: Streamlit Teams (Org-wide with SSO)

For enterprise features (SSO/SAML, viewer auth, private apps):
- Upgrade to Streamlit Teams at https://streamlit.io/cloud
- Supports Google, Okta, Azure AD single sign-on
- No password sharing needed — users sign in with corporate email

---

## Option 3: Self-Hosted (Docker)

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Run locally
```bash
docker build -t fpa-dashboard .
docker run -p 8501:8501 fpa-dashboard
```

### Deploy to cloud
- **AWS**: Push to ECR → deploy on ECS Fargate or App Runner
- **GCP**: Push to Artifact Registry → deploy on Cloud Run
- **Azure**: Push to ACR → deploy on Container Apps

---

## Configuration

### Password Protection
Create `.streamlit/secrets.toml` (local) or set in Streamlit Cloud secrets:
```toml
password = "your-secure-password"
```
Remove the `password` key entirely to disable authentication.

### Theme & Upload Limits
Edit `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 50  # MB

[theme]
primaryColor = "#3b82f6"
```

---

## Quick Start (Local Testing)

```bash
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501 in your browser.
