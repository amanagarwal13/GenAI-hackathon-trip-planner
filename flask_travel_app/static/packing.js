document.addEventListener('DOMContentLoaded', () => {
    // Wizard state
    let currentStep = 1;
    const totalSteps = 3;
    let packingData = {
        destination: '',
        startDate: '',
        endDate: '',
        activities: [],
        travelers: '',
        luggageType: '',
        packingStyle: '',
        specialItems: ''
    };
    
    // Session management
    let sessionId = null;
    
    // DOM elements
    const wizard = document.getElementById('onboarding-wizard');
    const chatContainer = document.getElementById('chat-container');
    const progressFill = document.getElementById('progress-fill');
    const stepIndicators = document.querySelectorAll('.step-indicator');
    const wizardSteps = document.querySelectorAll('.wizard-step');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const getPackingListBtn = document.getElementById('get-packing-list-btn');
    const editPreferencesBtn = document.getElementById('edit-preferences-btn');
    
    // Chat elements
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');

    // Initialize wizard
    updateWizardUI();
    setupEventListeners();

    function setupEventListeners() {
        // Navigation buttons
        prevBtn.addEventListener('click', () => changeStep(-1));
        nextBtn.addEventListener('click', () => changeStep(1));
        
        // Get packing list buttons (wizard and preferences panel)
        document.getElementById('get-packing-list-btn').addEventListener('click', startPackingPlanner);
        
        // Edit preferences button
        if (editPreferencesBtn) {
            editPreferencesBtn.addEventListener('click', editPreferences);
        }
        
        // Add event listener for preferences panel packing button (will be added dynamically)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('plan-btn') || e.target.id === 'get-packing-list-btn-panel') {
                sendPreferencesToChat();
            }
        });

        // Activity selection
        document.querySelectorAll('.activity-card').forEach(card => {
            card.addEventListener('click', () => toggleActivity(card));
        });

        // Form validation
        document.querySelectorAll('input, select').forEach(input => {
            input.addEventListener('change', validateCurrentStep);
        });

        // Chat functionality
        sendButton.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('start-date').min = today;
        document.getElementById('end-date').min = today;

        // Update end date minimum when start date changes
        document.getElementById('start-date').addEventListener('change', (e) => {
            document.getElementById('end-date').min = e.target.value;
        });
    }

    function changeStep(direction) {
        if (direction === 1 && !validateCurrentStep()) {
            return;
        }

        const newStep = currentStep + direction;
        if (newStep >= 1 && newStep <= totalSteps) {
            currentStep = newStep;
            updateWizardUI();
        }
    }

    function updateWizardUI() {
        // Update progress bar
        const progress = (currentStep / totalSteps) * 100;
        progressFill.style.width = `${progress}%`;

        // Update step indicators
        stepIndicators.forEach((indicator, index) => {
            const stepNumber = index + 1;
            indicator.classList.remove('active', 'completed');
            
            if (stepNumber === currentStep) {
                indicator.classList.add('active');
            } else if (stepNumber < currentStep) {
                indicator.classList.add('completed');
            }
        });

        // Update wizard steps
        wizardSteps.forEach((step, index) => {
            step.classList.remove('active');
            if (index + 1 === currentStep) {
                step.classList.add('active');
            }
        });

        // Update navigation buttons
        prevBtn.style.display = currentStep > 1 ? 'block' : 'none';
        
        if (currentStep === totalSteps) {
            nextBtn.style.display = 'none';
            getPackingListBtn.style.display = 'block';
        } else {
            nextBtn.style.display = 'block';
            getPackingListBtn.style.display = 'none';
        }

        // Update next button state
        nextBtn.disabled = !validateCurrentStep();
    }

    function validateCurrentStep() {
        switch (currentStep) {
            case 1:
                return document.getElementById('destination').value &&
                       document.getElementById('start-date').value &&
                       document.getElementById('end-date').value;
            case 2:
                return packingData.activities.length > 0;
            case 3:
                return document.getElementById('travelers').value;
            default:
                return false;
        }
    }

    function toggleActivity(card) {
        const activity = card.dataset.activity;
        card.classList.toggle('selected');
        
        if (card.classList.contains('selected')) {
            if (!packingData.activities.includes(activity)) {
                packingData.activities.push(activity);
            }
        } else {
            packingData.activities = packingData.activities.filter(a => a !== activity);
        }
        
        updateWizardUI();
    }

    function collectPackingData() {
        packingData.destination = document.getElementById('destination').value;
        packingData.startDate = document.getElementById('start-date').value;
        packingData.endDate = document.getElementById('end-date').value;
        packingData.travelers = document.getElementById('travelers').value;
        packingData.luggageType = document.getElementById('luggage-type').value;
        packingData.packingStyle = document.getElementById('packing-style').value;
        packingData.specialItems = document.getElementById('special-items').value;
    }

    async function startPackingPlanner() {
        collectPackingData();
        
        // Show loading state
        getPackingListBtn.disabled = true;
        getPackingListBtn.textContent = '🔄 Setting up...';

        try {
            // Create session
            await createSession();
            
            // Hide wizard and show chat interface
            wizard.style.display = 'none';
            chatContainer.style.display = 'block';
            
            // Display preferences in the right panel
            displayPreferences();
            
            // Add welcome message
            addMessage("👋 Hello! I'm your Smart Packing Assistant. I can see all your trip details on the right. I'll help you create the perfect weather-adaptive, culturally-appropriate packing list. Feel free to ask me anything about packing or click 'Get Smart Packing List' when you're ready!", 'bot');
            
        } catch (error) {
            console.error('Error setting up chat:', error);
            
            // Show more specific error message
            let errorMessage = 'Sorry, there was an error setting up the chat. Please try again.';
            if (error.message) {
                errorMessage = `Error: ${error.message}`;
            }
            
            alert(errorMessage);
            getPackingListBtn.disabled = false;
            getPackingListBtn.textContent = '🧳 Get My Smart Packing List!';
        }
    }

    function calculateDuration(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const diffTime = Math.abs(end - start);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    }

    async function createSession() {
        try {
            console.log('🔄 Creating session for packing agent...');
            const response = await fetch('/api/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ agent_type: 'packing' }),
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.error || `HTTP ${response.status}: ${response.statusText}`;
                throw new Error(`Failed to create session: ${errorMessage}`);
            }
            
            const data = await response.json();
            sessionId = data.id;
            console.log('✅ Packing agent session created successfully:', sessionId);
        } catch (error) {
            console.error('❌ Error creating session:', error);
            throw error;
        }
    }

    async function sendMessageToAgent(message) {
        try {
            const response = await fetch(`/api/sessions/${sessionId}/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: message, agent_type: 'packing' }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let botMessageElement = null;
            let fullMessageText = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    // Apply formatting to the complete message
                    if (botMessageElement && fullMessageText) {
                        const formattedText = formatBotMessage(fullMessageText);
                        botMessageElement.innerHTML = formattedText;
                    }
                    break;
                }
                
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data:')) {
                        const jsonStr = line.substring(5).trim();
                        if (jsonStr && jsonStr !== '') {
                            try {
                                const event = JSON.parse(jsonStr);
                                
                                if (event.error) {
                                    addMessage(`Error: ${event.error}`, 'bot');
                                    continue;
                                }
                                
                                let text = processStreamEvent(event);
                                if (text) {
                                    // Hide loading indicator when first response comes
                                    if (!botMessageElement) {
                                        hideLoadingMessage();
                                        botMessageElement = document.createElement('div');
                                        botMessageElement.classList.add('message', 'bot');
                                        chatMessages.appendChild(botMessageElement);
                                    }
                                    
                                    if (text.startsWith('\n[🔧')) {
                                        botMessageElement.innerHTML += `<div class="tool-call">${text}</div>`;
                                    } else {
                                        // Accumulate text for final formatting
                                        fullMessageText += text;
                                        botMessageElement.textContent = fullMessageText;
                                    }
                                    
                                    // Enhanced smooth scrolling during streaming
                                    smoothScrollToBottom();
                                }
                            } catch (e) {
                                console.error("Failed to parse JSON chunk:", jsonStr, e);
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    async function sendMessage() {
        const messageText = chatInput.value.trim();
        if (messageText === '' || !sessionId) return;

        addMessage(messageText, 'user');
        chatInput.value = '';
        
        // Show loading and disable input
        showLoadingMessage();
        chatInput.disabled = true;
        sendButton.disabled = true;
        sendButton.textContent = 'Sending...';

        try {
            await sendMessageToAgent(messageText);
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        } finally {
            hideLoadingMessage();
            chatInput.disabled = false;
            sendButton.disabled = false;
            sendButton.textContent = 'Send';
            chatInput.focus();
        }
    }

    function showLoadingMessage() {
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('message', 'loading');
        loadingElement.id = 'loading-message';
        loadingElement.innerHTML = `
            <div class="loading-text">Your packing assistant is thinking...</div>
            <div class="spinner"></div>
        `;
        chatMessages.appendChild(loadingElement);
        
        // Enhanced smooth scrolling
        smoothScrollToBottom();
    }

    function hideLoadingMessage() {
        const loadingElement = document.getElementById('loading-message');
        if (loadingElement) {
            loadingElement.remove();
        }
    }

    function processStreamEvent(event) {
        if (event.content && event.content.parts) {
            const parts = event.content.parts;
            if (parts && Array.isArray(parts) && parts.length > 0) {
                const text = parts[0].text;
                if (text) {
                    return text;
                }
            }
        }
        
        if (event.actions && event.actions.tool_code) {
            const toolName = event.actions.tool_code.name || 'Unknown';
            const toolInput = event.actions.tool_code.input || {};
            return `\n[🔧 Calling tool: ${toolName}(${JSON.stringify(toolInput)})]`;
        }
        
        return null;
    }

    function addMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        
        // Enhanced formatting for both bot and user messages
        if (sender === 'bot') {
            const formattedText = formatBotMessage(text);
            messageElement.innerHTML = formattedText;
        } else {
            // Format user messages too (especially for structured preferences)
            const formattedText = formatUserMessage(text);
            messageElement.innerHTML = formattedText;
        }
        
        chatMessages.appendChild(messageElement);
        
        // Enhanced smooth scrolling
        smoothScrollToBottom();
    }
    
    function smoothScrollToBottom() {
        // Use requestAnimationFrame for smooth scrolling
        requestAnimationFrame(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    }

    function formatUserMessage(text) {
        // Handle structured preferences message
        let formatted = text;
        
        // Format bold text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Format numbered lists
        formatted = formatted.replace(/^(\d+)\.\s(.+)$/gm, '<li>$2</li>');
        if (formatted.includes('<li>')) {
            formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>');
        }
        
        // Format bullet points
        formatted = formatted.replace(/^-\s(.+)$/gm, '<li>$1</li>');
        if (formatted.includes('<li>') && !formatted.includes('<ol>')) {
            formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        }
        
        // Handle line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }

    function formatBotMessage(text) {
        // Handle general formatting
        let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Handle lists
        formatted = formatted.replace(/\* (.*?)(?=\n|$)/g, '<li>$1</li>');
        if (formatted.includes('<li>')) {
            formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        }
        
        return formatted;
    }

    function displayPreferences() {
        const preferencesContent = document.getElementById('preferences-content');
        const duration = calculateDuration(packingData.startDate, packingData.endDate);
        
        let html = '';
        
        // Basic trip info
        html += `
            <div class="preference-item">
                <div class="preference-label">🌎 Destination</div>
                <div class="preference-value">${packingData.destination}</div>
            </div>
        `;
        
        html += `
            <div class="preference-item">
                <div class="preference-label">📅 Duration</div>
                <div class="preference-value">${duration} days (${packingData.startDate} to ${packingData.endDate})</div>
            </div>
        `;
        
        html += `
            <div class="preference-item">
                <div class="preference-label">👥 Travelers</div>
                <div class="preference-value">${packingData.travelers}</div>
            </div>
        `;
        
        // Activities
        if (packingData.activities.length > 0) {
            html += `
                <div class="preference-item">
                    <div class="preference-label">🚶‍♀️ Planned Activities</div>
                    <div class="preference-themes">
                        ${packingData.activities.map(activity => `<span class="theme-tag">${activity}</span>`).join('')}
                    </div>
                </div>
            `;
        }
        
        // Optional preferences
        if (packingData.luggageType) {
            html += `
                <div class="preference-item">
                    <div class="preference-label">🧳 Luggage Type</div>
                    <div class="preference-value">${packingData.luggageType.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                </div>
            `;
        }
        
        if (packingData.packingStyle) {
            html += `
                <div class="preference-item">
                    <div class="preference-label">📦 Packing Style</div>
                    <div class="preference-value">${packingData.packingStyle.charAt(0).toUpperCase() + packingData.packingStyle.slice(1)}</div>
                </div>
            `;
        }
        
        if (packingData.specialItems) {
            html += `
                <div class="preference-item">
                    <div class="preference-label">📝 Special Items</div>
                    <div class="preference-value">${packingData.specialItems}</div>
                </div>
            `;
        }
        
        preferencesContent.innerHTML = html;
    }

    function sendPreferencesToChat() {
        if (!sessionId) {
            alert('Please wait for the session to be ready.');
            return;
        }
        
        // Get the plan button and show loading state
        const planButton = document.querySelector('.plan-btn') || document.getElementById('get-packing-list-btn-panel');
        if (planButton) {
            planButton.disabled = true;
            planButton.textContent = '🔄 Creating Packing List...';
        }
        
        // Create natural language prompt from preferences
        const prompt = createPackingPrompt();
        
        // Display the formatted preferences as a user message so user can see what's being sent
        addMessage(prompt, 'user');
        
        // Show loading message immediately
        showLoadingMessage();
        
        // Disable chat input while processing
        chatInput.disabled = true;
        sendButton.disabled = true;
        sendButton.textContent = 'Processing...';
        
        // Send the formatted prompt to the agent
        sendMessageToAgent(prompt).finally(() => {
            // Reset button state
            if (planButton) {
                planButton.disabled = false;
                planButton.textContent = '🧳 Get Smart Packing List';
            }
            
            // Re-enable chat input
            chatInput.disabled = false;
            sendButton.disabled = false;
            sendButton.textContent = 'Send';
            chatInput.focus();
        });
    }
    
    function createPackingPrompt() {
        const duration = calculateDuration(packingData.startDate, packingData.endDate);
        
        let prompt = `I need help creating a smart, weather-adaptive packing list for my upcoming trip. Here are my trip details:

🌎 **Destination:** ${packingData.destination}
📅 **Travel Dates:** ${packingData.startDate} to ${packingData.endDate} (${duration} days)
👥 **Number of Travelers:** ${packingData.travelers}`;

        if (packingData.activities.length > 0) {
            prompt += `\n🚶‍♀️ **Planned Activities:** ${packingData.activities.join(', ')}`;
        }
        
        if (packingData.luggageType) {
            prompt += `\n🧳 **Luggage Preference:** ${packingData.luggageType.replace('-', ' ')}`;
        }
        
        if (packingData.packingStyle) {
            prompt += `\n📦 **Packing Style:** ${packingData.packingStyle}`;
        }
        
        if (packingData.specialItems) {
            prompt += `\n📝 **Special Items/Requirements:** ${packingData.specialItems}`;
        }
        
        prompt += `\n\n🧳 **Please provide:**
1. A comprehensive, weather-adaptive packing list organized by categories
2. Weather forecast analysis and how it affects what to pack
3. Cultural considerations and appropriate attire for the destination
4. Activity-specific gear and clothing recommendations
5. Packing optimization tips for my luggage type and style
6. Daily outfit suggestions if helpful
7. Any destination-specific items I should consider

Please make sure the recommendations are tailored to the weather conditions, cultural norms, and my planned activities. Thank you!`;

        return prompt;
    }

    function editPreferences() {
        // Show wizard again
        chatContainer.style.display = 'none';
        wizard.style.display = 'block';
        
        // Reset to first step
        currentStep = 1;
        updateWizardUI();
        
        // Reset get packing list button
        getPackingListBtn.disabled = false;
        getPackingListBtn.textContent = '🧳 Get My Smart Packing List!';
    }

    // Add form validation on input
    document.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('input', updateWizardUI);
        input.addEventListener('change', updateWizardUI);
    });
});
