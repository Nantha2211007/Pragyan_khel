# 🎥 Frame Drop & Frame Merge Detection  
### NextGen Hackathon Submission – 2026

---

## 📌 Overview

This project detects **frame drops** and **frame merges (duplicate frames)** in video streams using a hybrid time-based and motion-based analysis approach.

The system provides:

- Frame-level classification (NORMAL / DROP / MERGE)
- Annotated output video
- CSV export of results
- Motion energy visualization graph
- Clean Flask-based web interface

---

## 🧠 Problem Statement

In video streams, especially compressed or transmitted media, two common issues occur:

1. **Frame Drops** – Missing frames causing time spikes.
2. **Frame Merges** – Duplicate frames inserted during encoding.

Our solution automatically detects these issues and provides visual and numerical evidence.

---

## 🔍 Detection Strategy

### 1️⃣ Frame Drop Detection

We use a two-stage approach:

### A) Time-Based Detection
- Compute the **median frame time gap**
- If:

  gap / median_gap ≥ 1.9  

  → Frame is marked as DROP

- Estimated dropped frames:

  round(ratio) - 1

This method detects missing frames caused by timing irregularities.

---

### B) Motion-Based Fallback (if no time drop detected)

If no time-based drop is found:

1. Compute frame-to-frame motion:
   - Mean absolute pixel difference
2. Apply moving average smoothing (window = 5)
3. Compute deviation:
   |motion - smooth|
4. Use 90th percentile deviation threshold

Frames exceeding threshold are marked as DROP.

---

### 2️⃣ Frame Merge Detection

Frame merges are treated as **duplicate frames**.

We detect merges by:

- Computing pixel difference between consecutive frames
- Adaptive condition:
  - Difference must be extremely small
  - And significantly lower than typical motion level

This prevents false positives in stable videos.

---

## 📊 Motion Visualization

The system generates a motion analysis graph:

- Raw motion curve
- Smoothed motion trend
- Drop spikes highlighted

This improves interpretability and transparency during evaluation.

---

## 🏗️ Project Structure
---
frame_analyzer_v2/
│
├── server.py
├── pipeline.py
├── detector.py
├── loader.py
├── renderer.py
├── requirements.txt
│
├── templates/
│ └── home.html
│
├── static/
│ └── theme.css
## ⚙️ How to Run

### 1️⃣ Install Dependencies
pip install -r requirements.txt
### 2️⃣ Start the Server
python server.py
### 3️⃣ Open in Browser
http://127.0.0.1:5000
Upload a video to begin analysis.

---

## 📁 Output Files

For each video, the system generates:

- `processed_output.mp4` → Annotated video
- `results.csv` → Frame-level classification
- `motion_graph.png` → Motion energy visualization

---

## 🧰 Tech Stack

- Python
- Flask
- OpenCV
- NumPy
- Matplotlib

---

## 🎯 Key Features

✔ Hybrid time + motion drop detection  
✔ Adaptive duplicate merge detection  
✔ Motion energy graph visualization  
✔ CSV export  
✔ Annotated output video  
✔ Clean and explainable logic  

---

## 🚀 Real-World Applications

- Video quality monitoring
- Streaming reliability testing
- Broadcast signal analysis
- Surveillance integrity validation
- Encoding artifact detection

---

## 🏁 Hackathon Focus

The solution prioritizes:

- Simplicity
- Explainability
- Stability across videos
- Real-time usability
- Clear visual feedback

---

## 👨‍💻 Team Submission – NextGen Hackathon 2026

This project was developed as part of the NextGen Hackathon final submission.

---