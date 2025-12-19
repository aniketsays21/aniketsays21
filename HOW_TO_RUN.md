# 🚀 How to Run the AI UGC Video Platform

**For Complete Beginners - Step by Step Guide**

---

## 🎯 What You Need to Know

Your AI video platform has **3 parts** that need to run together:

| Part | What It Does | Like... |
|------|--------------|---------|
| **Backend** | Handles requests, talks to database | Restaurant kitchen |
| **Frontend** | The website you see | Restaurant dining room |
| **Celery Worker** | Processes videos in background | The chef cooking |

**Important:** You need **3 terminal windows** open at the same time!

---

## 🚦 Starting the Application

### Step 1: Make Sure Services Are Running

Before starting the app, check that PostgreSQL and Redis are running:

```bash
# Check PostgreSQL
pg_isready

# Check Redis
redis-cli ping
```

**Expected output:**
- PostgreSQL: `/var/run/postgresql:5432 - accepting connections`
- Redis: `PONG`

**If they're not running:**
```bash
sudo service postgresql start
sudo service redis-server start
```

---

### Step 2: Open 3 Terminal Windows

Think of it like opening 3 browser tabs - each runs something different!

---

### 📱 Terminal 1: Start the Backend

**What it does:** Runs the API server (the brain)

```bash
# Go to backend folder
cd /home/user/aniketsays21/backend

# Activate virtual environment
source venv/bin/activate

# Start the backend
uvicorn api.main:app --reload
```

**What you'll see:**
```
INFO: Uvicorn running on http://127.0.0.1:8000
🚀 AI UGC Video Platform started in development mode
```

**This means:** ✅ Backend is running!

**Access it at:** http://localhost:8000/docs (API documentation)

---

### 🎨 Terminal 2: Start the Frontend

**What it does:** Runs the website (what you interact with)

```bash
# Go to frontend folder
cd /home/user/aniketsays21/frontend

# Start the website
npm run dev
```

**What you'll see:**
```
  VITE v5.0.8  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**This means:** ✅ Website is running!

**Access it at:** http://localhost:5173

---

### 👨‍🍳 Terminal 3: Start Celery Worker (Optional but Recommended)

**What it does:** Processes video generation in the background

```bash
# Go to backend folder
cd /home/user/aniketsays21/backend

# Activate virtual environment
source venv/bin/activate

# Start Celery worker
celery -A services.worker worker --loglevel=info
```

**What you'll see:**
```
[tasks]
  . services.worker.generate_video

celery@hostname ready.
```

**This means:** ✅ Worker is ready to process videos!

---

## 🎬 Using the Platform

Once all 3 are running:

1. **Open your browser** and go to: http://localhost:5173

2. **You'll see the AI Video Platform website!**

3. **To generate a video:**
   - Upload a model image (photo of a person)
   - Choose a background
   - Select an action
   - Type what you want them to say
   - Click "Generate Video"
   - Wait 2-5 minutes
   - Download your video!

---

## 🛑 Stopping the Application

To stop each service:

1. **Go to each terminal window**
2. **Press:** `Ctrl + C`

This stops that service safely.

---

## 🔄 Restarting the Application

When you restart your computer or close terminals:

1. **Start PostgreSQL and Redis** (if not auto-started)
2. **Follow Step 2** again (open 3 terminals)
3. **Run the commands** in each terminal

---

## 🆘 Troubleshooting

### Problem: "Port already in use"

**What it means:** The service is already running somewhere

**Solution:**
```bash
# Kill the process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill the process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```

---

### Problem: "Database connection error"

**What it means:** PostgreSQL isn't running

**Solution:**
```bash
sudo service postgresql start
```

---

### Problem: "Redis connection error"

**What it means:** Redis isn't running

**Solution:**
```bash
sudo service redis-server start
```

---

### Problem: "ModuleNotFoundError"

**What it means:** Virtual environment isn't activated

**Solution:**
```bash
# Make sure you're in the backend directory
cd /home/user/aniketsays21/backend

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt now
```

---

## 📊 Understanding What's Running

### Backend (Terminal 1)

```
URL: http://localhost:8000
Purpose: Handles API requests
Logs: Shows every request received
```

### Frontend (Terminal 2)

```
URL: http://localhost:5173
Purpose: The website interface
Logs: Shows page loads and builds
```

### Celery Worker (Terminal 3)

```
No URL (runs in background)
Purpose: Generates videos
Logs: Shows video processing progress
```

---

## 🎯 Quick Start Checklist

- [ ] PostgreSQL running?
- [ ] Redis running?
- [ ] Terminal 1: Backend running on port 8000?
- [ ] Terminal 2: Frontend running on port 5173?
- [ ] Terminal 3: Celery worker ready?
- [ ] Browser open to http://localhost:5173?

**If all checked:** ✅ You're ready to generate AI videos!

---

## 💡 Tips for Beginners

1. **Keep all 3 terminals open** while using the app
2. **Don't close terminals** or the services will stop
3. **Watch the logs** - they show what's happening
4. **First video will be slow** - AI models load initially
5. **Subsequent videos will be faster**

---

## 🌟 You Did It!

You've successfully set up and can now run a complete AI-powered video generation platform! That's amazing for someone who says they're a "non-coder"! 🎉

---

## 📞 Need Help?

- **API Documentation:** http://localhost:8000/docs (when backend is running)
- **Check logs in each terminal** for error messages
- **Most issues:** PostgreSQL or Redis not running

**Remember:** You're running professional-grade AI software! Be proud! 🚀
