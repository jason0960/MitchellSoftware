/* ============================================
   AI Chat Bubble — Client Logic
   ============================================ */
(function () {
    'use strict';

    const API_BASE = '';  // same-origin — served by Flask

    // DOM refs
    const toggle = document.getElementById('chatToggle');
    const window_ = document.getElementById('chatWindow');
    const intro = document.getElementById('chatIntro');
    const startBtn = document.getElementById('chatStartBtn');
    const nameInput = document.getElementById('chatRecruiterName');
    const jobInput = document.getElementById('chatJobPosting');
    const messagesEl = document.getElementById('chatMessages');
    const inputArea = document.getElementById('chatInputArea');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSendBtn');

    // State
    let isOpen = false;
    let conversationId = '';
    let recruiterName = '';
    let jobPosting = '';
    let sending = false;

    // ── Toggle chat window ───────────────────────────────────
    toggle.addEventListener('click', () => {
        isOpen = !isOpen;
        toggle.classList.toggle('open', isOpen);
        window_.classList.toggle('visible', isOpen);

        if (isOpen && !conversationId) {
            nameInput.focus();
        } else if (isOpen && conversationId) {
            chatInput.focus();
        }
    });

    // ── Enable start button when name is entered ─────────────
    nameInput.addEventListener('input', () => {
        startBtn.disabled = !nameInput.value.trim();
    });

    // ── Start conversation ───────────────────────────────────
    startBtn.addEventListener('click', startConversation);
    nameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && nameInput.value.trim()) {
            startConversation();
        }
    });

    function startConversation() {
        recruiterName = nameInput.value.trim();
        jobPosting = jobInput.value.trim();

        if (!recruiterName) return;

        // Switch from intro to chat view
        intro.style.display = 'none';
        messagesEl.style.display = 'flex';
        inputArea.style.display = 'flex';

        // Welcome message
        addMessage('system', `Welcome, ${recruiterName}! Ask me anything about Jason's experience.`);

        if (jobPosting) {
            addMessage('system', 'Job posting received — I\'ll factor it into my answers.');
        }

        chatInput.focus();

        // If job posting provided, auto-send an initial assessment
        if (jobPosting) {
            sendMessage('Based on the job posting I shared, how well does Jason fit this role?');
        }
    }

    // ── Send message ─────────────────────────────────────────
    sendBtn.addEventListener('click', () => sendMessage());
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    function sendMessage(overrideText) {
        const text = overrideText || chatInput.value.trim();
        if (!text || sending) return;

        // Add user message to chat
        addMessage('user', text);
        chatInput.value = '';
        sending = true;
        sendBtn.disabled = true;

        // Show typing indicator
        const typingEl = showTyping();

        // Call the API
        fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            mode: 'cors',
            body: JSON.stringify({
                recruiter_name: recruiterName,
                message: text,
                conversation_id: conversationId,
                job_posting: !conversationId ? jobPosting : '',
            }),
        })
            .then(r => r.json())
            .then(data => {
                removeTyping(typingEl);

                if (data.error) {
                    addMessage('error', data.error);
                } else {
                    conversationId = data.conversation_id || conversationId;
                    addMessage('assistant', data.reply);
                }
            })
            .catch(err => {
                removeTyping(typingEl);
                addMessage('error', 'Connection failed. The server may be waking up — try again in a moment.');
                console.error('Chat error:', err);
            })
            .finally(() => {
                sending = false;
                sendBtn.disabled = false;
                chatInput.focus();
            });
    }

    // ── Message helpers ──────────────────────────────────────
    function addMessage(role, text) {
        const msg = document.createElement('div');
        msg.className = `chat-msg ${role}`;
        msg.textContent = text;
        messagesEl.appendChild(msg);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function showTyping() {
        const el = document.createElement('div');
        el.className = 'chat-typing';
        el.innerHTML = '<span></span><span></span><span></span>';
        messagesEl.appendChild(el);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        return el;
    }

    function removeTyping(el) {
        if (el && el.parentNode) {
            el.parentNode.removeChild(el);
        }
    }

})();
