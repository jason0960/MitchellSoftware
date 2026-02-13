/* ================================================================
   LUMBER YARD RESTOCK PLANNER — Three.js + WebGL
   GPU-accelerated 3D lumber yard with bunk inventory scanning.
   ================================================================ */

// ─── CATALOG ───────────────────────────────────────────────────
const CATALOG = [
    // Dimensional Lumber
    { id: 'dim-2x4x8',   name: '2×4×8 SPF',         category: 'Dimensional', capacity: 294, unitPrice: 3.48,  unitWeight: 9,   color: 0xdeb887, dims: { w: 3.5, h: 1.5, l: 96 }},
    { id: 'dim-2x4x10',  name: '2×4×10 SPF',        category: 'Dimensional', capacity: 294, unitPrice: 5.28,  unitWeight: 11,  color: 0xd2b48c, dims: { w: 3.5, h: 1.5, l: 120 }},
    { id: 'dim-2x4x12',  name: '2×4×12 SPF',        category: 'Dimensional', capacity: 294, unitPrice: 6.98,  unitWeight: 14,  color: 0xc4a882, dims: { w: 3.5, h: 1.5, l: 144 }},
    { id: 'dim-2x6x8',   name: '2×6×8 SPF',         category: 'Dimensional', capacity: 189, unitPrice: 5.98,  unitWeight: 14,  color: 0xcaa472, dims: { w: 5.5, h: 1.5, l: 96 }},
    { id: 'dim-2x6x12',  name: '2×6×12 SPF',        category: 'Dimensional', capacity: 189, unitPrice: 8.98,  unitWeight: 21,  color: 0xbc9862, dims: { w: 5.5, h: 1.5, l: 144 }},
    { id: 'dim-2x8x12',  name: '2×8×12 SPF',        category: 'Dimensional', capacity: 147, unitPrice: 12.68, unitWeight: 28,  color: 0xb08c52, dims: { w: 7.25, h: 1.5, l: 144 }},
    { id: 'dim-2x10x12', name: '2×10×12 SPF',       category: 'Dimensional', capacity: 98,  unitPrice: 17.28, unitWeight: 35,  color: 0xa48042, dims: { w: 9.25, h: 1.5, l: 144 }},
    { id: 'dim-2x12x16', name: '2×12×16 SPF',       category: 'Dimensional', capacity: 84,  unitPrice: 28.98, unitWeight: 56,  color: 0x987434, dims: { w: 11.25, h: 1.5, l: 192 }},
    { id: 'dim-4x4x8',   name: '4×4×8 Post',        category: 'Dimensional', capacity: 60,  unitPrice: 10.98, unitWeight: 22,  color: 0xd4a24c, dims: { w: 3.5, h: 3.5, l: 96 }},
    { id: 'dim-4x4x10',  name: '4×4×10 Post',       category: 'Dimensional', capacity: 60,  unitPrice: 14.98, unitWeight: 28,  color: 0xc89840, dims: { w: 3.5, h: 3.5, l: 120 }},

    // Sheet Goods
    { id: 'sht-ply34',   name: '3/4" Plywood 4×8',  category: 'Sheet', capacity: 40,  unitPrice: 42.98, unitWeight: 70,  color: 0xe8d5a0, dims: { w: 48, h: 0.75, l: 96 }},
    { id: 'sht-ply12',   name: '1/2" Plywood 4×8',  category: 'Sheet', capacity: 50,  unitPrice: 32.48, unitWeight: 48,  color: 0xf0ddb0, dims: { w: 48, h: 0.5, l: 96 }},
    { id: 'sht-osb',     name: '7/16" OSB 4×8',     category: 'Sheet', capacity: 60,  unitPrice: 14.98, unitWeight: 44,  color: 0xc8b080, dims: { w: 48, h: 0.4375, l: 96 }},
    { id: 'sht-mdf',     name: '3/4" MDF 4×8',      category: 'Sheet', capacity: 30,  unitPrice: 38.98, unitWeight: 86,  color: 0xbfa878, dims: { w: 48, h: 0.75, l: 96 }},

    // Pressure Treated
    { id: 'pt-2x6x12',   name: 'PT 2×6×12',         category: 'Treated', capacity: 120, unitPrice: 12.98, unitWeight: 28,  color: 0x7a8a5c, dims: { w: 5.5, h: 1.5, l: 144 }},
    { id: 'pt-4x4x8',    name: 'PT 4×4×8 Post',     category: 'Treated', capacity: 48,  unitPrice: 15.98, unitWeight: 30,  color: 0x6e7e50, dims: { w: 3.5, h: 3.5, l: 96 }},
    { id: 'pt-6x6x12',   name: 'PT 6×6×12 Timber',  category: 'Treated', capacity: 24,  unitPrice: 48.98, unitWeight: 80,  color: 0x627244, dims: { w: 5.5, h: 5.5, l: 144 }},

    // Specialty
    { id: 'sp-deck',     name: '5/4×6×12 Deck',     category: 'Specialty', capacity: 96,  unitPrice: 9.48,  unitWeight: 16,  color: 0xd4a860, dims: { w: 5.5, h: 1.0, l: 144 }},
    { id: 'sp-cedar',    name: 'Cedar 1×6×6 Fence',  category: 'Specialty', capacity: 480, unitPrice: 5.98,  unitWeight: 5,   color: 0xc05832, dims: { w: 5.5, h: 0.75, l: 72 }},
    { id: 'sp-landscape',name: 'Landscape Timber 8ft',category: 'Specialty', capacity: 36,  unitPrice: 4.98,  unitWeight: 18,  color: 0x5a6644, dims: { w: 3.5, h: 3.5, l: 96 }},
];

const TRUCK_MAX_LBS = 48000;

// ─── STATE ─────────────────────────────────────────────────────
let bunkData = [];          // { ...catalogItem, current, meshGroup, flagged }
let restockOrder = [];      // items flagged for restock
let scene, camera, renderer, controls;
let raycaster, mouse;
let hoveredBunk = null;
let animFrame;

// Camera fly-to state
let cameraTarget = null;   // { pos: Vector3, lookAt: Vector3, t: 0 }
const CAMERA_FLY_SPEED = 0.03;

// ─── INIT ──────────────────────────────────────────────────────
function init() {
    initScene();
    buildYard();
    bindEvents();
    updateYardHealth();
    animate();
}

// ─── THREE.JS SCENE ────────────────────────────────────────────
function initScene() {
    const canvas = document.getElementById('yardCanvas');
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x080c14);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x080c14, 0.006);

    camera = new THREE.PerspectiveCamera(50, canvas.clientWidth / canvas.clientHeight, 0.1, 500);
    camera.position.set(0, 30, 55);

    controls = new THREE.OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.target.set(0, 3, 0);
    controls.maxPolarAngle = Math.PI / 2.1;
    controls.minDistance = 15;
    controls.maxDistance = 120;

    // Lights
    const ambient = new THREE.AmbientLight(0xffffff, 0.35);
    scene.add(ambient);

    const sun = new THREE.DirectionalLight(0xffeedd, 0.8);
    sun.position.set(30, 50, 20);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    sun.shadow.camera.left = -60;
    sun.shadow.camera.right = 60;
    sun.shadow.camera.top = 50;
    sun.shadow.camera.bottom = -50;
    scene.add(sun);

    const fill = new THREE.DirectionalLight(0xaaccff, 0.25);
    fill.position.set(-20, 20, -10);
    scene.add(fill);

    // Ground
    const groundGeo = new THREE.PlaneGeometry(200, 200);
    const groundMat = new THREE.MeshStandardMaterial({ color: 0x1a1a2e, roughness: 0.9 });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Concrete pad lines
    for (let i = -80; i <= 80; i += 10) {
        const lineGeo = new THREE.PlaneGeometry(0.05, 160);
        const lineMat = new THREE.MeshBasicMaterial({ color: 0x252540 });
        const line = new THREE.Mesh(lineGeo, lineMat);
        line.rotation.x = -Math.PI / 2;
        line.position.set(i, 0.01, 0);
        scene.add(line);
    }

    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();

    onResize();
    window.addEventListener('resize', onResize);
}

function onResize() {
    const canvas = renderer.domElement;
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
}

// ─── BUILD THE YARD ────────────────────────────────────────────
function buildYard() {
    // Clear existing
    bunkData.forEach(b => { if (b.meshGroup) scene.remove(b.meshGroup); });
    bunkData = [];
    restockOrder = [];

    // Randomize fill levels
    const items = CATALOG.map(item => ({
        ...item,
        current: randomFill(item.capacity),
        flagged: false,
        meshGroup: null,
    }));

    bunkData = items;

    // Layout: 2 long rows
    const rowItems = [items.slice(0, 10), items.slice(10)];
    const rowZ = [12, -12];

    rowItems.forEach((row, ri) => {
        let xPos = -42;
        row.forEach((bunk, bi) => {
            const group = createBunkMesh(bunk, ri);
            group.position.set(xPos, 0, rowZ[ri]);
            group.userData = { bunkIndex: bunkData.indexOf(bunk) };
            scene.add(group);
            bunk.meshGroup = group;
            xPos += 9;
        });
    });

    // Row labels
    addRowLabel('Row A — Dimensional / Posts', -42, rowZ[0] + 5);
    addRowLabel('Row B — Sheet / Treated / Specialty', -42, rowZ[1] + 5);

    updateYardHealth();
    updateSidebar();
}

function randomFill(capacity) {
    // Weighted random: 30% chance full, 25% ok, 20% low, 15% critical, 10% empty
    const r = Math.random();
    if (r < 0.15) return 0;
    if (r < 0.30) return Math.floor(capacity * (0.05 + Math.random() * 0.15));
    if (r < 0.55) return Math.floor(capacity * (0.20 + Math.random() * 0.30));
    if (r < 0.75) return Math.floor(capacity * (0.50 + Math.random() * 0.25));
    return Math.floor(capacity * (0.80 + Math.random() * 0.20));
}

function createBunkMesh(bunk, rowIndex) {
    const group = new THREE.Group();
    const pct = bunk.current / bunk.capacity;
    const isSheet = bunk.category === 'Sheet';

    // Base rack / cradle — steel I-beam supports
    const rackW = 6;
    const rackD = 5;
    const rackH = 0.3;
    const rackGeo = new THREE.BoxGeometry(rackW, rackH, rackD);
    const rackMat = new THREE.MeshStandardMaterial({ color: 0x333344, roughness: 0.7 });
    const rack = new THREE.Mesh(rackGeo, rackMat);
    rack.position.y = rackH / 2;
    rack.castShadow = true;
    rack.receiveShadow = true;
    group.add(rack);

    // Cross-beam stickers (dunnage) under the bunk
    const stickerMat = new THREE.MeshStandardMaterial({ color: 0x444455, roughness: 0.6, metalness: 0.3 });
    for (let sz = -1.5; sz <= 1.5; sz += 1.5) {
        const stickerGeo = new THREE.BoxGeometry(rackW + 0.1, 0.15, 0.3);
        const sticker = new THREE.Mesh(stickerGeo, stickerMat);
        sticker.position.set(0, rackH + 0.075, sz);
        group.add(sticker);
    }

    // Vertical rack posts (HD orange steel)
    const postH = 7;
    const postGeo = new THREE.BoxGeometry(0.2, postH, 0.2);
    const postMat = new THREE.MeshStandardMaterial({ color: 0xF96302, roughness: 0.5, metalness: 0.4 });
    [[-rackW/2 + 0.15, -rackD/2 + 0.15], [-rackW/2 + 0.15, rackD/2 - 0.15],
     [rackW/2 - 0.15, -rackD/2 + 0.15], [rackW/2 - 0.15, rackD/2 - 0.15]].forEach(([x, z]) => {
        const post = new THREE.Mesh(postGeo, postMat);
        post.position.set(x, postH / 2, z);
        post.castShadow = true;
        group.add(post);
    });

    // Individual board layers
    const maxStackH = 5.5;
    const stackH = maxStackH * pct;
    const baseY = rackH + 0.15; // above dunnage

    if (stackH > 0.05) {
        // Shared geometries & materials (reused across layers to cut draw calls)
        const boardMat = new THREE.MeshStandardMaterial({ color: bunk.color, roughness: 0.85 });
        const boardAltMat = new THREE.MeshStandardMaterial({ color: darkenColor(bunk.color, 0.92), roughness: 0.85 });
        const stickerBoardMat = new THREE.MeshStandardMaterial({ color: 0x555566, roughness: 0.6 });

        if (isSheet) {
            // Sheet goods — fewer thick slabs for performance
            const sheetThick = 0.15;
            const gap = 0.03;
            const numSheets = Math.min(Math.floor(stackH / (sheetThick + gap)), 15);
            const sheetGeo = new THREE.BoxGeometry(rackW - 0.5, sheetThick, rackD - 0.3);
            for (let i = 0; i < numSheets; i++) {
                const y = baseY + i * (sheetThick + gap) + sheetThick / 2;
                const sheet = new THREE.Mesh(sheetGeo, i % 2 === 0 ? boardMat : boardAltMat);
                sheet.position.y = y;
                sheet.castShadow = i === numSheets - 1;
                sheet.receiveShadow = i === 0;
                group.add(sheet);
            }
        } else {
            // Dimensional lumber — full-width layer slabs with sticker separators
            // Each layer is ONE mesh (the full row), not individual boards
            const layerH = 0.18;
            const layerGap = 0.02;
            const stickerEvery = 4;
            const stickerH = 0.06;
            const numLayers = Math.min(Math.floor(stackH / (layerH + layerGap)), 18);
            const layerGeo = new THREE.BoxGeometry(rackW - 0.5, layerH, rackD - 0.4);
            const stickerGeo = new THREE.BoxGeometry(rackW - 0.4, stickerH, 0.2);

            let curY = baseY;
            for (let layer = 0; layer < numLayers; layer++) {
                // Sticker separator every N layers
                if (layer > 0 && layer % stickerEvery === 0) {
                    for (let sz = -1.5; sz <= 1.5; sz += 1.5) {
                        const st = new THREE.Mesh(stickerGeo, stickerBoardMat);
                        st.position.set(0, curY + stickerH / 2, sz);
                        group.add(st);
                    }
                    curY += stickerH + layerGap;
                }
                const slab = new THREE.Mesh(layerGeo, layer % 2 === 0 ? boardMat : boardAltMat);
                slab.position.set(0, curY + layerH / 2, 0);
                slab.castShadow = layer === numLayers - 1;
                slab.receiveShadow = layer === 0;
                group.add(slab);
                curY += layerH + layerGap;
            }

            // Board edge lines on the front face (visual detail, cheap planes)
            const edgeLineMat = new THREE.MeshBasicMaterial({ color: darkenColor(bunk.color, 0.78), side: THREE.DoubleSide });
            const edgeCount = Math.min(Math.floor((rackD - 0.4) / 0.4), 12);
            const edgeGeo = new THREE.PlaneGeometry(rackW - 0.6, stackH);
            for (let e = 0; e < edgeCount; e++) {
                const ez = -(rackD - 0.4) / 2 + (e + 1) * ((rackD - 0.4) / (edgeCount + 1));
                const eLine = new THREE.Mesh(
                    new THREE.PlaneGeometry(0.02, Math.min(stackH, maxStackH)),
                    edgeLineMat
                );
                eLine.position.set(0, baseY + Math.min(stackH, maxStackH) / 2, rackD / 2 - 0.18);
                eLine.position.z = rackD / 2 - 0.18;
                eLine.position.x = -(rackW - 0.5) / 2 + 0.2 + e * ((rackW - 0.7) / edgeCount);
                group.add(eLine);
            }
        }
    }

    // Banding straps (orange steel straps around the bunk)
    if (stackH > 0.3) {
        const strapMat = new THREE.MeshStandardMaterial({ color: 0xF96302, roughness: 0.4, metalness: 0.6 });
        const strapPositions = [-1.8, 0, 1.8];
        strapPositions.forEach(sx => {
            // Vertical front strap
            const frontGeo = new THREE.BoxGeometry(0.06, Math.min(stackH, maxStackH), 0.06);
            const front = new THREE.Mesh(frontGeo, strapMat);
            front.position.set(sx, baseY + Math.min(stackH, maxStackH) / 2, rackD / 2 - 0.12);
            group.add(front);
            // Vertical back strap
            const back = new THREE.Mesh(frontGeo, strapMat);
            back.position.set(sx, baseY + Math.min(stackH, maxStackH) / 2, -rackD / 2 + 0.12);
            group.add(back);
            // Top strap
            const topGeo = new THREE.BoxGeometry(0.06, 0.06, rackD - 0.2);
            const top = new THREE.Mesh(topGeo, strapMat);
            top.position.set(sx, baseY + Math.min(stackH, maxStackH), 0);
            group.add(top);
        });
    }

    // Fill-level indicator bar (floating above)
    const indGeo = new THREE.BoxGeometry(rackW, 0.2, 0.3);
    const indMat = new THREE.MeshBasicMaterial({ color: getFillColor(pct) });
    const indicator = new THREE.Mesh(indGeo, indMat);
    indicator.position.set(0, postH + 0.3, 0);
    indicator.name = 'indicator';
    group.add(indicator);

    // Label sprite
    const label = makeTextSprite(bunk.name, pct);
    label.position.set(0, postH + 1, 0);
    label.name = 'label';
    group.add(label);

    // Percentage sprite
    const pctLabel = makeTextSprite(`${Math.round(pct * 100)}%`, pct, true);
    pctLabel.position.set(0, postH + 0.5, rackD / 2 + 0.8);
    pctLabel.name = 'pctLabel';
    group.add(pctLabel);

    // Low-stock glow (pulsing red box for bunks < 25%)
    const glowMat = new THREE.MeshBasicMaterial({ color: 0xff3333, transparent: true, opacity: 0 });
    const glowMesh = new THREE.Mesh(new THREE.BoxGeometry(rackW + 0.6, postH + 1, rackD + 0.6), glowMat);
    glowMesh.position.y = (postH + 1) / 2;
    glowMesh.name = 'lowStockGlow';
    glowMesh.visible = false;
    group.add(glowMesh);

    return group;
}

function getFillColor(pct) {
    if (pct >= 0.8) return 0x22c55e;
    if (pct >= 0.5) return 0x86efac;
    if (pct >= 0.2) return 0xeab308;
    if (pct > 0)    return 0xef4444;
    return 0x374151;
}

function getFillColorCSS(pct) {
    if (pct >= 0.8) return '#22c55e';
    if (pct >= 0.5) return '#86efac';
    if (pct >= 0.2) return '#eab308';
    if (pct > 0)    return '#ef4444';
    return '#374151';
}

function getFillLabel(pct) {
    if (pct >= 0.8) return 'Full';
    if (pct >= 0.5) return 'OK';
    if (pct >= 0.2) return 'Low';
    if (pct > 0)    return 'Critical';
    return 'Empty';
}

function darkenColor(hex, factor) {
    const r = ((hex >> 16) & 0xff) * factor;
    const g = ((hex >> 8) & 0xff) * factor;
    const b = (hex & 0xff) * factor;
    return (Math.floor(r) << 16) | (Math.floor(g) << 8) | Math.floor(b);
}

function makeTextSprite(text, pct, small = false) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = small ? 128 : 256;
    canvas.height = small ? 48 : 64;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = `${small ? 'bold 28px' : 'bold 22px'} monospace`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = getFillColorCSS(pct);
    ctx.fillText(text, canvas.width / 2, canvas.height / 2);

    const tex = new THREE.CanvasTexture(canvas);
    tex.minFilter = THREE.LinearFilter;
    const mat = new THREE.SpriteMaterial({ map: tex, transparent: true });
    const sprite = new THREE.Sprite(mat);
    sprite.scale.set(small ? 2.5 : 5, small ? 1 : 1.2, 1);
    return sprite;
}

function addRowLabel(text, x, z) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 512;
    canvas.height = 64;
    ctx.fillStyle = '#F96302';
    ctx.font = 'bold 28px monospace';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 10, 32);
    const tex = new THREE.CanvasTexture(canvas);
    tex.minFilter = THREE.LinearFilter;
    const mat = new THREE.SpriteMaterial({ map: tex, transparent: true });
    const sprite = new THREE.Sprite(mat);
    sprite.scale.set(18, 2, 1);
    sprite.position.set(x + 18, 10, z);
    scene.add(sprite);
}

// ─── INTERACTION ───────────────────────────────────────────────
function bindEvents() {
    const canvas = renderer.domElement;
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('click', onMouseClick);
    canvas.addEventListener('touchend', onTouchTap, { passive: false });
    document.getElementById('generatePdfBtn').addEventListener('click', generatePdf);
    document.getElementById('clearCartBtn').addEventListener('click', clearSelection);
    document.getElementById('rotateLeftBtn').addEventListener('click', () => rotateCamera(-1));
    document.getElementById('rotateRightBtn').addEventListener('click', () => rotateCamera(1));
    document.getElementById('resetViewBtn').addEventListener('click', resetView);
    document.getElementById('randomizeBtn').addEventListener('click', () => { buildYard(); });
    document.getElementById('searchInput').addEventListener('input', highlightSearch);
    document.querySelectorAll('.pb-cat-tab').forEach(tab => {
        tab.addEventListener('click', () => filterCategory(tab));
    });

    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('pbSidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    const closeSidebar = document.getElementById('closeSidebar');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => { sidebar.classList.add('open'); backdrop.classList.add('visible'); });
        closeSidebar.addEventListener('click', () => { sidebar.classList.remove('open'); backdrop.classList.remove('visible'); });
        backdrop.addEventListener('click', () => { sidebar.classList.remove('open'); backdrop.classList.remove('visible'); });
    }

    // Dark/light theme toggle
    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
        // Restore saved theme
        if (localStorage.getItem('pb-theme') === 'light') {
            document.body.classList.add('light-theme');
            themeBtn.innerHTML = '<i class="fas fa-moon"></i>';
            renderer.setClearColor(0xdde0e6);
        }
        themeBtn.addEventListener('click', () => {
            const isLight = document.body.classList.toggle('light-theme');
            themeBtn.innerHTML = isLight ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
            renderer.setClearColor(isLight ? 0xdde0e6 : 0x080c14);
            localStorage.setItem('pb-theme', isLight ? 'light' : 'dark');
        });
    }
}

function onMouseMove(e) {
    const canvas = renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const meshes = [];
    bunkData.forEach(b => { if (b.meshGroup) meshes.push(...b.meshGroup.children.filter(c => c.isMesh)); });
    const intersects = raycaster.intersectObjects(meshes);

    const tooltip = document.getElementById('itemTooltip');

    if (intersects.length > 0) {
        const group = intersects[0].object.parent;
        const idx = group.userData.bunkIndex;
        if (idx !== undefined && idx !== hoveredBunk) {
            hoveredBunk = idx;
            const bunk = bunkData[idx];
            const pct = bunk.current / bunk.capacity;
            const toOrder = bunk.capacity - bunk.current;
            tooltip.innerHTML = `
                <div class="tt-name">${bunk.name}</div>
                <div class="tt-row"><span>In stock:</span><span>${bunk.current} / ${bunk.capacity}</span></div>
                <div class="tt-row"><span>Status:</span><span style="color:${getFillColorCSS(pct)}">${getFillLabel(pct)}</span></div>
                <div class="tt-row"><span>To restock:</span><span>${toOrder} pcs</span></div>
                <div class="tt-row"><span>Unit price:</span><span>$${bunk.unitPrice.toFixed(2)}</span></div>
                <div class="tt-bar"><div class="tt-fill" style="width:${pct*100}%;background:${getFillColorCSS(pct)}"></div></div>
            `;
            tooltip.classList.add('visible');
        }
        tooltip.style.left = (e.clientX - renderer.domElement.getBoundingClientRect().left + 15) + 'px';
        tooltip.style.top = (e.clientY - renderer.domElement.getBoundingClientRect().top - 10) + 'px';
        canvas.style.cursor = 'pointer';
    } else {
        hoveredBunk = null;
        tooltip.classList.remove('visible');
        canvas.style.cursor = 'grab';
    }
}

function onMouseClick(e) {
    if (hoveredBunk === null) return;
    const bunk = bunkData[hoveredBunk];
    if (bunk.current >= bunk.capacity) {
        showStatus('That bunk is fully stocked — no restock needed!', 'error');
        return;
    }
    toggleFlag(hoveredBunk);
}

function onTouchTap(e) {
    if (!e.changedTouches || e.changedTouches.length === 0) return;
    const touch = e.changedTouches[0];
    const canvas = renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    mouse.x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const meshes = [];
    bunkData.forEach(b => { if (b.meshGroup) meshes.push(...b.meshGroup.children.filter(c => c.isMesh)); });
    const intersects = raycaster.intersectObjects(meshes);

    if (intersects.length > 0) {
        const group = intersects[0].object.parent;
        const idx = group.userData.bunkIndex;
        if (idx !== undefined) {
            const bunk = bunkData[idx];
            if (bunk.current >= bunk.capacity) {
                showStatus('That bunk is fully stocked — no restock needed!', 'error');
                return;
            }
            toggleFlag(idx);
        }
    }
}

function toggleFlag(idx) {
    const bunk = bunkData[idx];
    bunk.flagged = !bunk.flagged;

    updateBunkVisual(bunk);

    if (bunk.flagged) {
        restockOrder.push(bunk);
        showStatus(`Flagged ${bunk.name} for restocking`, 'success');
        // Fly camera toward the bunk
        if (bunk.meshGroup) {
            const pos = bunk.meshGroup.position.clone();
            const offset = camera.position.clone().sub(controls.target).normalize().multiplyScalar(25);
            cameraTarget = {
                pos: new THREE.Vector3(pos.x + offset.x, Math.max(camera.position.y, 20), pos.z + offset.z),
                lookAt: new THREE.Vector3(pos.x, pos.y + 3, pos.z),
                t: 0
            };
        }
    } else {
        restockOrder = restockOrder.filter(b => b.id !== bunk.id);
        showStatus(`Removed ${bunk.name} from restock order`, '');
    }

    updateSidebar();
    updateToggleBadge();
    document.getElementById('hoverHint').classList.add('hidden');
}

function updateBunkVisual(bunk) {
    if (!bunk.meshGroup) return;
    // Remove existing ring
    const existing = bunk.meshGroup.getObjectByName('flagRing');
    if (existing) bunk.meshGroup.remove(existing);

    if (bunk.flagged) {
        // Add glowing ring
        const ringGeo = new THREE.RingGeometry(3.8, 4.2, 32);
        const ringMat = new THREE.MeshBasicMaterial({
            color: 0xF96302,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.8,
        });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = -Math.PI / 2;
        ring.position.y = 0.05;
        ring.name = 'flagRing';
        bunk.meshGroup.add(ring);

        // Pulse the indicator
        const ind = bunk.meshGroup.getObjectByName('indicator');
        if (ind) ind.material.color.setHex(0xF96302);
    } else {
        // Restore indicator color
        const pct = bunk.current / bunk.capacity;
        const ind = bunk.meshGroup.getObjectByName('indicator');
        if (ind) ind.material.color.setHex(getFillColor(pct));
    }
}

// ─── SIDEBAR ───────────────────────────────────────────────────
function updateSidebar() {
    const cartList = document.getElementById('cartList');
    const badge = document.getElementById('cartBadge');
    const btn = document.getElementById('generatePdfBtn');

    badge.textContent = restockOrder.length;

    if (restockOrder.length === 0) {
        cartList.innerHTML = '<p class="pb-empty">No bunks flagged — click low bunks in the yard!</p>';
        btn.disabled = true;
    } else {
        cartList.innerHTML = restockOrder.map((bunk, i) => {
            const toOrder = bunk.capacity - bunk.current;
            const cost = toOrder * bunk.unitPrice;
            const pct = bunk.current / bunk.capacity;
            return `
                <div class="pb-cart-item">
                    <div class="pb-cart-color" style="background:${getFillColorCSS(pct)}"></div>
                    <div class="pb-cart-info">
                        <div class="pb-cart-name">${bunk.name}</div>
                        <div class="pb-cart-detail">${toOrder} pcs × $${bunk.unitPrice.toFixed(2)} = $${cost.toFixed(2)}</div>
                    </div>
                    <button class="pb-cart-remove" onclick="removeBunkByIndex(${bunkData.indexOf(bunk)})" title="Remove">
                        <i class="fas fa-xmark"></i>
                    </button>
                </div>
            `;
        }).join('');
        btn.disabled = false;
    }

    // Summary
    let totalItems = restockOrder.length;
    let totalQty = 0, totalCost = 0, totalWeight = 0;
    restockOrder.forEach(b => {
        const qty = b.capacity - b.current;
        totalQty += qty;
        totalCost += qty * b.unitPrice;
        totalWeight += qty * b.unitWeight;
    });

    document.getElementById('totalItems').textContent = totalItems;
    document.getElementById('totalQty').textContent = totalQty.toLocaleString();
    document.getElementById('totalPrice').textContent = '$' + totalCost.toFixed(2);
    document.getElementById('weightLabel').textContent = totalWeight.toLocaleString() + ' lbs';

    const pct = Math.min(totalWeight / TRUCK_MAX_LBS, 1);
    const bar = document.getElementById('weightBar');
    bar.style.width = (pct * 100) + '%';
    bar.className = 'pb-load-bar' + (pct > 0.9 ? ' danger' : pct > 0.7 ? ' warn' : '');
}

function removeBunkByIndex(idx) {
    toggleFlag(idx);
}

function updateToggleBadge() {
    const badge = document.getElementById('toggleBadge');
    if (badge) badge.textContent = restockOrder.length;
}

function clearSelection() {
    bunkData.forEach((b, i) => {
        if (b.flagged) toggleFlag(i);
    });
}

function updateYardHealth() {
    let full = 0, low = 0, crit = 0;
    bunkData.forEach(b => {
        const pct = b.current / b.capacity;
        if (pct >= 0.5) full++;
        else if (pct >= 0.2) low++;
        else crit++;
    });
    document.getElementById('fullCount').textContent = full;
    document.getElementById('lowCount').textContent = low;
    document.getElementById('critCount').textContent = crit;
}

// ─── SEARCH / FILTER ───────────────────────────────────────────
function highlightSearch() {
    const q = document.getElementById('searchInput').value.toLowerCase().trim();
    bunkData.forEach(b => {
        if (!b.meshGroup) return;
        const match = !q || b.name.toLowerCase().includes(q);
        b.meshGroup.visible = match;
    });
}

function filterCategory(tab) {
    document.querySelectorAll('.pb-cat-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const cat = tab.dataset.cat;
    bunkData.forEach(b => {
        if (!b.meshGroup) return;
        b.meshGroup.visible = cat === 'all' || b.category === cat;
    });
}

// ─── CAMERA CONTROLS ──────────────────────────────────────────
function rotateCamera(dir) {
    const angle = dir * Math.PI / 6;
    const c = controls.target.clone();
    const offset = camera.position.clone().sub(c);
    const cosA = Math.cos(angle), sinA = Math.sin(angle);
    const newX = offset.x * cosA - offset.z * sinA;
    const newZ = offset.x * sinA + offset.z * cosA;
    camera.position.set(c.x + newX, camera.position.y, c.z + newZ);
    controls.update();
}

function resetView() {
    camera.position.set(0, 30, 55);
    controls.target.set(0, 3, 0);
    controls.update();
}

// ─── ANIMATE ───────────────────────────────────────────────────
function animate() {
    animFrame = requestAnimationFrame(animate);

    // Camera fly-to animation
    if (cameraTarget) {
        cameraTarget.t += CAMERA_FLY_SPEED;
        const t = Math.min(cameraTarget.t, 1);
        const ease = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; // easeInOutQuad
        camera.position.lerpVectors(camera.position, cameraTarget.pos, ease * 0.08);
        controls.target.lerp(cameraTarget.lookAt, ease * 0.08);
        if (t >= 1) cameraTarget = null;
    }

    controls.update();

    const t = Date.now() * 0.003;

    bunkData.forEach(b => {
        if (!b.meshGroup) return;

        // Pulse flagged bunk rings
        if (b.flagged) {
            const ring = b.meshGroup.getObjectByName('flagRing');
            if (ring) ring.material.opacity = 0.5 + 0.3 * Math.sin(t);
        }

        // Low-stock pulse glow (< 25% and not flagged)
        const pct = b.current / b.capacity;
        const glow = b.meshGroup.getObjectByName('lowStockGlow');
        if (glow) {
            if (pct < 0.25 && pct > 0 && !b.flagged) {
                glow.visible = true;
                glow.material.opacity = 0.15 + 0.1 * Math.sin(t * 1.5);
            } else {
                glow.visible = false;
            }
        }
    });

    renderer.render(scene, camera);
}

// ─── PDF GENERATION ────────────────────────────────────────────
async function generatePdf() {
    if (restockOrder.length === 0) return;
    const btn = document.getElementById('generatePdfBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    showStatus('Building restock order PDF...', '');

    // Build order data
    const orderItems = restockOrder.map(b => ({
        name: b.name,
        category: b.category,
        current: b.current,
        capacity: b.capacity,
        toOrder: b.capacity - b.current,
        unitPrice: b.unitPrice,
        unitWeight: b.unitWeight,
        totalWeight: (b.capacity - b.current) * b.unitWeight,
        totalCost: (b.capacity - b.current) * b.unitPrice,
        color: '#' + b.color.toString(16).padStart(6, '0'),
    }));

    // Build truck diagram on canvas
    const truckCanvas = buildTruckDiagram(orderItems);
    const truckImageData = truckCanvas.toDataURL('image/png');

    // Build bunk status chart
    const chartCanvas = buildYardChart();
    const chartImageData = chartCanvas.toDataURL('image/png');

    const payload = {
        items: orderItems,
        truckImage: truckImageData,
        chartImage: chartImageData,
        totalWeight: orderItems.reduce((s, i) => s + i.totalWeight, 0),
        totalCost: orderItems.reduce((s, i) => s + i.totalCost, 0),
        totalPieces: orderItems.reduce((s, i) => s + i.toOrder, 0),
        totalBunks: orderItems.length,
    };

    try {
        const res = await fetch('http://localhost:5000/generate-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error('Server error ' + res.status);
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        window.open(url, '_blank');
        showStatus('Restock order PDF generated!', 'success');
    } catch (err) {
        showStatus('PDF generation failed — is the Flask server running?', 'error');
        console.error(err);
    }

    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-file-pdf"></i> Generate Restock Order (PDF)';
}

// ─── 3D FLATBED TRUCK DIAGRAM (offscreen Three.js render) ─────
function buildTruckDiagram(items) {
    const W = 1200, H = 700;

    // Offscreen renderer
    const offCanvas = document.createElement('canvas');
    offCanvas.width = W;
    offCanvas.height = H;
    const offRenderer = new THREE.WebGLRenderer({ canvas: offCanvas, antialias: true, preserveDrawingBuffer: true });
    offRenderer.setSize(W, H);
    offRenderer.setClearColor(0x0a0e17);
    offRenderer.shadowMap.enabled = true;
    offRenderer.shadowMap.type = THREE.PCFSoftShadowMap;

    const offScene = new THREE.Scene();
    offScene.fog = new THREE.FogExp2(0x0a0e17, 0.008);

    // Camera — slightly above middle, off to the right
    const offCamera = new THREE.PerspectiveCamera(42, W / H, 0.1, 500);
    offCamera.position.set(28, 18, 22);
    offCamera.lookAt(0, 2, -4);

    // Lights
    offScene.add(new THREE.AmbientLight(0xffffff, 0.45));
    const offSun = new THREE.DirectionalLight(0xffeedd, 0.9);
    offSun.position.set(30, 40, 25);
    offSun.castShadow = true;
    offSun.shadow.mapSize.set(2048, 2048);
    offSun.shadow.camera.left = -40;
    offSun.shadow.camera.right = 40;
    offSun.shadow.camera.top = 30;
    offSun.shadow.camera.bottom = -30;
    offScene.add(offSun);
    const offFill = new THREE.DirectionalLight(0x8899cc, 0.3);
    offFill.position.set(-15, 15, -10);
    offScene.add(offFill);

    // Ground plane
    const gndGeo = new THREE.PlaneGeometry(120, 120);
    const gndMat = new THREE.MeshStandardMaterial({ color: 0x1a1a2e, roughness: 0.95 });
    const gnd = new THREE.Mesh(gndGeo, gndMat);
    gnd.rotation.x = -Math.PI / 2;
    gnd.receiveShadow = true;
    offScene.add(gnd);

    // ── BUILD FLATBED TRUCK ──
    const truck = new THREE.Group();

    // --- Chassis frame (long steel I-beams) ---
    const frameMat = new THREE.MeshStandardMaterial({ color: 0x222233, roughness: 0.6, metalness: 0.5 });
    const frameL = 30; // total truck length
    const frameBeam = new THREE.BoxGeometry(frameL, 0.3, 0.4);
    const leftRail = new THREE.Mesh(frameBeam, frameMat);
    leftRail.position.set(0, 0.8, -1.8);
    leftRail.castShadow = true;
    truck.add(leftRail);
    const rightRail = new THREE.Mesh(frameBeam, frameMat);
    rightRail.position.set(0, 0.8, 1.8);
    rightRail.castShadow = true;
    truck.add(rightRail);
    // Cross members
    for (let cx = -frameL/2 + 1; cx <= frameL/2 - 1; cx += 2.5) {
        const crossGeo = new THREE.BoxGeometry(0.2, 0.2, 4);
        const cross = new THREE.Mesh(crossGeo, frameMat);
        cross.position.set(cx, 0.75, 0);
        truck.add(cross);
    }

    // --- Flatbed deck (wood plank surface) ---
    const deckW = 24, deckD = 4.8, deckH2 = 0.15;
    const deckMat = new THREE.MeshStandardMaterial({ color: 0x3a3525, roughness: 0.9 });
    const deckMesh = new THREE.Mesh(new THREE.BoxGeometry(deckW, deckH2, deckD), deckMat);
    deckMesh.position.set(2, 1.05, 0);
    deckMesh.castShadow = true;
    deckMesh.receiveShadow = true;
    truck.add(deckMesh);
    // Plank lines on the deck
    const plankLineMat = new THREE.MeshBasicMaterial({ color: 0x2e2a1e });
    for (let pz = -deckD/2 + 0.4; pz < deckD/2; pz += 0.45) {
        const plLine = new THREE.Mesh(new THREE.BoxGeometry(deckW - 0.1, 0.01, 0.02), plankLineMat);
        plLine.position.set(2, 1.13, pz);
        truck.add(plLine);
    }

    // --- Headache rack (behind cab) ---
    const hrMat = new THREE.MeshStandardMaterial({ color: 0xF96302, roughness: 0.4, metalness: 0.5 });
    // Main posts
    const hrH = 4;
    const hrX = 2 - deckW/2 + 0.2;
    [[-1.8], [1.8]].forEach(([z]) => {
        const post = new THREE.Mesh(new THREE.BoxGeometry(0.12, hrH, 0.12), hrMat);
        post.position.set(hrX, 1.13 + hrH/2, z);
        post.castShadow = true;
        truck.add(post);
    });
    // Cross bars
    for (let hy = 1.7; hy < hrH + 1.13; hy += 0.8) {
        const bar = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, 3.8), hrMat);
        bar.position.set(hrX, hy, 0);
        truck.add(bar);
    }
    // Top rail
    const topRail = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.15, 4), hrMat);
    topRail.position.set(hrX, 1.13 + hrH, 0);
    truck.add(topRail);

    // --- Cab (semi-truck tractor) ---
    const cabGroup = new THREE.Group();
    const cabMat = new THREE.MeshStandardMaterial({ color: 0xF96302, roughness: 0.35, metalness: 0.3 });
    const cabDarkMat = new THREE.MeshStandardMaterial({ color: 0xcc5500, roughness: 0.35, metalness: 0.3 });
    const glassMat = new THREE.MeshStandardMaterial({ color: 0x8aaccf, roughness: 0.1, metalness: 0.6, transparent: true, opacity: 0.7 });

    // Cab box
    const cabBody = new THREE.Mesh(new THREE.BoxGeometry(4, 3.2, 3.6), cabMat);
    cabBody.position.set(-12, 2.6, 0);
    cabBody.castShadow = true;
    cabGroup.add(cabBody);
    // Hood (lower extension)
    const hood = new THREE.Mesh(new THREE.BoxGeometry(3, 1.6, 3.4), cabDarkMat);
    hood.position.set(-15, 1.4, 0);
    hood.castShadow = true;
    cabGroup.add(hood);
    // Windshield
    const windshield = new THREE.Mesh(new THREE.BoxGeometry(0.08, 1.8, 2.8), glassMat);
    windshield.position.set(-13.5, 3.0, 0);
    windshield.rotation.z = 0.15;
    cabGroup.add(windshield);
    // Side windows
    const sideWinR = new THREE.Mesh(new THREE.BoxGeometry(2.5, 1.2, 0.06), glassMat);
    sideWinR.position.set(-12, 3.2, 1.82);
    cabGroup.add(sideWinR);
    const sideWinL = new THREE.Mesh(new THREE.BoxGeometry(2.5, 1.2, 0.06), glassMat);
    sideWinL.position.set(-12, 3.2, -1.82);
    cabGroup.add(sideWinL);
    // Exhaust stacks
    const exhMat = new THREE.MeshStandardMaterial({ color: 0x666666, roughness: 0.3, metalness: 0.7 });
    [-1.6, 1.6].forEach(ez => {
        const exh = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 2.5, 8), exhMat);
        exh.position.set(-10.3, 4.7, ez);
        cabGroup.add(exh);
        // Cap
        const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.12, 0.2, 8), exhMat);
        cap.position.set(-10.3, 6.0, ez);
        cabGroup.add(cap);
    });
    // Headlights
    const hlMat = new THREE.MeshBasicMaterial({ color: 0xffffaa });
    [-1, 1].forEach(hz => {
        const hl = new THREE.Mesh(new THREE.SphereGeometry(0.18, 8, 8), hlMat);
        hl.position.set(-16.5, 1.6, hz);
        cabGroup.add(hl);
    });
    // Grille
    const grilleMat = new THREE.MeshStandardMaterial({ color: 0x888888, roughness: 0.4, metalness: 0.6 });
    const grille = new THREE.Mesh(new THREE.BoxGeometry(0.08, 1.2, 2.8), grilleMat);
    grille.position.set(-16.52, 1.4, 0);
    cabGroup.add(grille);
    // Bumper
    const bumperMat = new THREE.MeshStandardMaterial({ color: 0x555555, roughness: 0.4, metalness: 0.5 });
    const bumper = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 3.8), bumperMat);
    bumper.position.set(-16.7, 0.7, 0);
    cabGroup.add(bumper);
    // Steps
    const stepMat = new THREE.MeshStandardMaterial({ color: 0x444444, roughness: 0.5 });
    [1.9, -1.9].forEach(sz => {
        const step = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.12, 0.6), stepMat);
        step.position.set(-11, 1.0, sz);
        cabGroup.add(step);
    });
    // Fuel tanks (cylindrical, under cab)
    const tankMat = new THREE.MeshStandardMaterial({ color: 0x444455, roughness: 0.4, metalness: 0.5 });
    [-2.2, 2.2].forEach(tz => {
        const tank = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 2.5, 12), tankMat);
        tank.rotation.z = Math.PI / 2;
        tank.position.set(-11, 0.9, tz);
        cabGroup.add(tank);
    });

    truck.add(cabGroup);

    // --- Wheels (with dual tires) ---
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.9 });
    const rimMat = new THREE.MeshStandardMaterial({ color: 0x666666, roughness: 0.3, metalness: 0.7 });
    const hubMat = new THREE.MeshStandardMaterial({ color: 0x888888, roughness: 0.3, metalness: 0.5 });

    function addWheelSet(x, z, dual) {
        const offsets = dual ? [-0.25, 0.25] : [0];
        offsets.forEach(dz => {
            const tire = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.35, 16), wheelMat);
            tire.rotation.x = Math.PI / 2;
            tire.position.set(x, 0.5, z + dz);
            tire.castShadow = true;
            truck.add(tire);
            const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.37, 12), rimMat);
            rim.rotation.x = Math.PI / 2;
            rim.position.set(x, 0.5, z + dz);
            truck.add(rim);
            const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.39, 8), hubMat);
            hub.rotation.x = Math.PI / 2;
            hub.position.set(x, 0.5, z + dz);
            truck.add(hub);
        });
    }
    // Steer axle
    addWheelSet(-15, -1.85, false);
    addWheelSet(-15, 1.85, false);
    // Drive tandem
    addWheelSet(-10, -1.85, true);
    addWheelSet(-10, 1.85, true);
    addWheelSet(-8.5, -1.85, true);
    addWheelSet(-8.5, 1.85, true);
    // Trailer tandem
    addWheelSet(11, -1.85, true);
    addWheelSet(11, 1.85, true);
    addWheelSet(12.5, -1.85, true);
    addWheelSet(12.5, 1.85, true);

    // --- Fenders / Mudflaps ---
    const fenderMat = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.5 });
    // Cab steer axle fenders (above wheels, on cab body)
    [-2.15, 2.15].forEach(fz => {
        const fender = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.06, 0.6), fenderMat);
        fender.position.set(-15, 1.15, fz);
        truck.add(fender);
    });
    // Drive tandem fenders (behind cab, above wheels)
    [-2.25, 2.25].forEach(fz => {
        const fender = new THREE.Mesh(new THREE.BoxGeometry(3.5, 0.06, 0.8), fenderMat);
        fender.position.set(-9.25, 1.15, fz);
        truck.add(fender);
    });
    // Trailer tandem — mudguard brackets under the deck, outboard
    const mudguardMat = new THREE.MeshStandardMaterial({ color: 0x2a2a2a, roughness: 0.6 });
    [-2.35, 2.35].forEach(fz => {
        // Horizontal mudguard above trailer wheels
        const guard = new THREE.Mesh(new THREE.BoxGeometry(3.8, 0.06, 0.55), mudguardMat);
        guard.position.set(11.75, 1.08, fz);
        truck.add(guard);
        // Vertical bracket connecting mudguard to frame
        const bracket = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.5, 0.08), mudguardMat);
        bracket.position.set(10, 0.85, fz);
        truck.add(bracket);
        const bracket2 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.5, 0.08), mudguardMat);
        bracket2.position.set(13.5, 0.85, fz);
        truck.add(bracket2);
        // Rear mudflap
        const flap = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.6, 0.4), mudguardMat);
        flap.position.set(13.8, 0.7, fz);
        truck.add(flap);
    });

    offScene.add(truck);

    // ── BIN-PACK BUNKS ONTO THE 3D FLATBED ──
    const deckTop = 1.13;
    const loadableLength = deckW - 1.5; // leave space near headache rack
    const loadableWidth = deckD - 0.6;
    const deckStartX = hrX + 0.5; // start loading after headache rack

    // Sort heaviest first
    const sorted = [...items].sort((a, b) => {
        const wDiff = b.totalWeight - a.totalWeight;
        if (Math.abs(wDiff) > 100) return wDiff;
        return b.toOrder - a.toOrder;
    });

    // Calculate bunk 3D dimensions based on order quantity
    const bunkModels = sorted.map(item => {
        const pcs = item.toOrder;
        const isSheet = item.category === 'Sheet';
        const bunkL = Math.min(Math.max(1.5, pcs * 0.012 + 1), 4.5); // length along truck
        const bunkW2 = Math.min(Math.max(1.2, pcs * 0.008 + 1), loadableWidth * 0.9); // width across truck
        const bunkH2 = isSheet ? Math.min(Math.max(0.5, pcs * 0.02), 2) : Math.min(Math.max(0.6, pcs * 0.008 + 0.3), 2.5);
        return { ...item, bunkL, bunkW: bunkW2, bunkH: bunkH2 };
    });

    // 2D bin-packing on the deck (X = along truck, Z = across truck)
    let curPX = deckStartX;
    let curPZ = -loadableWidth / 2 + 0.3;
    let rowMaxL = 0;
    const placedBunks = [];

    bunkModels.forEach(bm => {
        if (curPZ + bm.bunkW > loadableWidth / 2) {
            // Next row along the truck
            curPX += rowMaxL + 0.3;
            curPZ = -loadableWidth / 2 + 0.3;
            rowMaxL = 0;
        }
        if (curPX + bm.bunkL > deckStartX + loadableLength) return; // no more room

        placedBunks.push({ ...bm, placeX: curPX + bm.bunkL / 2, placeZ: curPZ + bm.bunkW / 2 });
        curPZ += bm.bunkW + 0.2;
        rowMaxL = Math.max(rowMaxL, bm.bunkL);
    });

    // Create 3D bunk meshes on the deck
    placedBunks.forEach(bm => {
        const bGroup = new THREE.Group();
        const isSheet = bm.category === 'Sheet';
        const colorHex = parseInt(bm.color.replace('#', ''), 16);

        // Dunnage (cradle sticks under bunk)
        const dunMat = new THREE.MeshStandardMaterial({ color: 0x555555, roughness: 0.6 });
        [-bm.bunkL * 0.3, bm.bunkL * 0.3].forEach(dx => {
            const dun = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, bm.bunkW + 0.1), dunMat);
            dun.position.set(dx, 0.04, 0);
            bGroup.add(dun);
        });

        if (isSheet) {
            // Stacked sheets
            const sheetH = 0.025;
            const gap = 0.005;
            const numSheets = Math.min(Math.floor(bm.bunkH / (sheetH + gap)), 40);
            const sMat = new THREE.MeshStandardMaterial({ color: colorHex, roughness: 0.7 });
            const sAlt = new THREE.MeshStandardMaterial({ color: darkenColor(colorHex, 0.9), roughness: 0.7 });
            for (let s = 0; s < numSheets; s++) {
                const sh = new THREE.Mesh(
                    new THREE.BoxGeometry(bm.bunkL - 0.1, sheetH, bm.bunkW - 0.05),
                    s % 2 === 0 ? sMat : sAlt
                );
                sh.position.y = 0.08 + s * (sheetH + gap) + sheetH / 2;
                sh.castShadow = true;
                sh.receiveShadow = true;
                bGroup.add(sh);
            }
        } else {
            // Stacked boards with sticker layers
            const boardH = 0.04;
            const boardGap = 0.008;
            const stickerEvery = 5;
            const numBoards = Math.min(Math.floor(bm.bunkH / (boardH + boardGap)), 30);
            const bMat = new THREE.MeshStandardMaterial({ color: colorHex, roughness: 0.85 });
            const bAlt = new THREE.MeshStandardMaterial({ color: darkenColor(colorHex, 0.9), roughness: 0.85 });
            const stMat = new THREE.MeshStandardMaterial({ color: 0x555566, roughness: 0.5 });

            let ly = 0.08;
            for (let b3 = 0; b3 < numBoards; b3++) {
                if (b3 > 0 && b3 % stickerEvery === 0) {
                    // Sticker separator
                    [-bm.bunkL * 0.3, 0, bm.bunkL * 0.3].forEach(sx => {
                        const st = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.03, bm.bunkW - 0.05), stMat);
                        st.position.set(sx, ly + 0.015, 0);
                        bGroup.add(st);
                    });
                    ly += 0.035;
                }
                // Row of boards
                const boardsAcross = Math.max(2, Math.floor(bm.bunkW / 0.15));
                const startZ2 = -bm.bunkW / 2 + 0.08;
                const spacing = (bm.bunkW - 0.16) / boardsAcross;
                for (let ba = 0; ba < boardsAcross; ba++) {
                    const bd = new THREE.Mesh(
                        new THREE.BoxGeometry(bm.bunkL - 0.15, boardH, spacing - 0.01),
                        (b3 + ba) % 2 === 0 ? bMat : bAlt
                    );
                    bd.position.set(0, ly + boardH / 2, startZ2 + ba * spacing + spacing / 2);
                    bd.castShadow = true;
                    bd.receiveShadow = true;
                    bGroup.add(bd);
                }
                ly += boardH + boardGap;
            }
        }

        // Banding straps
        const strapMat3 = new THREE.MeshStandardMaterial({ color: 0xF96302, roughness: 0.3, metalness: 0.6 });
        [-bm.bunkL * 0.25, bm.bunkL * 0.25].forEach(sx => {
            // Vertical straps (front and back)
            const vStrap = new THREE.Mesh(new THREE.BoxGeometry(0.02, bm.bunkH, 0.02), strapMat3);
            vStrap.position.set(sx, 0.08 + bm.bunkH / 2, bm.bunkW / 2 - 0.02);
            bGroup.add(vStrap);
            const vStrapB = new THREE.Mesh(new THREE.BoxGeometry(0.02, bm.bunkH, 0.02), strapMat3);
            vStrapB.position.set(sx, 0.08 + bm.bunkH / 2, -bm.bunkW / 2 + 0.02);
            bGroup.add(vStrapB);
            // Top strap
            const tStrap = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.02, bm.bunkW), strapMat3);
            tStrap.position.set(sx, 0.08 + bm.bunkH, 0);
            bGroup.add(tStrap);
        });

        // Label sprite
        const lblCanvas = document.createElement('canvas');
        lblCanvas.width = 256;
        lblCanvas.height = 64;
        const lblCtx = lblCanvas.getContext('2d');
        lblCtx.clearRect(0, 0, 256, 64);
        lblCtx.fillStyle = '#F96302';
        lblCtx.font = 'bold 20px monospace';
        lblCtx.textAlign = 'center';
        lblCtx.fillText(bm.name, 128, 24);
        lblCtx.fillStyle = '#ffffff';
        lblCtx.font = '16px monospace';
        lblCtx.fillText(bm.toOrder + ' pcs', 128, 48);
        const lblTex = new THREE.CanvasTexture(lblCanvas);
        lblTex.minFilter = THREE.LinearFilter;
        const lblSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: lblTex, transparent: true }));
        lblSprite.scale.set(2, 0.5, 1);
        lblSprite.position.set(0, bm.bunkH + 0.5, 0);
        bGroup.add(lblSprite);

        bGroup.position.set(bm.placeX + 2, deckTop, bm.placeZ);
        offScene.add(bGroup);
    });

    // ── 2D OVERLAY (title, weight, load bar) drawn after render ──
    offRenderer.render(offScene, offCamera);

    // Get the 3D render, then draw 2D text overlay on top
    const finalCanvas = document.createElement('canvas');
    finalCanvas.width = W;
    finalCanvas.height = H;
    const fCtx = finalCanvas.getContext('2d');
    fCtx.drawImage(offCanvas, 0, 0);

    // Title
    fCtx.fillStyle = '#F96302';
    fCtx.font = 'bold 20px monospace';
    fCtx.textAlign = 'center';
    fCtx.fillText('INCOMING DELIVERY — FLATBED LOADING PLAN', W / 2, 30);

    // Weight / utilization
    const totalW = items.reduce((s, i) => s + i.totalWeight, 0);
    const pctLoad = (totalW / TRUCK_MAX_LBS * 100).toFixed(1);
    fCtx.fillStyle = '#94a3b8';
    fCtx.font = '13px monospace';
    fCtx.fillText(
        `Total: ${totalW.toLocaleString()} lbs / ${TRUCK_MAX_LBS.toLocaleString()} lbs (${pctLoad}% loaded)  •  ${placedBunks.length} bunk${placedBunks.length !== 1 ? 's' : ''}`,
        W / 2, 52
    );

    // Load bar
    const barX = W / 2 - 220, barY2 = 60, barW2 = 440, barH2 = 10;
    fCtx.fillStyle = '#1a2233';
    fCtx.fillRect(barX, barY2, barW2, barH2);
    const lPct = Math.min(totalW / TRUCK_MAX_LBS, 1);
    fCtx.fillStyle = lPct > 0.9 ? '#ef4444' : lPct > 0.7 ? '#eab308' : '#22c55e';
    fCtx.fillRect(barX, barY2, barW2 * lPct, barH2);
    fCtx.strokeStyle = '#333';
    fCtx.lineWidth = 1;
    fCtx.strokeRect(barX, barY2, barW2, barH2);

    // Cleanup offscreen renderer
    offRenderer.dispose();

    return finalCanvas;
}

// ─── YARD HEALTH CHART ─────────────────────────────────────────
function buildYardChart() {
    const W = 900, H = 260;
    const canvas = document.createElement('canvas');
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = '#0f1629';
    ctx.fillRect(0, 0, W, H);

    ctx.fillStyle = '#F96302';
    ctx.font = 'bold 14px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('YARD INVENTORY STATUS — ALL BUNKS', W / 2, 22);

    const barW = Math.min(36, (W - 80) / bunkData.length - 4);
    const startX = 40;
    const barArea = H - 65;
    const baseY = H - 30;

    bunkData.forEach((b, i) => {
        const pct = b.current / b.capacity;
        const x = startX + i * (barW + 4);
        const h = barArea * pct;

        // Background bar
        ctx.fillStyle = '#1a2233';
        ctx.fillRect(x, baseY - barArea, barW, barArea);

        // Fill bar
        ctx.fillStyle = getFillColorCSS(pct);
        ctx.fillRect(x, baseY - h, barW, h);

        // Flagged border
        if (b.flagged) {
            ctx.strokeStyle = '#F96302';
            ctx.lineWidth = 2;
            ctx.strokeRect(x - 1, baseY - barArea - 1, barW + 2, barArea + 2);
        }

        // Label
        ctx.save();
        ctx.translate(x + barW / 2, baseY + 4);
        ctx.rotate(Math.PI / 4);
        ctx.fillStyle = '#94a3b8';
        ctx.font = '8px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(b.name.substring(0, 10), 0, 0);
        ctx.restore();
    });

    return canvas;
}

// ─── UTILITIES ─────────────────────────────────────────────────
function showStatus(msg, cls) {
    const el = document.getElementById('statusMsg');
    el.textContent = msg;
    el.className = 'pb-status ' + (cls || '');
}

// ─── START ─────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', init);
