# Jason Mitchell - Portfolio Website

A modern, responsive portfolio website showcasing my work as a Software Engineer — Inventory Planning & Replenishment, PDF Automation, and DevOps.

## 🔗 Live Site

**[jason0960.github.io/MitchellSoftware](https://jason0960.github.io/MitchellSoftware/)**

## 🪵 Lumber Yard Restock Planner — Interactive Demo

**[Live Demo →](https://lumber-yard-restock-planner.onrender.com)**

A 3D interactive lumber yard demo built to showcase PDF automation and full-stack engineering skills.

**What it does:**
- Browse a 3D lumber yard with 20 product bunks across 4 categories (Dimensional, Sheet, Treated, Specialty)
- Each bunk shows real-time fill level — click to flag low-stock bunks for restocking
- Generate a professional PDF delivery order with a **3D-rendered flatbed truck diagram** showing how bunks are loaded (bin-packed) onto the trailer
- PDF includes line items, pricing, weight totals, yard health chart, and the truck render

**Tech stack:**
- **Frontend**: Three.js (r128) for 3D rendering + OrbitControls
- **Backend**: Python / Flask + ReportLab for PDF generation
- **3D Truck Diagram**: Offscreen Three.js renderer → PNG → embedded in PDF
- **Algorithm**: First-fit decreasing bin-packing for optimal flatbed loading

### Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```
Then open `http://localhost:5000`

## 🚀 Features

- **Creative / Professional Mode Toggle**: Switch between a dark terminal-themed creative layout and a clean light professional layout — state managed via JavaScript with localStorage persistence
- **Responsive Design**: Fully responsive layout that works on desktop, tablet, and mobile devices
- **Career Timeline**: Progression from OMOW Bootcamp → Internship → Full-Time SWE
- **Work Contributions**: Enterprise applications, PDF automation, deployment workflows, monitoring, production bug fixes, and KTLO
- **Tech Stack Grid**: Backend, Frontend, DevOps & CI/CD, Observability & Tools
- **Interactive Elements**: Typing effect, cursor glow, smooth scrolling, scroll-triggered animations, mobile navigation
- **Contact Form**: With success feedback

## 🛠️ Technologies Used

- HTML5
- CSS3 (Custom properties, Grid, Flexbox)
- JavaScript (ES6+ — state/props architecture)
- Font Awesome icons
- Google Fonts (JetBrains Mono, Inter)
- GitHub Actions (deployment)

## 📂 Project Structure

```
MitchellSoftware/
├── index.html                      # Portfolio — main HTML
├── styles.css                      # Portfolio — stylesheet (creative + professional themes)
├── script.js                       # Portfolio — JavaScript (AppState manager, renderers)
├── pallet-builder.html             # Restock Planner — page
├── pallet-builder.js               # Restock Planner — Three.js 3D app + PDF logic
├── pallet-builder.css              # Restock Planner — dark theme styles
├── server.py                       # Flask server — static files + PDF endpoint
├── requirements.txt                # Python dependencies (Flask, ReportLab, flask-cors)
├── render.yaml                     # Render.com deployment config
├── .github/workflows/deploy.yml    # GitHub Pages deployment workflow
├── DEPLOYMENT.md                   # Deployment guide
└── README.md                       # This file
```

## 🖥️ Run Locally

```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx http-server

# Or just open the file directly
open index.html
```

Then navigate to `http://localhost:8000` in your browser.

## 📧 Contact

- **Email**: [jasonmitchell096@gmail.com](mailto:jasonmitchell096@gmail.com)
- **LinkedIn**: [linkedin.com/in/jason-mitchell-b39a4418b](https://www.linkedin.com/in/jason-mitchell-b39a4418b)
- **GitHub**: [github.com/jason0960](https://github.com/jason0960)

## 📄 License

© 2026 Jason Mitchell. All rights reserved.
