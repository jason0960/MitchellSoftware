/* ============================================
   Jason Mitchell Portfolio — Script
   State-driven mode system with props
   ============================================ */

(function () {
    'use strict';

    // ---------- Helpers ----------
    const $ = (sel, ctx = document) => ctx.querySelector(sel);
    const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

    // ============================================
    // State Manager — reactive state with props
    // ============================================
    const AppState = {
        _state: {
            mode: 'creative',
            scrolled: false,
            mobileMenuOpen: false,
            activeSection: 'home',
            typingActive: true,
            whiteboard: false
        },

        _subscribers: [],

        // Props — derived values computed from state
        get props() {
            const s = this._state;
            return Object.freeze({
                mode: s.mode,
                isCreative: s.mode === 'creative',
                isProfessional: s.mode === 'professional',
                scrolled: s.scrolled,
                mobileMenuOpen: s.mobileMenuOpen,
                activeSection: s.activeSection,
                typingActive: s.typingActive && s.mode === 'creative',
                whiteboard: s.whiteboard && s.mode === 'creative',
                modeLabel: s.mode === 'creative' ? 'Creative' : 'Professional',
                bodyClass: s.mode === 'professional' ? 'professional' : ''
            });
        },

        // Get raw state value
        get(key) {
            return this._state[key];
        },

        // Update state and notify subscribers
        setState(updates) {
            const prev = { ...this._state };
            let changed = false;

            for (const [key, value] of Object.entries(updates)) {
                if (this._state[key] !== value) {
                    this._state[key] = value;
                    changed = true;
                }
            }

            if (changed) {
                const props = this.props;
                const changedKeys = Object.keys(updates).filter(k => prev[k] !== this._state[k]);
                this._subscribers.forEach(fn => fn(props, changedKeys));
            }
        },

        // Subscribe to state changes
        subscribe(fn) {
            this._subscribers.push(fn);
            return () => {
                this._subscribers = this._subscribers.filter(s => s !== fn);
            };
        },

        // Toggle a boolean state value
        toggle(key) {
            this.setState({ [key]: !this._state[key] });
        }
    };

    // ============================================
    // Renderers — subscribe to state, update DOM
    // ============================================

    // --- Mode Renderer ---
    function renderMode(props, changed) {
        if (!changed.includes('mode')) return;

        // Update body class
        document.body.classList.toggle('professional', props.isProfessional);

        // Turn off whiteboard when leaving creative
        if (props.isProfessional && AppState.get('whiteboard')) {
            AppState.setState({ whiteboard: false });
        }

        // Update toggle label
        const label = $('#modeLabel');
        if (label) label.textContent = props.modeLabel;

        // Swap hero button content
        const heroBtn = $('#heroBtn');
        if (heroBtn) {
            if (props.isProfessional) {
                heroBtn.innerHTML = '<i class="fas fa-briefcase"></i> View Experience';
            } else {
                heroBtn.innerHTML = '<i class="fas fa-terminal"></i> View My Work';
            }
        }

        // Persist preference
        localStorage.setItem('jm-portfolio-mode', props.mode);
    }

    // --- Navbar Renderer ---
    function renderNavbar(props, changed) {
        if (changed.includes('scrolled')) {
            const navbar = $('nav.navbar');
            if (navbar) navbar.classList.toggle('scrolled', props.scrolled);
        }

        if (changed.includes('activeSection')) {
            $$('.nav-link').forEach(link => {
                link.classList.toggle('active',
                    link.getAttribute('href') === '#' + props.activeSection
                );
            });
            $$('.editor-tab').forEach(tab => {
                tab.classList.toggle('active',
                    tab.getAttribute('href') === '#' + props.activeSection
                );
            });
        }

        if (changed.includes('mobileMenuOpen')) {
            const hamburger = $('#hamburger');
            const navMenu = $('#navMenu');
            if (hamburger) hamburger.classList.toggle('open', props.mobileMenuOpen);
            if (navMenu) navMenu.classList.toggle('open', props.mobileMenuOpen);
        }
    }

    // --- Whiteboard Renderer ---
    function renderWhiteboard(props, changed) {
        if (!changed.includes('whiteboard') && !changed.includes('mode')) return;

        document.body.classList.toggle('whiteboard-on', props.whiteboard);

        const btn = $('#whiteboardBtn');
        if (btn) btn.classList.toggle('active', props.whiteboard);

        if (props.whiteboard) {
            const overlay = $('#wbOverlay');
            if (overlay) overlay.style.height = document.documentElement.scrollHeight + 'px';
            requestAnimationFrame(positionAnnotations);
        }
    }

    function positionAnnotations() {
        const annotations = $$('.wb-annotation[data-target]');
        const sy = window.scrollY;
        const vw = window.innerWidth;
        const isMobile = vw <= 768;

        annotations.forEach(ann => {
            const targetId = ann.dataset.target;
            const target = document.getElementById(targetId);
            if (!target) return;

            const r = target.getBoundingClientRect();
            const absTop = r.top + sy;
            const absLeft = r.left;
            const centerX = absLeft + r.width / 2;
            const aw = ann.offsetWidth || 200;
            const ah = ann.offsetHeight || 60;

            // Reset special positioning
            ann.style.position = '';
            ann.style.right = '';
            ann.style.bottom = '';

            if (isMobile) {
                // On mobile, place all annotations below their target, clamped to viewport
                if (targetId === 'cursorGlow') return; // hidden via CSS on mobile
                ann.style.left = Math.max(4, Math.min(centerX - aw * 0.375, vw - aw * 0.75 - 4)) + 'px';
                ann.style.top = (absTop + r.height + 6) + 'px';
                return;
            }

            switch (targetId) {
                /* ---- BELOW-target annotations (arrow ↑ label) ---- */
                case 'modeToggle':
                    ann.style.left = Math.max(4, Math.min(centerX - aw / 2, vw - aw - 4)) + 'px';
                    ann.style.top = (absTop + r.height + 8) + 'px';
                    break;
                case 'navBrand':
                    ann.style.left = Math.max(4, absLeft) + 'px';
                    ann.style.top = (absTop + r.height + 8) + 'px';
                    break;
                case 'whiteboardBtn':
                    ann.style.left = Math.max(4, centerX - aw / 2) + 'px';
                    ann.style.top = (absTop + r.height + 8) + 'px';
                    break;
                case 'socialLinks':
                    ann.style.left = Math.max(4, absLeft) + 'px';
                    ann.style.top = (absTop + r.height + 8) + 'px';
                    break;

                /* ---- RIGHT-of-target annotations (arrow ← label) ---- */
                case 'editorTabs':
                    ann.style.left = Math.min(absLeft + r.width + 12, vw - aw - 4) + 'px';
                    ann.style.top = (absTop + r.height / 2 - ah / 2) + 'px';
                    break;
                case 'scrollHint':
                    ann.style.left = Math.min(absLeft + r.width + 12, vw - aw - 4) + 'px';
                    ann.style.top = (absTop + r.height / 2 - ah / 2) + 'px';
                    break;
                case 'timeline':
                    ann.style.left = Math.min(absLeft + r.width + 12, vw - aw - 4) + 'px';
                    ann.style.top = (absTop + 40) + 'px';
                    break;

                /* ---- LEFT-of-target annotations (label arrow →) ---- */
                case 'typedText':
                    ann.style.left = Math.max(4, absLeft - aw - 12) + 'px';
                    ann.style.top = (absTop - 4) + 'px';
                    break;
                case 'heroTagline':
                    ann.style.left = Math.max(4, absLeft - aw - 12) + 'px';
                    ann.style.top = (absTop - 4) + 'px';
                    break;

                /* ---- ABOVE-target annotations (label arrow ↓) ---- */
                case 'workGrid':
                    ann.style.left = (absLeft + 20) + 'px';
                    ann.style.top = (absTop - ah - 8) + 'px';
                    break;
                case 'skillsGrid':
                    ann.style.left = (absLeft + 20) + 'px';
                    ann.style.top = (absTop - ah - 8) + 'px';
                    break;
                case 'contactForm':
                    ann.style.left = (absLeft + r.width * 0.55) + 'px';
                    ann.style.top = (absTop - ah - 8) + 'px';
                    break;

                /* ---- FIXED annotation ---- */
                case 'cursorGlow':
                    ann.style.position = 'fixed';
                    ann.style.right = '2rem';
                    ann.style.bottom = '5rem';
                    ann.style.left = 'auto';
                    ann.style.top = 'auto';
                    break;
            }
        });
    }

    // Reposition on scroll (needed for fixed-navbar elements) & resize
    window.addEventListener('scroll', () => {
        if (AppState.props.whiteboard) requestAnimationFrame(positionAnnotations);
    });
    window.addEventListener('resize', () => {
        if (AppState.props.whiteboard) requestAnimationFrame(positionAnnotations);
    });

    // Subscribe renderers
    AppState.subscribe(renderMode);
    AppState.subscribe(renderNavbar);
    AppState.subscribe(renderWhiteboard);

    const typedEl = $('#typedText');
    let typingTimeout = null;

    if (typedEl) {
        const strings = [
            'Software Engineer',
            'Java & React Developer',
            'Full Stack Engineer',
            'Python Automation Builder',
            'DevOps & CI/CD Contributor'
        ];
        let stringIndex = 0;
        let charIndex = 0;
        let deleting = false;
        const typeSpeed = 80;
        const deleteSpeed = 40;
        const pauseEnd = 2000;
        const pauseStart = 500;

        function type() {
            // Only run in creative mode
            if (!AppState.props.typingActive) {
                typingTimeout = setTimeout(type, 500);
                return;
            }

            const current = strings[stringIndex];
            if (!deleting) {
                typedEl.textContent = current.substring(0, charIndex + 1);
                charIndex++;
                if (charIndex === current.length) {
                    typingTimeout = setTimeout(() => { deleting = true; type(); }, pauseEnd);
                    return;
                }
            } else {
                typedEl.textContent = current.substring(0, charIndex - 1);
                charIndex--;
                if (charIndex === 0) {
                    deleting = false;
                    stringIndex = (stringIndex + 1) % strings.length;
                    typingTimeout = setTimeout(type, pauseStart);
                    return;
                }
            }
            typingTimeout = setTimeout(type, deleting ? deleteSpeed : typeSpeed);
        }

        setTimeout(type, 1000);
    }

    const glow = $('#cursorGlow');
    if (glow) {
        document.addEventListener('mousemove', (e) => {
            if (AppState.props.isCreative) {
                glow.style.left = e.clientX + 'px';
                glow.style.top = e.clientY + 'px';
            }
        });
    }

    // --- Scroll Handler ---
    let scrollTicking = false;
    window.addEventListener('scroll', () => {
        if (!scrollTicking) {
            requestAnimationFrame(() => {
                const y = window.scrollY;
                const sections = $$('section[id]');
                let current = 'home';

                sections.forEach(section => {
                    if (y >= section.offsetTop - 200) {
                        current = section.id;
                    }
                });

                AppState.setState({
                    scrolled: y > 40,
                    activeSection: current
                });

                scrollTicking = false;
            });
            scrollTicking = true;
        }
    });

    // --- Mode Toggle ---
    const toggleBtn = $('#modeToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const next = AppState.props.isCreative ? 'professional' : 'creative';
            AppState.setState({ mode: next });
        });
    }

    // --- Whiteboard Toggle ---
    const wbBtn = $('#whiteboardBtn');
    if (wbBtn) {
        wbBtn.addEventListener('click', () => {
            AppState.toggle('whiteboard');
        });
    }

    // --- Mobile Menu ---
    const hamburger = $('#hamburger');
    const navMenu = $('#navMenu');

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            AppState.toggle('mobileMenuOpen');
        });

        $$('.nav-link', navMenu).forEach(link => {
            link.addEventListener('click', () => {
                AppState.setState({ mobileMenuOpen: false });
            });
        });
    }

    // --- Smooth Scroll ---
    $$('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = $(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    $$('.reveal').forEach((el, i) => {
        el.style.transitionDelay = (i * 0.08) + 's';
        revealObserver.observe(el);
    });

    const EMAILJS_PUBLIC_KEY = 'ImyXAHd9l808uQoki';
    const EMAILJS_SERVICE_ID = 'service_k5gog04';
    const EMAILJS_TEMPLATE_ID = 'template_a2sf6bc';

    // Initialize EmailJS
    if (window.emailjs) {
        emailjs.init(EMAILJS_PUBLIC_KEY);
    }

    const form = $('#contactForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = form.querySelector('.btn-primary');
            const origHTML = btn.innerHTML;

            // Disable button while sending
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

            const templateParams = {
                from_name: form.querySelector('#name').value,
                from_email: form.querySelector('#email').value,
                message: form.querySelector('#message').value
            };

            emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, templateParams)
                .then(() => {
                    btn.innerHTML = '<i class="fas fa-check"></i> Sent!';
                    btn.style.background = '#28c840';
                    form.reset();

                    setTimeout(() => {
                        btn.innerHTML = origHTML;
                        btn.style.background = '';
                        btn.disabled = false;
                    }, 3000);
                })
                .catch((error) => {
                    console.error('EmailJS error:', error);
                    btn.innerHTML = '<i class="fas fa-times"></i> Failed';
                    btn.style.background = '#ef4444';

                    setTimeout(() => {
                        btn.innerHTML = origHTML;
                        btn.style.background = '';
                        btn.disabled = false;
                    }, 3000);
                });
        });
    }

    // ============================================
    // Initialize — restore saved mode
    // ============================================
    const savedMode = localStorage.getItem('jm-portfolio-mode');
    if (savedMode === 'professional' || savedMode === 'creative') {
        AppState.setState({ mode: savedMode });
    }

    // ============================================
    // Console Signature
    // ============================================
    console.log(
        '%c{ JM }',
        'font-size: 28px; font-weight: 700; color: #F96302; font-family: monospace;'
    );
    console.log(
        '%cJason Mitchell — Software Engineer',
        'font-size: 12px; color: #7d8590; font-family: system-ui;'
    );

    // ============================================
    // Prometheus Tracking — Portfolio Analytics
    // ============================================
    const API_BASE = 'https://mitchellsoftwareportfolio.onrender.com';

    function trackEvent(event) {
        fetch(`${API_BASE}/api/track`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            mode: 'cors',
            body: JSON.stringify({ event }),
        }).catch(() => {});
    }

    // Track portfolio page view (once per session)
    if (!sessionStorage.getItem('tracked-portfolio-view')) {
        trackEvent('portfolio_view');
        sessionStorage.setItem('tracked-portfolio-view', '1');
    }

    // Fetch and display live stats
    function loadStats() {
        fetch(`${API_BASE}/api/stats`, { mode: 'cors' })
            .then(r => r.json())
            .then(data => {
                const el = (id, val) => {
                    const e = document.getElementById(id);
                    if (e) e.textContent = typeof val === 'number' ? val.toLocaleString() : val;
                };
                el('statViews', data.portfolio_views || 0);
                el('statDemos', data.demo_views || 0);
                el('statPdfs', data.pdf_generations || 0);
                el('statVotes', data.resume_enjoyed || 0);

                // Health metrics
                if (data.health) {
                    el('statUptime', data.health.uptime_display || '—');
                    el('statMemory', data.health.memory_mb || '—');
                    el('statCpu', data.health.cpu_percent + '%');
                    el('statSessions', data.health.active_sessions || 0);
                }
            })
            .catch(() => {});
    }
    loadStats();

    // "Enjoyed this?" vote button
    const enjoyedBtn = document.getElementById('enjoyedBtn');
    if (enjoyedBtn) {
        if (localStorage.getItem('jm-enjoyed-voted')) {
            enjoyedBtn.innerHTML = '<i class="fas fa-check"></i> Thanks!';
            enjoyedBtn.classList.add('voted');
            enjoyedBtn.disabled = true;
        }
        enjoyedBtn.addEventListener('click', () => {
            trackEvent('resume_enjoyed');
            enjoyedBtn.innerHTML = '<i class="fas fa-check"></i> Thanks!';
            enjoyedBtn.classList.add('voted');
            enjoyedBtn.disabled = true;
            localStorage.setItem('jm-enjoyed-voted', '1');
            // Refresh stats after a short delay
            setTimeout(loadStats, 500);
        });
    }

})();
