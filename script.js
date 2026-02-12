(function () {
    'use strict';

    const $ = (sel, ctx = document) => ctx.querySelector(sel);
    const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

    // State manager
    const AppState = {
        _state: {
            mode: 'creative',
            scrolled: false,
            mobileMenuOpen: false,
            activeSection: 'home',
            typingActive: true
        },

        _subscribers: [],

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

        get(key) {
            return this._state[key];
        },

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

        subscribe(fn) {
            this._subscribers.push(fn);
            return () => {
                this._subscribers = this._subscribers.filter(s => s !== fn);
            };
        },

        toggle(key) {
            this.setState({ [key]: !this._state[key] });
        }
    };

    // Mode renderer — handles theme switching
    function renderMode(props, changed) {
        if (!changed.includes('mode')) return;

        document.body.classList.toggle('professional', props.isProfessional);

        const label = $('#modeLabel');
        if (label) label.textContent = props.modeLabel;

        const heroBtn = $('#heroBtn');
        if (heroBtn) {
            if (props.isProfessional) {
                heroBtn.innerHTML = '<i class="fas fa-briefcase"></i> View Experience';
            } else {
                heroBtn.innerHTML = '<i class="fas fa-terminal"></i> View My Work';
            }
        }

        localStorage.setItem('jm-portfolio-mode', props.mode);
    }

    // Navbar renderer — scroll state + active link + mobile menu
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

    AppState.subscribe(renderMode);
    AppState.subscribe(renderNavbar);

    // Typing effect
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

        function type() {
            if (!AppState.props.typingActive) {
                typingTimeout = setTimeout(type, 500);
                return;
            }

            const current = strings[stringIndex];
            if (!deleting) {
                typedEl.textContent = current.substring(0, charIndex + 1);
                charIndex++;
                if (charIndex === current.length) {
                    typingTimeout = setTimeout(() => { deleting = true; type(); }, 2000);
                    return;
                }
            } else {
                typedEl.textContent = current.substring(0, charIndex - 1);
                charIndex--;
                if (charIndex === 0) {
                    deleting = false;
                    stringIndex = (stringIndex + 1) % strings.length;
                    typingTimeout = setTimeout(type, 500);
                    return;
                }
            }
            typingTimeout = setTimeout(type, deleting ? 40 : 80);
        }

        setTimeout(type, 1000);
    }

    // Cursor glow (creative mode only)
    const glow = $('#cursorGlow');
    if (glow) {
        document.addEventListener('mousemove', (e) => {
            if (AppState.props.isCreative) {
                glow.style.left = e.clientX + 'px';
                glow.style.top = e.clientY + 'px';
            }
        });
    }

    // Scroll tracking
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

    // Mode toggle
    const toggleBtn = $('#modeToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const next = AppState.props.isCreative ? 'professional' : 'creative';
            AppState.setState({ mode: next });
        });
    }

    // Mobile menu
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

    // Smooth scroll
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

    // Scroll reveal
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

    // EmailJS contact form
    const EMAILJS_PUBLIC_KEY = 'ImyXAHd9l808uQoki';
    const EMAILJS_SERVICE_ID = 'service_k5gog04';
    const EMAILJS_TEMPLATE_ID = 'template_a2sf6bc';

    if (window.emailjs) {
        emailjs.init(EMAILJS_PUBLIC_KEY);
    }

    const form = $('#contactForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = form.querySelector('.btn-primary');
            const origHTML = btn.innerHTML;

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

    // Restore saved mode
    const savedMode = localStorage.getItem('jm-portfolio-mode');
    if (savedMode === 'professional' || savedMode === 'creative') {
        AppState.setState({ mode: savedMode });
    }

    console.log(
        '%c{ JM }',
        'font-size: 28px; font-weight: 700; color: #F96302; font-family: monospace;'
    );
    console.log(
        '%cJason Mitchell — Software Engineer @ The Home Depot',
        'font-size: 12px; color: #7d8590; font-family: system-ui;'
    );

})();
