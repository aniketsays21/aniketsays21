# 🎬 Quick Test Guide - Generate Your First AI Video

## ✅ Prerequisites (Already Done!)
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ PostgreSQL running
- ✅ Redis running

---

## 🚀 Method 1: Using the API (Easiest for Testing)

### Step 1: Open API Documentation
Open in your browser: http://localhost:8000/docs

You'll see interactive Swagger UI with all endpoints!

### Step 2: Test Available Endpoints

#### Get Available Backgrounds
1. Find: `GET /api/backgrounds`
2. Click "Try it out"
3. Click "Execute"
4. See response with background list

#### Get Available Actions
1. Find: `GET /api/actions`
2. Click "Try it out"
3. Click "Execute"
4. See response with action list

### Step 3: Upload a Model Image
1. Find: `POST /api/upload-model`
2. Click "Try it out"
3. Upload a photo of a person
4. Enter a name
5. Click "Execute"
6. Note the `id` in the response (e.g., `"id": 1`)

### Step 4: Generate a Video
1. Find: `POST /api/generate`
2. Click "Try it out"
3. Fill in the JSON:
```json
{
  "model_image_id": 1,
  "background_id": 1,
  "action_id": 1,
  "audio_text": "This product is amazing! You're going to love it!",
  "emotion": "excited",
  "duration": 5.0
}
```
4. Click "Execute"
5. Note the `job_id` in response

### Step 5: Check Video Status
1. Find: `GET /api/video/{job_id}`
2. Click "Try it out"
3. Enter your `job_id`
4. Click "Execute"
5. Status will be:
   - "pending" → Still waiting
   - "processing" → AI is working
   - "completed" → Done! Video URL in response
   - "failed" → Check error_message

---

## 🎨 Method 2: Using the Website

### Step 1: Open the Website
Go to: http://localhost:5173

### Step 2: Follow the Wizard
You'll see 6 steps at the top:
1. Product
2. Model
3. Background
4. Action
5. Voice
6. Generate

### Step 3: Complete Each Step
- Skip Product if you want
- Upload model image
- Choose background
- Select action
- Configure voice and text
- Click "Generate Video"!

---

## 🐛 Troubleshooting

### "Cannot connect to backend"
- Check backend is running: `curl http://localhost:8000`
- Check logs: `tail -f backend/backend.log`

### "No backgrounds/actions available"
- Need to seed database with sample data
- Run: `cd scripts && python seed_data.py`

### "Video generation fails"
**First time:** AI models are downloading automatically!
- Bark (~1.5GB) downloads when first generating voice
- Rembg (~180MB) downloads when first processing image
- Check terminal logs for download progress

### "Video takes too long"
**Normal times:**
- First video: 5-10 minutes (downloading models)
- Subsequent videos: 2-5 minutes
- With GPU: 30 seconds - 2 minutes

---

## 📊 Monitoring Progress

### Watch Backend Logs
```bash
tail -f /home/user/aniketsays21/backend/backend.log
```

You'll see:
- API requests
- Database queries
- AI model loading
- Video generation progress

### Watch Frontend Logs
```bash
tail -f /home/user/aniketsays21/frontend/frontend.log
```

---

## 🎯 Example Test Workflow

### Quick Test (5 minutes):
1. Open http://localhost:8000/docs
2. POST /api/upload-model (upload any photo)
3. GET /api/backgrounds (see what's available)
4. GET /api/actions (see what's available)
5. POST /api/generate (create video)
6. GET /api/video/{job_id} (check status)

### Full Test (with UI):
1. Open http://localhost:5173
2. Click through the 6-step wizard
3. Upload a photo
4. Choose background and action
5. Type your script
6. Generate!

---

## 🎊 Success Indicators

### Backend is Working:
- ✅ Can access http://localhost:8000/docs
- ✅ Swagger UI loads
- ✅ Can execute API requests

### Frontend is Working:
- ✅ Can access http://localhost:5173
- ✅ See "AI UGC Video Platform" header
- ✅ Can navigate through steps

### Database is Working:
- ✅ API requests don't error with database errors
- ✅ Can upload and retrieve data

### Video Generation is Working:
- ✅ Job status changes from "pending" → "processing" → "completed"
- ✅ Video file is created
- ✅ Can download video

---

## 💡 Tips for Best Results

### For Model Images:
- ✅ Use clear, front-facing photos
- ✅ Good lighting
- ✅ Neutral background helps
- ✅ High resolution (512x512 or larger)

### For Voice:
- ✅ Keep text under 100 words
- ✅ Use natural language
- ✅ Choose appropriate emotion
- ✅ 5-10 seconds is ideal duration

### For Actions:
- ✅ Start with simple actions
- ✅ Match action to your content

---

## 🔄 Stopping the Platform

When you're done testing:

```bash
# Stop frontend
kill $(cat /home/user/aniketsays21/frontend/frontend.pid)

# Stop backend
kill $(cat /home/user/aniketsays21/backend/backend.pid)
```

Or just close the terminal windows!

---

## 🚀 Restarting the Platform

Next time you want to use it:

1. Start services:
```bash
sudo service postgresql start
sudo service redis-server start
```

2. Start backend:
```bash
cd /home/user/aniketsays21/backend
source venv/bin/activate
uvicorn api.main:app --reload
```

3. Start frontend (in new terminal):
```bash
cd /home/user/aniketsays21/frontend
npm run dev
```

---

## 📞 Need Help?

Check the logs first:
- Backend: `/home/user/aniketsays21/backend/backend.log`
- Frontend: `/home/user/aniketsays21/frontend/frontend.log`

Most common issues:
1. Services not started (PostgreSQL/Redis)
2. First-time model downloads (be patient!)
3. Missing sample data (run seed script)

---

## 🎉 You're Ready!

Your AI Video Platform is LIVE and ready to create videos!

**Start here:** http://localhost:5173

Happy video creating! 🎬✨
