import re

with open('frontend/app.js', 'r') as f:
    code = f.read()

# 1. async DOMContentLoaded
code = code.replace("document.addEventListener('DOMContentLoaded', () => {", "document.addEventListener('DOMContentLoaded', async () => {")

# 2. variables and modals
target_vars = """    const apiKeyInput = document.getElementById('api-key-input');
    const tabs = document.querySelectorAll('.tab');"""

replacement_vars = """    const authBtn = document.getElementById('auth-btn');
    const userTierBadge = document.getElementById('user-tier-badge');
    const tabs = document.querySelectorAll('.tab');

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
        userTierBadge.textContent = tier;
        if (tier !== 'Guest') {
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
    }"""

code = code.replace(target_vars, replacement_vars)

# 3. getApiKey inside logic
target_btn = """        const content = articleInput.value.trim();
        const apiKey = apiKeyInput.value.trim();

        if (!content) {
            showToast('Please paste an article first.', 'error');
            return;
        }

        if (!apiKey) {
            showToast('API Key is required.', 'error');
            return;
        }"""
        
replacement_btn = """        const content = articleInput.value.trim();
        const apiKey = getApiKey();

        if (!content) {
            showToast('Please paste an article first.', 'error');
            return;
        }

        if (!apiKey) {
            showToast('Session not initialized.', 'error');
            return;
        }"""
code = code.replace(target_btn, replacement_btn)

# 4. upgrade modal trigger
target_err = """            if (!response.ok) {
                let errMsg = 'Processing failed';
                try {
                    const errData = await response.json();
                    errMsg = errData.detail || errData.message || errMsg;
                } catch (e) {
                    errMsg = await response.text() || errMsg;
                }
                throw new Error(errMsg);
            }"""

replacement_err = """            if (!response.ok) {
                let errMsg = 'Processing failed';
                try {
                    const errData = await response.json();
                    errMsg = errData.detail || errData.message || errMsg;
                } catch (e) {
                    errMsg = await response.text() || errMsg;
                }
                
                if (errMsg === 'guest_limit_reached') {
                    showUpgradeModal('Guest Limit Reached', 'You have used your 3 free guest scans. Sign up now to get 10 free daily scans!', true);
                    return; // exit early without toast
                } else if (errMsg === 'daily_limit_reached') {
                    showUpgradeModal('Daily Limit Reached', 'You have used your 10 free scans. Request an unlock for unlimited access.', false);
                    return; // exit early without toast
                }
                throw new Error(errMsg);
            }"""
code = code.replace(target_err, replacement_err)

# 5. History API key
target_hist = "const apiKey = apiKeyInput.value.trim();"
replacement_hist = "const apiKey = getApiKey();"
code = code.replace(target_hist, replacement_hist)

with open('frontend/app.js', 'w') as f:
    f.write(code)

print("Patched app.js successfully")
