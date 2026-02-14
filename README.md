# MitchellSoftware

My portfolio site and the interactive Lumber Yard Restock Planner demo that goes with it. Built this to show what I can do — full-stack engineering, 3D rendering, PDF automation, and observability — all in one place.

**Portfolio**: [jason0960.github.io/MitchellSoftware](https://jason0960.github.io/MitchellSoftware/)
**Demo**: [mitchellsoftwareportfolio.onrender.com](https://mitchellsoftwareportfolio.onrender.com)

---

## What's in here

### Portfolio (`index.html`)

The main site. Dark terminal theme with Home Depot orange (`#F96302`), JetBrains Mono font, the whole vibe. Has a creative/professional mode toggle so you can switch between a styled layout and a cleaner one. Everything's state-driven through a custom `AppState` manager — no frameworks, just vanilla JS.

Sections cover my career timeline, work contributions, tech stack, and a contact form wired up through EmailJS. There's also a "Did you enjoy this?" vote button that feeds into the analytics dashboard at the bottom of the page.

### Lumber Yard Restock Planner (`pallet-builder.*`)

This is the interactive demo. A 3D lumber yard with 20 product bunks you can browse, click to flag for restocking, and generate a full PDF delivery order from. The PDF includes:

- Line items with pricing and weight
- A **3D-rendered flatbed truck diagram** showing how the bunks get loaded (bin-packed onto the trailer)
- A yard health bar chart
- Order summary with totals

Built the 3D scene with Three.js r128. The truck diagram is rendered offscreen in a separate Three.js scene, exported as a PNG, and embedded directly into the PDF via ReportLab. The bin-packing uses a first-fit decreasing algorithm to figure out optimal loading.

The yard itself has individual board layers in each bunk, sticker separators between layers, banding straps — I went a little overboard on the detail but it looks good.

### Backend (`server.py`)

Flask server that handles:
- PDF generation via ReportLab
- Prometheus metrics (`/metrics` endpoint with counters, gauges, histograms)
- Event tracking (`/api/track`) and stats (`/api/stats`)
- System health monitoring (uptime, memory, CPU via psutil)
- Session tracking with a 15-minute sliding window

Deployed on Render.com. The portfolio itself is static on GitHub Pages.

---

## Running it locally

**Portfolio only** (no backend needed):
```bash
python -m http.server 8000
# then go to http://localhost:8000
```

**Full stack with the demo**:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
# then go to http://localhost:5000
```

**Tests**:
```bash
source .venv/bin/activate
pip install pytest
python -m pytest tests/ -v
```

---

## Tech

- **Frontend**: HTML/CSS/JS (no frameworks), Three.js for 3D, OrbitControls for camera
- **Backend**: Python, Flask, ReportLab, flask-cors
- **Monitoring**: prometheus-client, psutil
- **Hosting**: GitHub Pages (portfolio), Render.com (demo/API)
- **Fonts**: JetBrains Mono, Inter, Caveat
- **Testing**: pytest (306 tests across 6 test files)

## Project structure

```
├── index.html              # Portfolio page
├── styles.css              # Portfolio styles (dark + light themes)
├── script.js               # Portfolio JS (AppState, renderers, tracking)
├── pallet-builder.html     # Restock Planner page
├── pallet-builder.js       # 3D yard, interactions, PDF generation
├── pallet-builder.css      # Restock Planner styles
├── server.py               # Flask backend (PDF, metrics, tracking)
├── requirements.txt        # Python deps
├── pytest.ini              # Test config
├── tests/                  # Test suite (306 tests)
├── render.yaml             # Render.com deploy config
├── .github/workflows/      # GitHub Pages CI
├── DEPLOYMENT.md           # Deploy notes
└── README.md
```

## Contact

- **Email**: [jasonmitchell096@gmail.com](mailto:jasonmitchell096@gmail.com)
- **LinkedIn**: [linkedin.com/in/jason-mitchell-b39a4418b](https://www.linkedin.com/in/jason-mitchell-b39a4418b)
- **GitHub**: [github.com/jason0960](https://github.com/jason0960)

---

© 2026 Jason Mitchell
