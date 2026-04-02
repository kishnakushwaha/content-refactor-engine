document.addEventListener('DOMContentLoaded', async () => {
    const processBtn = document.getElementById('process-btn');
    const articleInput = document.getElementById('article-input');
    const wordCount = document.getElementById('input-word-count');
    const authBtn = document.getElementById('auth-btn');
    const userTierBadge = document.getElementById('user-tier-badge');
    const tabs = document.querySelectorAll('.tab');

    // Modals
    const authModal = document.getElementById('auth-modal');
    const upgradeModal = document.getElementById('upgrade-modal');
    const submitAuthBtn = document.getElementById('submit-auth-btn');
    const authEmailInput = document.getElementById('auth-email-input');

    await checkSession();

    function getApiKey() {
        return localStorage.getItem('cre_api_key');
    }

    function setApiKey(key, tier) {
        localStorage.setItem('cre_api_key', key);
        if (userTierBadge) userTierBadge.textContent = tier;
        if (tier !== 'Guest' && authBtn) {
            authBtn.style.display = 'none';
        }
    }

    async function checkSession() {
        const key = getApiKey();
        if (!key) {
            try {
                const res = await fetch('/api/guest-session', { method: 'POST' });
                const data = await res.json();
                if (data.api_key) setApiKey(data.api_key, 'Guest');
            } catch (e) { console.error('Failed to init guest', e); }
        } else {
            if (key.includes('guest')) setApiKey(key, 'Guest');
            else setApiKey(key, 'Free');
        }
    }

    // Modal UI Handlers
    authBtn?.addEventListener('click', () => authModal.classList.remove('hidden'));
    document.getElementById('close-auth-modal')?.addEventListener('click', () => authModal.classList.add('hidden'));
    document.getElementById('close-upgrade-modal')?.addEventListener('click', () => upgradeModal.classList.add('hidden'));

    submitAuthBtn?.addEventListener('click', async () => {
        const email = authEmailInput.value.trim();
        if (!email) return showToast('Enter an email', 'error');
        submitAuthBtn.textContent = 'Wait...';
        
        try {
            const res = await fetch('/api/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, current_guest_key: getApiKey() })
            });
            const data = await res.json();
            if (res.ok) {
                setApiKey(data.api_key, 'Free');
                authModal.classList.add('hidden');
                showToast('Signup successful!');
                if (document.getElementById('tab-history').classList.contains('active')) loadHistory();
            } else throw new Error(data.detail);
        } catch(e) { showToast(e.message, 'error'); }
        submitAuthBtn.textContent = 'Continue';
    });

    function showUpgradeModal(title, message, isGuest) {
        document.getElementById('upgrade-title').textContent = title;
        document.getElementById('upgrade-message').textContent = message;
        
        const actions = document.getElementById('upgrade-actions-container');
        if (isGuest) {
            actions.innerHTML = `<button class="primary-btn w-100" onclick="document.getElementById('upgrade-modal').classList.add('hidden'); document.getElementById('auth-modal').classList.remove('hidden');">Sign Up Free</button>`;
        } else {
            actions.innerHTML = `<a href="mailto:admin@cre.com?subject=Limit%20Increase%20Request" class="primary-btn w-100" style="text-decoration:none; display:inline-block; text-align:center;">Request Unlock</a>`;
        }
        upgradeModal.classList.remove('hidden');
    }

    // UI Elements
    const emptyState = document.getElementById('empty-state');
    const progressPanel = document.getElementById('progress-panel');
    const reportResults = document.getElementById('report-results');
    const outputHtml = document.getElementById('output-html');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');

    // Progress Elements
    const progressSteps = document.getElementById('progress-steps');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressPercent = document.getElementById('progress-percent');

    // Step configuration matching backend progress_callback steps
    const STEP_CONFIG = {
        extracting: { label: 'Breaking down your text for in-depth analysis...', icon: '📝', percent: 10 },
        searching: { label: 'Analyzing billions of web pages for matching content...', icon: '🔍', percent: 30 },
        comparing: { label: 'Scanning millions of publications for potential matches...', icon: '📊', percent: 50 },
        analyzing: { label: 'Ensuring your content is uniquely yours...', icon: '🧠', percent: 70 },
        rewriting: { label: 'Analyzing for advanced rewording and paraphrasing...', icon: '✍️', percent: 85 },
        finalizing: { label: 'Generating your comprehensive report...', icon: '📋', percent: 95 },
        complete: { label: 'Analysis complete!', icon: '✅', percent: 100 }
    };

    // Live word count
    articleInput.addEventListener('input', () => {
        const words = articleInput.value.trim().split(/\s+/).filter(w => w.length > 0).length;
        wordCount.textContent = `${words} words`;
    });

    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');

            // Load history when History tab is clicked
            if (tab.dataset.tab === 'history') {
                loadHistory();
            }
        });
    });

    // =============================
    // SSE STREAMING PROCESS
    // =============================
    processBtn.addEventListener('click', async () => {
        const content = articleInput.value.trim();
        const apiKey = getApiKey();

        if (!content) {
            showToast('Please paste an article first.', 'error');
            return;
        }

        if (!apiKey) {
            showToast('Session not initialized. Refresh page.', 'error');
            return;
        }

        // Set Loading State
        processBtn.disabled = true;
        btnText.textContent = 'Processing...';
        loader.classList.remove('hidden');

        // Show progress panel
        emptyState.classList.add('hidden');
        reportResults.classList.add('hidden');
        progressPanel.classList.remove('hidden');
        progressSteps.innerHTML = '';
        progressBarFill.style.width = '0%';
        progressPercent.textContent = 'Loading... 0%';

        // Switch to Analysis tab
        tabs.forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tabs[0].classList.add('active');
        document.getElementById('tab-report').classList.add('active');

        let completedSteps = [];

        try {
            const response = await fetch('/api/process-stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': apiKey
                },
                body: JSON.stringify({ content })
            });

            if (!response.ok) {
                let errMsg = 'Processing failed';
                try {
                    const errData = await response.json();
                    errMsg = errData.detail || errData.message || errMsg;
                } catch (e) {
                    errMsg = await response.text() || errMsg;
                }
                
                if (errMsg === 'guest_limit_reached') {
                    showUpgradeModal('Guest Limit Reached', 'You have used your 3 free guest scans. Sign up now to get 10 free daily scans!', true);
                    throw new Error('Limit reached');
                } else if (errMsg === 'daily_limit_reached') {
                    showUpgradeModal('Daily Limit Reached', 'You have used your 10 free daily scans. Request an unlock for unlimited access.', false);
                    throw new Error('Limit reached');
                }
                
                throw new Error(errMsg);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    const jsonStr = line.slice(6).trim();
                    if (!jsonStr) continue;

                    try {
                        const event = JSON.parse(jsonStr);

                        if (event.step === 'complete') {
                            // Mark all steps as done
                            document.querySelectorAll('.progress-step').forEach(s => {
                                s.classList.remove('active');
                                s.classList.add('done');
                                const icon = s.querySelector('.step-icon');
                                icon.classList.remove('active');
                                icon.classList.add('done');
                                icon.innerHTML = '<span class="check">✓</span>';
                            });
                            progressBarFill.style.width = '100%';
                            progressPercent.textContent = 'Loading... 100%';

                            // Short delay then show results
                            await new Promise(r => setTimeout(r, 800));
                            progressPanel.classList.add('hidden');
                            renderReport(event.result);
                            showToast('Refactoring complete!');
                        } else {
                            // Mark previous steps as done
                            document.querySelectorAll('.progress-step.active').forEach(s => {
                                s.classList.remove('active');
                                s.classList.add('done');
                                const icon = s.querySelector('.step-icon');
                                icon.classList.remove('active');
                                icon.classList.add('done');
                                icon.innerHTML = '<span class="check">✓</span>';
                            });

                            // Add new active step
                            const config = STEP_CONFIG[event.step] || { label: event.message, icon: '⚡', percent: 50 };
                            addProgressStep(config.icon, event.message || config.label, true);
                            progressBarFill.style.width = config.percent + '%';
                            progressPercent.textContent = `Loading... ${config.percent}%`;
                        }
                    } catch (e) {
                        // Skip malformed events
                    }
                }
            }

        } catch (error) {
            progressPanel.classList.add('hidden');
            emptyState.classList.remove('hidden');
            showToast(error.message, 'error');
        } finally {
            processBtn.disabled = false;
            btnText.textContent = 'Analyze & Refactor';
            loader.classList.add('hidden');
        }
    });

    function addProgressStep(icon, text, isActive) {
        const step = document.createElement('div');
        step.className = `progress-step ${isActive ? 'active' : ''}`;
        step.innerHTML = `
            <div class="step-icon ${isActive ? 'active' : 'done'}">
                ${isActive ? '<div class="spinner"></div>' : '<span class="check">✓</span>'}
            </div>
            <span class="step-text">${text}</span>
        `;
        progressSteps.appendChild(step);

        // Auto-scroll to latest step
        step.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // =============================
    // RENDER REPORT
    // =============================
    function renderReport(data) {
        reportResults.classList.remove('hidden');

        const report = data.report || {};

        const isPlagiarismDetected = report.similarity_score !== "No significant matches found.";
        const simScoreNum = isPlagiarismDetected ? parseInt(report.similarity_score) : 0;

        // Update Meters
        document.getElementById('sim-score').textContent = isPlagiarismDetected ? report.similarity_score : "0%";
        document.getElementById('sim-fill').style.width = isPlagiarismDetected ? report.similarity_score : "0%";

        // Color coding similarity
        const simFill = document.getElementById('sim-fill');
        if (simScoreNum > 80) simFill.style.backgroundColor = 'var(--danger)';
        else if (simScoreNum > 40) simFill.style.backgroundColor = 'var(--warning)';
        else simFill.style.backgroundColor = 'var(--success)';

        document.getElementById('orig-score').textContent = report.originality_score || "--%";
        document.getElementById('orig-fill').style.width = report.originality_score || "0%";

        const trust = report.trust_score || "0/10";
        document.getElementById('trust-score').textContent = trust.split('/')[0];
        document.getElementById('trust-fill').style.width = `${(parseInt(trust) / 10) * 100}%`;

        // Qualitative Badges
        const riskBadge = document.getElementById('risk-badge');
        const safety = report.adsense_safety || "--";
        riskBadge.textContent = safety;
        riskBadge.className = 'badge';
        if (safety.toLowerCase().includes('high')) riskBadge.classList.add('risk');
        else if (safety.toLowerCase().includes('medium')) riskBadge.classList.add('warn');
        else riskBadge.classList.add('safe');

        // Plagiarism Risk Badge
        const plagBadge = document.getElementById('plag-badge');
        const plagRisk = report.plagiarism_risk || "--";
        plagBadge.textContent = plagRisk;
        plagBadge.className = 'badge';
        if (plagRisk.toLowerCase().includes('high')) plagBadge.classList.add('risk');
        else if (plagRisk.toLowerCase().includes('medium')) plagBadge.classList.add('warn');
        else plagBadge.classList.add('safe');

        document.getElementById('idea-badge').textContent = report.idea_similarity || "--";
        document.getElementById('value-badge').textContent = report.value_addition || "--";

        // SEO Score
        document.getElementById('seo-score').textContent = report.seo_score || "--%";
        document.getElementById('seo-fill').style.width = report.seo_score || "0%";

        // Matched References (top 5)
        const refsList = document.getElementById('refs-list');
        const refs = report.matched_references || [];
        if (refs.length > 0) {
            refsList.innerHTML = refs.map(ref =>
                `<a href="${ref.url}" target="_blank" class="ref-link">
                    <span class="ref-score">${ref.score}</span>
                    <span class="ref-url">${ref.url}</span>
                </a>`
            ).join('');
        } else {
            refsList.innerHTML = '<span class="text-muted">None detected</span>';
        }

        // Output HTML
        outputHtml.innerHTML = data.final_html || "<i>No content returned.</i>";
    }

    // =============================
    // HISTORY
    // =============================
    async function loadHistory() {
        const apiKey = getApiKey();
        if (!apiKey) return;

        const historyEmpty = document.getElementById('history-empty');
        const historyList = document.getElementById('history-list');

        try {
            const response = await fetch('/api/history', {
                headers: { 'X-API-Key': apiKey }
            });

            if (!response.ok) return;

            const data = await response.json();
            const history = data.history || [];

            if (history.length === 0) {
                historyEmpty.classList.remove('hidden');
                historyList.classList.add('hidden');
                return;
            }

            historyEmpty.classList.add('hidden');
            historyList.classList.remove('hidden');
            historyList.innerHTML = '';

            for (const item of history) {
                const simStr = item.semantic_similarity_score || '0%';
                const sim = parseInt(simStr) || 0;
                const scoreClass = sim > 70 ? 'high' : sim > 30 ? 'mid' : 'low';
                const date = item.created_at ? new Date(item.created_at).toLocaleString() : 'Unknown';
                const preview = (item.original_content || '').substring(0, 120) + '...';

                const el = document.createElement('div');
                el.className = 'history-item';
                el.innerHTML = `
                    <div class="history-meta">
                        <span class="history-date">${date}</span>
                        <span class="history-score ${scoreClass}">${sim}% similar</span>
                    </div>
                    <p class="history-preview">${preview}</p>
                `;
                historyList.appendChild(el);
            }

        } catch (err) {
            console.error('History load failed:', err);
        }
    }

    // =============================
    // TOASTS
    // =============================
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
});
