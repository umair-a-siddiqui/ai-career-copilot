<div align="center">

  <h1>🚀 AI CAREER COPILOT</h1>
  <p><b>Your Multi-Agent AI Partner for Career Growth & Application Optimization</b></p>

  <p>
    <a href="https://jobjet.streamlit.app/"><img src="https://img.shields.io/badge/Live_Demo-Try_App_Now-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo"></a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit">
    <img src="https://img.shields.io/badge/AI_Agents-Multi--Agent_System-7A00FF?style=flat-square" alt="AI Agents">
    <img src="https://img.shields.io/badge/API_Rotation-3--Key_Fallback-success?style=flat-square" alt="API Safety">
    <img src="https://img.shields.io/github/v/release/umair-a-siddiqui/ai-career-copilot?style=flat-square&color=orange" alt="Release">
  </p>

</div>

---

## 🚀 Interactive Live Demo

> **Try the deployed application right now:**  
> 🔗 [**jobjet.streamlit.app**](https://jobjet.streamlit.app/)

---

## ✨ Key Features

* **📊 Resume Matching & Keyword Gap Analysis:** Evaluates your current resume against job listings to identify missing technical keywords and ATS formatting gaps.
* **🤖 Multi-Agent Feedback Workflow:**
  * **Analyst Agent:** Extracts critical experience parameters and job description requirements.
  * **Tailor Agent:** Restructures resume bullet points to emphasize relevant technical skills.
  * **Interview Prep Agent:** Formulates customized behavioral and technical practice questions based on skill gaps.
* **🛡️ Hackathon Safety & Key Rotation:** Features an automated 3-key API rotation pipeline to prevent rate-limit throttling during high usage.

---

## 🤖 System Architecture & Flow

<details>
<summary><b>🔍 Click to expand multi-agent pipeline workflow</b></summary>

```text
[ User Input: Resume + Job Link ]
               │
               ▼
   ┌──────────────────────┐
   │    Analyst Agent     │ ──► Parses Keywords & Matches ATS Score
   └───────────┬──────────┘
               │
               ▼
   ┌──────────────────────┐
   │     Tailor Agent     │ ──► Optimizes Bullet Points & Skills
   └───────────┬──────────┘
               │
               ▼
   ┌──────────────────────┐
   │ Interview Prep Agent │ ──► Generates Targeted Questions
   └──────────────────────┘
