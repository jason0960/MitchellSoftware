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
            mode: 'creative',       // 'creative' | 'professional'
            scrolled: false,
            mobileMenuOpen: false,
            activeSection: 'home',
            typingActive: true
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
        }

        if (changed.includes('mobileMenuOpen')) {
            const hamburger = $('#hamburger');
            const navMenu = $('#navMenu');
            if (hamburger) hamburger.classList.toggle('open', props.mobileMenuOpen);
            if (navMenu) navMenu.classList.toggle('open', props.mobileMenuOpen);
        }
    }

    // Subscribe renderers
    AppState.subscribe(renderMode);
    AppState.subscribe(renderNavbar);

    // ============================================
    // Typing Effect — controlled by state
    // ============================================
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

    // ============================================
    // Cursor Glow — only in creative mode
    // ============================================
    const glow = $('#cursorGlow');
    if (glow) {
        document.addEventListener('mousemove', (e) => {
            if (AppState.props.isCreative) {
                glow.style.left = e.clientX + 'px';
                glow.style.top = e.clientY + 'px';
            }
        });
    }

    // ============================================
    // Event Handlers — dispatch state updates
    // ============================================

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

    // ============================================
    // Intersection Observer Reveals
    // ============================================
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

    // ============================================
    // Contact Form
    // ============================================
    const form = $('#contactForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = form.querySelector('.btn-primary');
            const origHTML = btn.innerHTML;
            const data = new FormData(form);

            console.log('Contact submission:', {
                name: data.get('name'),
                email: data.get('email'),
                message: data.get('message')
            });

            btn.innerHTML = '<i class="fas fa-check"></i> Sent!';
            btn.style.background = '#28c840';
            form.reset();

            setTimeout(() => {
                btn.innerHTML = origHTML;
                btn.style.background = '';
            }, 3000);
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
        '%cJason Mitchell — Software Engineer @ The Home Depot',
        'font-size: 12px; color: #7d8590; font-family: system-ui;'
    );

})();
