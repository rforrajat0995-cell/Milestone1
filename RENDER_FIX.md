# Fix Render Port Binding Error

## The Problem

Render shows: "No open ports detected" because it's still using the old start command.

## The Solution

You need to **manually update the Start Command** in Render dashboard.

### Step-by-Step Fix:

1. **Go to your Render Dashboard**
   - Open: https://dashboard.render.com
   - Click on your service (mutual-fund-faq-backend)

2. **Go to Settings Tab**
   - Click "Settings" in the left sidebar

3. **Update Start Command**
   - Scroll down to "Start Command" section
   - **Delete** the current command: `python backend_rag_api.py`
   - **Replace with**: `gunicorn backend_rag_api:app --bind 0.0.0.0:$PORT`
   - Click "Save Changes"

4. **Wait for Redeployment**
   - Render will automatically redeploy
   - Wait 5-10 minutes
   - Check the "Logs" tab to see progress

5. **Verify It's Working**
   - Status should show "Live" (green)
   - Logs should show: "Starting gunicorn" instead of "Running 'python backend_rag_api.py'"
   - Test: `https://your-app.onrender.com/health`

## Why This Happens

Render dashboard settings **override** the Procfile. Even though we updated the Procfile, you need to update the dashboard setting too.

## Alternative: Delete Start Command

If you want Render to use the Procfile automatically:
1. Go to Settings → Start Command
2. **Delete/clear** the start command field (leave it empty)
3. Save
4. Render will now use the Procfile

## Quick Checklist

- [ ] Updated Start Command in Render dashboard
- [ ] Changed to: `gunicorn backend_rag_api:app --bind 0.0.0.0:$PORT`
- [ ] Saved changes
- [ ] Waited for redeployment
- [ ] Status shows "Live"
- [ ] Health endpoint works

