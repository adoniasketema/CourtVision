# ☁️ CourtVision Azure Cloud Deployment Guide

This guide details the step-by-step process for deploying the **CourtVision Sports Analytics Pipeline** to Microsoft Azure using your **$100 Azure Student Credit**.

---

## 🏗️ Architectural Overview
To achieve production scalability and speed while conserving credits, we decouple the system into two cloud services:
1. **Backend API (Python + YOLOv8 + FastAPI):** Hosted inside a Docker container on an **Azure Linux Virtual Machine (VM)** or **Azure Container Instances (ACI)** to compute high-speed CV inference.
2. **Frontend UI (Vite + React):** Hosted completely **for Free** on **Azure Static Web Apps** with global CDN distribution.

---

## 🚀 Step 1: Deploying the Backend API (FastAPI)

### Option A: Azure Linux VM (Recommended for $100 Student Credits)
Having full SSH terminal access to an Ubuntu VM gives you complete freedom to monitor GPU usage, inspect logs, and manage Docker containers directly.

1. **Create the VM in Azure Dashboard:**
   * Search for **Virtual Machines** $\rightarrow$ Click **Create** $\rightarrow$ **Azure Virtual Machine**.
   * **Resource Group:** Create a new group named `CourtVision-RG`.
   * **Virtual Machine Name:** `CourtVision-VM`
   * **Region:** Select the closest region to you (e.g., `East US` or `West US`).
   * **Image:** Select **Ubuntu Server 22.04 LTS (x64)**.
   * **Size:**
     * *GPU Best Performance:* Search for **N-Series** (e.g., `Standard_NC4as_T4_v3` powered by NVIDIA T4 GPU).
     * *Multi-Core CPU Alternative (if GPU quota is 0 in region):* Choose **`Standard_F4s_v2`** (4 vCPU compute-optimized) or **`Standard_D4s_v5`**.
   * **Authentication Type:** Choose **SSH public key** or **Password**.
   * **Inbound Port Rules:** Open HTTP (`80`), HTTPS (`443`), and SSH (`22`).

2. **Open Port 8000 for FastAPI:**
   * After the VM deploys, click **Go to resource** $\rightarrow$ select **Networking** on the left menu.
   * Click **Add inbound port rule**:
     * **Destination Port Ranges:** `8000`
     * **Protocol:** `TCP`
     * **Name:** `AllowFastAPI8000`
     * Click **Add**.

3. **SSH Into VM & Launch Server:**
   Open your Mac terminal and connect using the IP address shown on your Azure VM overview:
   ```bash
   ssh username@YOUR_VM_PUBLIC_IP
   ```
   Once connected, run the following command to install Docker, clone your repo, and run the backend container:
   ```bash
   # Update system and install Docker
   sudo apt-get update && sudo apt-get install -y docker.io git
   sudo systemctl enable --now docker

   # Clone your repository (replace with your GitHub repo link!)
   git clone https://github.com/YOUR_GITHUB_USERNAME/Computer-Vision-Project.git
   cd Computer-Vision-Project

   # Build and run the high-performance CourtVision Docker container
   sudo docker build -t courtvision-backend .
   sudo docker run -d --restart always -p 8000:8000 --name api courtvision-backend
   ```
   * 🎉 Your cloud backend API is now completely live at: `http://YOUR_VM_PUBLIC_IP:8000/docs`!

---

### Option B: Deploy directly to Azure Container Instances (No Server Management)
If you do not wish to manage a Linux virtual machine:
1. Push your code to GitHub.
2. In Azure top search bar, search for **Container Registries** $\rightarrow$ Create a registry (e.g., `courtvisioncr`).
3. Under **Popular Solutions** on your Azure Education home screen, click **Deploy a Docker container** $\rightarrow$ Connect your GitHub repo and select Azure Container Instances (ACI). Azure automatically compiles your new `Dockerfile` and launches an isolated endpoint running on cloud processors!

---

## 🌐 Step 2: Deploying the Frontend (React UI) for Free

Now that your API server is alive in the cloud, let's connect your web app using **Azure Static Web Apps** (100% free hosting service):

1. **Update Frontend API Target:**
   * When deploying to production, your React app needs to know where to send video uploads.
   * When starting the production build, set the environment variable pointing to your Azure VM Public IP:
     ```env
     VITE_API_BASE_URL=http://YOUR_VM_PUBLIC_IP:8000
     ```

2. **Deploy on Azure:**
   * Search for **Static Web Apps** in the top Azure search bar $\rightarrow$ Click **Create**.
   * **Name:** `CourtVision-UI`
   * **Plan Type:** Select **Free (For hobby or personal projects)**.
   * **Source:** Select **GitHub** and sign into your GitHub account.
   * **Build Details:**
     * **Repository:** Select your `Computer-Vision-Project` repo.
     * **Build Presets:** Select **Vite** or **React**.
     * **App Location:** `/courtvision-ui`
     * **Output Location:** `dist`
   * Click **Review + Create**!

Within 2 minutes, Azure will provision a global HTTPS SSL domain (e.g., `https://calm-meadow-0a8b9e.azurestaticapps.net`) showcasing your stunning, AI-powered sports analytics application! 🏀⚡
