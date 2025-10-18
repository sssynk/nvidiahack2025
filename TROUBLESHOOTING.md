# 🔧 Troubleshooting Guide

## PDF Upload Issues

### ✅ Current Status

**Backend is now running at:** http://localhost:8000
**Frontend UI at:** http://localhost:3000

The backend has been fixed and is ready to accept PDF uploads!

---

## Common Issues & Solutions

### 1. "Cannot upload PDF" / Upload button not working

**✅ FIXED**: The backend is now running properly.

**Check:**
```bash
# Verify backend is running
curl http://localhost:8000/api/classes
# Should return: {"ok":true,"classes":[]}
```

**If backend is not running:**
```bash
cd /Users/josuediaz/nvidiahack2025
./start_backend.sh
```

---

### 2. Frontend can't connect to backend

**Solution:**
- Make sure backend is running on port 8000
- Frontend expects backend at `http://localhost:8000`
- Check browser console for errors

**Test backend:**
```bash
curl http://localhost:8000/api/classes
```

---

### 3. PDF file type not accepted in UI

**Check:** The UI file upload component should accept `.pdf` files.

**API accepts:** Any file with `.pdf` extension will be processed as a PDF.

**To test directly with API:**
```bash
# First create a test class
curl -X POST http://localhost:8000/api/classes \
  -F "name=Test Class" \
  -F "code=TEST101"

# Then upload a PDF (replace with your actual PDF path)
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/your/file.pdf" \
  -F "class_id=YOUR_CLASS_ID" \
  -F "session_title=Test PDF Upload"
```

---

### 4. "API key required" error

**This happens when:** Trying to upload videos without NVIDIA_API_KEY

**Solution for PDF-only usage:**
- PDFs don't need NVIDIA_API_KEY
- Only OpenAI key is needed (already configured)
- Videos require NVIDIA_API_KEY for transcription

**Current setup:**
- ✅ OpenAI API key: Configured
- ❌ NVIDIA API key: Not set (only needed for videos)
- 📄 PDF uploads: Work without NVIDIA key

---

### 5. UI shows "Upload Session" but nothing happens

**Possible causes:**
1. Backend not running → Start with `./start_backend.sh`
2. Frontend not connected → Check Network tab in browser dev tools
3. File type restriction → Make sure UI accepts .pdf

**Debug steps:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Try uploading a PDF
4. Check if request is sent to `/api/upload`
5. Check response for errors

---

### 6. PDF uploads but shows error

**Check the response for specific error:**

Common errors:
- "No text could be extracted" → PDF is image-based, needs OCR
- "Invalid PDF" → File is corrupted
- "Processing failed" → Check backend logs

**View backend logs:**
Backend is running in terminal - check output for errors.

---

## How to Test PDF Upload

### Method 1: Via UI (http://localhost:3000)

1. **Create a class first:**
   - Click "Create Class"
   - Enter name: "Test Class"
   - Save

2. **Upload a PDF:**
   - Select the class
   - Click upload button
   - Choose any PDF file (slides, document, etc.)
   - Click upload

3. **Check result:**
   - PDF should appear in sessions list
   - Summary should be generated
   - You can ask questions about it

### Method 2: Via API (Terminal)

```bash
# 1. Create a test class
curl -X POST http://localhost:8000/api/classes \
  -F "name=Machine Learning" \
  -F "code=CS229"

# Response will include class_id, use it below

# 2. Upload a PDF
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/Users/josuediaz/Downloads/your-pdf-file.pdf" \
  -F "class_id=YOUR_CLASS_ID_HERE" \
  -F "session_title=Lecture 1 Slides"

# Expected response:
# {
#   "ok": true,
#   "file_type": "pdf",
#   "class_id": "...",
#   "session_id": "...",
#   "title": "Lecture 1 Slides",
#   "num_pages": 25,
#   "summary": "..."
# }
```

---

## Verification Checklist

Run these commands to verify everything is working:

```bash
# 1. Check backend is running
curl http://localhost:8000/api/classes
# ✅ Should return: {"ok":true,"classes":[...]}

# 2. Check frontend is accessible
curl -I http://localhost:3000
# ✅ Should return: 200 OK

# 3. Test PDF module
cd /Users/josuediaz/nvidiahack2025
python3 test_pdf.py
# ✅ Should show: PDF support is ready!

# 4. Test OpenAI integration
python3 test_openai.py
# ✅ Should show: OpenAI integration working successfully!
```

---

## Quick Fixes

### Restart everything fresh:

```bash
# 1. Stop any running processes
pkill -f "uvicorn.*api:app"
pkill -f "next.*dev"

# 2. Start backend
cd /Users/josuediaz/nvidiahack2025
./start_backend.sh

# 3. Start frontend (in new terminal)
cd /Users/josuediaz/nvidiahack2025/ui
npm run dev
```

---

## Current Configuration

- ✅ **Backend**: Running on http://localhost:8000
- ✅ **Frontend**: Running on http://localhost:3000  
- ✅ **LLM Provider**: OpenAI
- ✅ **Model**: gpt-4o-mini
- ✅ **PDF Support**: Enabled
- ⚠️ **Video Support**: Needs NVIDIA_API_KEY

---

## Need More Help?

1. **Check backend logs** in the terminal where you ran `./start_backend.sh`
2. **Check browser console** (F12 → Console tab) for frontend errors
3. **Check network tab** (F12 → Network tab) to see API requests/responses
4. **Test with curl** commands above to isolate frontend vs backend issues

---

## Files to Check

- **Backend code**: `/Users/josuediaz/nvidiahack2025/api.py`
- **PDF module**: `/Users/josuediaz/nvidiahack2025/pdf_reader.py`
- **Integration**: `/Users/josuediaz/nvidiahack2025/integrated_agent.py`
- **Backend script**: `/Users/josuediaz/nvidiahack2025/start_backend.sh`

---

## Success Indicators

When everything works, you should see:
- ✅ Backend terminal shows: `Application startup complete`
- ✅ Frontend loads at http://localhost:3000
- ✅ Can create classes
- ✅ Can upload PDFs
- ✅ PDFs get processed and summarized
- ✅ Can ask questions about PDF content

The backend is **currently running and ready** to accept PDF uploads! 🎉

