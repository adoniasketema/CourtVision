# 🚀 100% Free NVIDIA Cloud GPU Setup (Google Colab)

When processing 60 FPS sports videos (600+ frames per clip), running three deep learning vision models on standard CPUs takes several minutes. By leveraging **Google Colab's Free NVIDIA T4 GPUs**, processing time drops down to **$\approx$15–30 seconds**!

Here is how to connect your Mac React Frontend directly to a Free Google Colab GPU supercomputer:

---

## Step 1: Initialize Your Free GPU Machine
1. Visit **[https://colab.research.google.com/](https://colab.research.google.com/)** in your browser and click **+ New Notebook**.
2. In the top navigation menu, click **Runtime $\rightarrow$ Change runtime type**.
3. Under **Hardware accelerator**, select **T4 GPU** and click **Save**.
   *(You now have a dedicated NVIDIA Tensor Core GPU server allocated for free!)*

---

## Step 2: Install Code & Prepare Models
Copy and paste this code block into your first Colab code cell and hit **Play / Run**:

```python
# 1. Download your newly owned GitHub repository
!git clone https://github.com/adoniasketema/CourtVision.git
%cd CourtVision

# 2. Install PyTorch GPU requirements and Cloud Tunnel packages
!apt-get install -y tesseract-ocr
!pip install -q -r requirements.txt
!pip install -q pyngrok uvicorn

print("✅ Repository cloned & dependencies installed!")
```

### 📂 Upload Your AI Models (Takes ~30 seconds):
1. On the far left side of your Google Colab screen, click the **Folder icon** 📁 to open the filesystem.
2. Click into the `CourtVision/models/` folder.
3. From your Mac Finder (`/Users/adoniasketema/Computer-Vision-Project/models`), simply **drag and drop** these three files directly into the Colab `models/` folder:
   * `ball_detector.pt`
   * `court_keypoint_detector.pt`
   * `player_detector.pt`

---

## Step 3: Launch High-Speed Cloud GPU API
In a new code cell in Colab, copy and paste the following Python server execution code:

```python
import os
from pyngrok import ngrok

# 1. Clean up any lingering cloud tunnels from previous cell restarts
ngrok.kill()

# 2. Enter your Free Ngrok Authtoken
NGROK_AUTH_TOKEN = "YOUR_NGROK_AUTH_TOKEN_HERE"
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# 2. Create public cloud tunnel FIRST
public_url = ngrok.connect(8000).public_url
print(
    f"\n🎉 YOUR NVIDIA GPU COURT VISION API IS LIVE AT: {public_url}"
)
print("👉 Paste this URL into your dashboard! Starting interactive server logs below...\n")

# 3. Launch FastAPI Uvicorn Server directly in foreground to view real-time logs!
!uvicorn api:app --host 0.0.0.0 --port 8000 --workers 1
```

---

## Step 4: Experience High-Speed Inference!
Copy the public URL printed in Colab (e.g., `https://a1b2-34-56-78.ngrok-free.app`).

Open your Mac terminal where your UI dev server runs, and launch Vite pointing to your Colab GPU:

```bash
cd /Users/adoniasketema/Computer-Vision-Project/courtvision-ui
VITE_API_BASE_URL="https://YOUR-NGROK-URL.ngrok-free.app" npm run dev
```

Open **http://localhost:5173**, drop in your video clip, and watch thousands of NVIDIA Tensor Cores chew through tracking calculations at blazing speed! 🏀⚡
