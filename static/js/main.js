document.addEventListener('DOMContentLoaded', () => {
    // Hamburger Menu
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
            if (navLinks.style.display === 'flex') {
                navLinks.style.flexDirection = 'column';
                navLinks.style.position = 'absolute';
                navLinks.style.top = '70px';
                navLinks.style.left = '0';
                navLinks.style.width = '100%';
                navLinks.style.backgroundColor = '#fff';
                navLinks.style.padding = '1rem';
                navLinks.style.boxShadow = '0 4px 6px -1px rgb(0 0 0 / 0.1)';
            }
        });
    }

    // Prediction Form Handling with Modal
    const form = document.getElementById('predictionForm');

    // Modal Elements
    const modal = document.getElementById('predictionModal');
    const closeModalBtn = document.getElementById('closeModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalPercentage = document.getElementById('modalPercentage');
    const modalMessage = document.getElementById('modalMessage');
    const modalActions = document.getElementById('modalActions');
    const modalBox = document.querySelector('.modal-box');
    const circlePath = document.getElementById('riskCirclePath');
    const modalIconArea = document.getElementById('modalIconArea');

    // Close Modal Logic
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    // Close on click outside
    window.addEventListener('click', (e) => {
        if (e.target == modal) {
            modal.style.display = 'none';
        }
    });

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = form.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerText;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            submitBtn.disabled = true;

            const formData = new FormData(form);

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    // Populate Modal
                    modal.style.display = 'flex';

                    // Reset Animation
                    modalBox.style.animation = 'none';
                    modalBox.offsetHeight; /* trigger reflow */
                    modalBox.style.animation = 'scaleUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards';

                    // Parse Probability
                    const probability = data.probability !== null ? parseFloat(data.probability) : 0;
                    console.log("DEBUG: Received Probability:", probability);

                    // Update Circle Chart
                    const dashArray = `${probability}, 100`;
                    circlePath.setAttribute('stroke-dasharray', dashArray);

                    // Animate Number logic
                    let start = 0;
                    const duration = 1200;
                    const stepTime = 20;
                    const steps = duration / stepTime;
                    const increment = probability / steps;

                    if (probability > 0) {
                        const timer = setInterval(() => {
                            start += increment;
                            if (start >= probability) {
                                start = probability;
                                clearInterval(timer);
                            }
                            // Show decimals if very small, else whole number
                            const displayVal = probability < 1 ? start.toFixed(2) : (probability < 10 ? start.toFixed(1) : Math.round(start));
                            modalPercentage.textContent = displayVal + "%";
                        }, stepTime);
                    } else {
                        modalPercentage.textContent = "0%";
                    }

                    // clear previous themes
                    modalBox.classList.remove('theme-high', 'theme-low');

                    // Heart Age Elements
                    const ageGap = data.heart_age - data.chronological_age;
                    let ageColor = ageGap > 0 ? "red" : (ageGap < 0 ? "green" : "blue");
                    let ageSymbol = ageGap > 0 ? `+${ageGap}` : (ageGap < 0 ? `${ageGap}` : "Opt");

                    // Metrics Grid (Horizontal Cards)
                    const metricsHtml = `
                        <div class="modal-metrics-grid">
                            <div class="stat-card">
                                <div class="stat-icon orange"><i class="fas fa-percentage"></i></div>
                                <div class="stat-label">Prediction Risk</div>
                                <div class="stat-value" id="modalPercentagePremium">0%</div>
                                <div class="reboot-vital" style="font-size: 0.6rem">AI Confidence</div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-icon ${ageColor}"><i class="fas fa-heartbeat"></i></div>
                                <div class="stat-label">Heart Age</div>
                                <div class="stat-value">${data.heart_age} <span style="font-size: 1rem; color: #64748b">yrs</span></div>
                                <div class="vital-tag">${ageSymbol} Gap</div>
                            </div>

                            <div class="stat-card">
                                <div class="stat-icon ${data.prediction === 1 ? 'red' : 'green'}">
                                    <i class="fas ${data.prediction === 1 ? 'fa-shield-virus' : 'fa-shield-alt'}"></i>
                                </div>
                                <div class="stat-label">Health Status</div>
                                <div class="stat-value" style="font-size: 1.25rem; padding: 0.75rem 0;">
                                    ${data.prediction === 1 ? 'CAUTION' : 'SECURE'}
                                </div>
                                <div class="reboot-vital" style="font-size: 0.6rem">Clinical Level</div>
                            </div>
                        </div>
                    `;

                    // Build Reboot Plan HTML (Enhanced)
                    const rebootRows = data.reboot_plan.map(d => `
                        <tr>
                            <td><span class="day-label">${d.day}</span></td>
                            <td class="reboot-desc">${d.activity}</td>
                            <td class="reboot-desc">${d.diet}</td>
                        </tr>
                    `).join('');

                    const rebootPlanHtml = `
                        <div class="reboot-scroll-zone">
                            <table class="reboot-grid">
                                <thead><tr><th>Timeline</th><th>Daily Roadmap</th><th>Nutrition Focus</th></tr></thead>
                                <tbody>${rebootRows}</tbody>
                            </table>
                        </div>
                    `;

                    // Main Modal Assembly
                    modalBox.className = 'modal-content-premium'; // Upgrade to premium
                    modalBox.classList.add(data.prediction === 1 ? 'theme-high' : 'theme-low');

                    modalMessage.innerHTML = `
                        <div class="premium-modal-header">
                            <i class="fas ${data.prediction === 1 ? 'fa-heart-pulse text-red-600' : 'fa-shield-heart text-green-600'}"></i>
                            <h2 class="${data.prediction === 1 ? 'text-red-800' : 'text-green-800'}">
                                ${data.prediction === 1 ? 'Cardiac Risk Assessment' : 'Heart Health Verified'}
                            </h2>
                        </div>

                        <div class="risk-alert-banner">
                            <i class="fas ${data.prediction === 1 ? 'fa-exclamation-circle' : 'fa-check-circle'}" style="font-size: 1.5rem"></i>
                            <span>${data.prediction === 1 ? 'Clinical Risk Detected: Please review your personalized 7-day reboot plan immediately.' : 'Excellent Vitals: Your cardiovascular profile is within the healthy range. Optimize further below.'}</span>
                        </div>

                        <div class="modal-tabs">
                            <button class="modal-tab active" data-tab="summary">Metrics Summary</button>
                            <button class="modal-tab" data-tab="reboot">7-Day Action Blueprint</button>
                        </div>

                        <div id="tab-summary" class="tab-pane active">
                            ${metricsHtml}
                            <p id="finalAdvice" style="margin-top: 1.5rem; color: #475569; line-height: 1.6; font-size: 0.95rem;"></p>
                        </div>

                        <div id="tab-reboot" class="tab-pane">
                            ${rebootPlanHtml}
                        </div>
                    `;

                    const finalAdvice = document.getElementById('finalAdvice');
                    if (data.prediction === 1) {
                        modalBox.classList.add('theme-high');
                        modalTitle.innerText = "Cardiac Risk Assessment";
                        modalIconArea.innerHTML = '<i class="fas fa-heart-pulse"></i>';
                        finalAdvice.innerHTML = `Our AI model has identified risk markers. Your <strong>Functional Heart Age is ${data.heart_age}</strong>. We recommend clinical consultation.`;

                        modalActions.innerHTML = `
                            <a href="/doctors" class="btn-modal-primary btn-find-doctor">
                                <i class="fas fa-user-doctor"></i> Find an Expert Doctor
                            </a>
                            <button type="button" id="downloadPassport" class="btn-modal-passport">
                                <i class="fas fa-file-pdf"></i> Get Smart Passport
                            </button>
                            <button type="button" class="btn-modal-secondary" onclick="location.reload()">Reset Assessment</button>
                        `;
                    } else {
                        modalBox.classList.add('theme-low');
                        modalTitle.innerText = "Heart Health Verified";
                        modalIconArea.innerHTML = '<i class="fas fa-shield-heart"></i>';
                        finalAdvice.innerHTML = `Congratulations! Your cardiovascular foundation is strong. Your heart is aging at an <strong>optimal rate</strong>. Stay healthy!`;

                        modalActions.innerHTML = `
                            <button type="button" id="downloadPassport" class="btn-modal-passport">
                                <i class="fas fa-file-pdf"></i> Download Passport
                            </button>
                            <button type="button" class="btn-modal-primary btn-awesome" onclick="document.getElementById('predictionModal').style.display='none'">
                                <i class="fas fa-thumbs-up"></i> Awesome! Everything looks Great
                            </button>
                        `;
                    }

                    // Re-trigger percentage animation
                    if (data.probability > 0) {
                        let currentStart = 0;
                        const duration = 1500;
                        const stepTime = Math.abs(Math.floor(duration / data.probability));
                        const timer = setInterval(() => {
                            currentStart += 1;
                            const modalPercentage = document.getElementById('modalPercentagePremium');
                            if (!modalPercentage) { clearInterval(timer); return; }
                            if (currentStart >= data.probability) {
                                clearInterval(timer);
                                currentStart = data.probability;
                            }
                            modalPercentage.textContent = Math.round(currentStart) + "%";
                        }, stepTime);
                    }

                    // Handle Tab Toggling
                    const modalTabs = document.querySelectorAll('.modal-tab');
                    modalTabs.forEach(tab => {
                        tab.addEventListener('click', () => {
                            modalTabs.forEach(t => t.classList.remove('active'));
                            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                            tab.classList.add('active');
                            const target = tab.getAttribute('data-tab');
                            document.getElementById(`tab-${target}`).classList.add('active');
                        });
                    });

                    // Add Listener for Download Button (dynamic)
                    const downloadBtn = document.getElementById('downloadPassport');
                    if (downloadBtn) {
                        downloadBtn.addEventListener('click', async () => {
                            const originalContent = downloadBtn.innerHTML;
                            downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
                            downloadBtn.disabled = true;

                            try {
                                const currentForm = document.getElementById('predictionForm');
                                const formData = new FormData(currentForm);
                                const response = await fetch('/generate_report', {
                                    method: 'POST',
                                    body: formData
                                });

                                if (response.ok) {
                                    const blob = await response.blob();
                                    const url = window.URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    const patientName = currentForm.querySelector('[name="patient_name"]').value.trim().replace(/\s+/g, '_').toLowerCase() || 'patient';
                                    const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
                                    a.download = `${patientName}_Heart_Passport_${timestamp}.pdf`;
                                    document.body.appendChild(a);
                                    a.click();
                                    window.URL.revokeObjectURL(url);
                                    a.remove();
                                } else {
                                    const errData = await response.json();
                                    alert('Server Error: ' + (errData.error || 'Failed to generate report.'));
                                }
                            } catch (err) {
                                console.error('Download Error:', err);
                                alert('Connection Error: Could not reach the server to generate PDF.');
                            } finally {
                                downloadBtn.innerHTML = originalContent;
                                downloadBtn.disabled = false;
                            }
                        });
                    }

                } else {
                    alert('Error: ' + data.error);
                }

            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while processing your request.');
            } finally {
                submitBtn.innerText = originalBtnText;
                submitBtn.disabled = false;
            }
        });
    }

    // --- AI Chatbot Logic (Global) ---
    const chatToggle = document.getElementById('chatToggle');
    const chatWindow = document.getElementById('chatWindow');
    const chatClose = document.getElementById('chatClose');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    const chatMessages = document.getElementById('chatMessages');

    if (chatToggle && chatWindow && chatClose) {
        // Toggle Window
        chatToggle.addEventListener('click', () => {
            const isHidden = chatWindow.style.display === 'none' || chatWindow.style.display === '';
            chatWindow.style.display = isHidden ? 'flex' : 'none';
            if (isHidden) chatInput.focus();
        });

        chatClose.addEventListener('click', () => {
            chatWindow.style.display = 'none';
        });

        // Send Message
        const sendMessage = async () => {
            const text = chatInput.value.trim();
            if (!text) return;

            // Add User Message
            appendMessage(text, 'user');
            chatInput.value = '';

            // Add Typing Indicator
            const typingId = addTypingIndicator();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();

                // Remove Typing Indicator and Add Bot Message
                removeTypingIndicator(typingId);
                appendMessage(data.response, 'bot');
            } catch (error) {
                console.error('Chat Error:', error);
                removeTypingIndicator(typingId);
                appendMessage("I'm sorry, I'm having trouble connecting to my brain right now. Please try again later!", 'bot');
            }
        };

        chatSend.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }

    function appendMessage(text, side) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${side}`;
        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing-indicator';
        typingDiv.id = id;
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
});
