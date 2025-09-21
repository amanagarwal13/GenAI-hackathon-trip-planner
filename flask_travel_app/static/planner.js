document.addEventListener('DOMContentLoaded', () => {
    // Wizard state
    let currentStep = 1;
    const totalSteps = 4;
    let tripData = {
        origin: '',
        destination: '',
        startDate: '',
        endDate: '',
        budget: '',
        travelers: '',
        accommodation: '',
        themes: [],
        foodPreference: '',
        pace: '',
        flightPreference: '',
        specialRequirements: ''
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
    const planTripBtn = document.getElementById('plan-trip-btn');
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
        
        // Plan trip buttons (wizard and preferences panel)
        document.getElementById('plan-trip-btn').addEventListener('click', planTrip);
        
        // Edit preferences button
        if (editPreferencesBtn) {
            editPreferencesBtn.addEventListener('click', editPreferences);
        }
        
        // Add event listener for preferences panel plan button (will be added dynamically)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('plan-btn')) {
                sendPreferencesToChat();
            }
        });

        // Theme selection
        document.querySelectorAll('.theme-card').forEach(card => {
            card.addEventListener('click', () => toggleTheme(card));
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
            planTripBtn.style.display = 'block';
        } else {
            nextBtn.style.display = 'block';
            planTripBtn.style.display = 'none';
        }

        // Update next button state
        nextBtn.disabled = !validateCurrentStep();
    }

    function validateCurrentStep() {
        switch (currentStep) {
            case 1:
                return document.getElementById('origin').value &&
                       document.getElementById('destination').value &&
                       document.getElementById('start-date').value &&
                       document.getElementById('end-date').value;
            case 2:
                return document.getElementById('budget').value &&
                       document.getElementById('travelers').value &&
                       document.querySelector('input[name="accommodation"]:checked');
            case 3:
                return tripData.themes.length > 0;
            case 4:
                return true; // Optional step
            default:
                return false;
        }
    }

    function toggleTheme(card) {
        const theme = card.dataset.theme;
        card.classList.toggle('selected');
        
        if (card.classList.contains('selected')) {
            if (!tripData.themes.includes(theme)) {
                tripData.themes.push(theme);
            }
        } else {
            tripData.themes = tripData.themes.filter(t => t !== theme);
        }
        
        updateWizardUI();
    }

    function collectTripData() {
        tripData.origin = document.getElementById('origin').value;
        tripData.destination = document.getElementById('destination').value;
        tripData.startDate = document.getElementById('start-date').value;
        tripData.endDate = document.getElementById('end-date').value;
        tripData.budget = document.getElementById('budget').value;
        tripData.travelers = document.getElementById('travelers').value;
        tripData.accommodation = document.querySelector('input[name="accommodation"]:checked')?.value || '';
        tripData.foodPreference = document.getElementById('food-preference').value;
        tripData.pace = document.getElementById('pace').value;
        tripData.flightPreference = document.getElementById('flight-preference').value;
        tripData.specialRequirements = document.getElementById('special-requirements').value;
    }

    async function planTrip() {
        collectTripData();
        
        // Show loading state
        planTripBtn.disabled = true;
        planTripBtn.textContent = '🔄 Setting up...';

        try {
            // Create session
            await createSession();
            
            // Hide wizard and show chat interface
            wizard.style.display = 'none';
            chatContainer.style.display = 'block';
            
            // Display preferences in the right panel
            displayPreferences();
            
            // Add welcome message
            addMessage("👋 Hello! I'm Aria, your AI Travel Specialist. I can see all your trip preferences on the right. Feel free to ask me anything about your trip or click 'Plan My Trip' when you're ready!", 'bot');
            
        } catch (error) {
            console.error('Error setting up chat:', error);
            
            // Show more specific error message
            let errorMessage = 'Sorry, there was an error setting up the chat. Please try again.';
            if (error.message) {
                errorMessage = `Error: ${error.message}`;
            }
            
            alert(errorMessage);
            planTripBtn.disabled = false;
            planTripBtn.textContent = '🚀 Plan My Trip!';
        }
    }

    function updateTripSummary() {
        const tripTitle = document.getElementById('trip-title');
        const tripSummary = document.getElementById('trip-summary');
        
        tripTitle.textContent = `${tripData.origin} to ${tripData.destination} Trip`;
        
        const duration = calculateDuration(tripData.startDate, tripData.endDate);
        const themesText = tripData.themes.length > 0 ? tripData.themes.join(', ') : 'General';
        
        tripSummary.innerHTML = `
            <div><strong>📅 Duration:</strong> ${duration} days (${tripData.startDate} to ${tripData.endDate})</div>
            <div><strong>💰 Budget:</strong> ₹${parseInt(tripData.budget).toLocaleString()}</div>
            <div><strong>👥 Travelers:</strong> ${tripData.travelers}</div>
            <div><strong>🎯 Themes:</strong> ${themesText}</div>
        `;
    }

    function calculateDuration(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const diffTime = Math.abs(end - start);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    }

    async function createSession() {
        try {
            console.log('🔄 Creating session...');
            const response = await fetch('/api/sessions', {
                method: 'POST',
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.error || `HTTP ${response.status}: ${response.statusText}`;
                throw new Error(`Failed to create session: ${errorMessage}`);
            }
            
            const data = await response.json();
            sessionId = data.id;
            console.log('✅ Session created successfully:', sessionId);
        } catch (error) {
            console.error('❌ Error creating session:', error);
            throw error;
        }
    }

    async function generateItinerary() {
        if (!sessionId) {
            throw new Error('No session available');
        }

        // Create comprehensive prompt for itinerary generation
        const prompt = createItineraryPrompt();
        
        // Add initial message with Aria branding
        addMessage("🎉 Hello! I'm Aria, your AI Travel Specialist. I'm generating your personalized itinerary based on your preferences. This may take a moment...", 'bot');
        
        // Add loading indicator
        showLoadingMessage();
        
        try {
            await sendMessageToAgent(prompt);
        } catch (error) {
            console.error('Error generating itinerary:', error);
            addMessage("❌ Sorry, there was an error generating your itinerary. Please try asking me specific questions about your trip.", 'bot');
        } finally {
            hideLoadingMessage();
        }
    }

    function createItineraryPrompt() {
        const duration = calculateDuration(tripData.startDate, tripData.endDate);
        
        let prompt = `Please create a detailed ${duration}-day itinerary for a trip from ${tripData.origin} to ${tripData.destination} with the following specifications:

📅 **Trip Details:**
- Dates: ${tripData.startDate} to ${tripData.endDate} (${duration} days)
- Budget: ₹${parseInt(tripData.budget).toLocaleString()}
- Travelers: ${tripData.travelers}
- Accommodation preference: ${tripData.accommodation}

🎯 **Interests & Themes:**
- Primary themes: ${tripData.themes.join(', ')}
- Travel pace: ${tripData.pace || 'moderate'}`;

        if (tripData.foodPreference) {
            prompt += `\n- Food preference: ${tripData.foodPreference}`;
        }

        if (tripData.specialRequirements) {
            prompt += `\n- Special requirements: ${tripData.specialRequirements}`;
        }

        prompt += `\n\n📋 **Please provide:**
1. A day-by-day detailed itinerary with specific activities, timings, and locations
2. Accommodation recommendations within the budget
3. Transportation suggestions
4. Food recommendations (considering dietary preferences)
5. Estimated costs for major activities
6. Tips and local insights

Please format the response clearly with day-wise breakdown and include practical details like addresses, timings, and booking requirements where relevant.`;

        return prompt;
    }

    async function sendMessageToAgent(message) {
        try {
            const response = await fetch(`/api/sessions/${sessionId}/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: message }),
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
            <div class="loading-text">Aria is thinking...</div>
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
        // Handle flight options formatting
        if (text.includes('flight from') && text.includes('₹')) {
            return formatFlightOptions(text);
        }
        
        // Handle bullet points
        let formatted = text.replace(/\* \*\*(.*?)\*\*/g, '<div class="flight-option"><div class="flight-header">$1</div>');
        formatted = formatted.replace(/\* (.*?)₹([\d,]+)/g, '<div class="flight-option"><div class="flight-details">$1</div><div class="flight-price">₹$2</div></div>');
        
        // Handle general formatting
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Handle lists
        formatted = formatted.replace(/\* (.*?)(?=\n|$)/g, '<li>$1</li>');
        if (formatted.includes('<li>')) {
            formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        }
        
        return formatted;
    }

    function formatFlightOptions(text) {
        // Extract flight options and format them nicely
        const flightPattern = /\* \*\*(.*?)\*\*:(.*?)₹([\d,]+)/g;
        let matches = [];
        let match;
        
        while ((match = flightPattern.exec(text)) !== null) {
            matches.push({
                airline: match[1].trim(),
                details: match[2].trim(),
                price: match[3].trim()
            });
        }
        
        if (matches.length > 0) {
            let formatted = text.split('* **')[0]; // Get the intro text
            formatted += '<div class="flight-options">';
            
            matches.forEach(flight => {
                formatted += `
                    <div class="flight-option">
                        <div class="flight-header">${flight.airline}</div>
                        <div class="flight-details">${flight.details}</div>
                        <div class="flight-price">₹${flight.price}</div>
                    </div>
                `;
            });
            
            formatted += '</div>';
            
            // Add any remaining text after the flights
            const remainingText = text.split('₹' + matches[matches.length - 1].price)[1];
            if (remainingText) {
                formatted += remainingText.replace(/\n/g, '<br>');
            }
            
            return formatted;
        }
        
        // Fallback to regular formatting
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
    }

    function displayPreferences() {
        const preferencesContent = document.getElementById('preferences-content');
        const duration = calculateDuration(tripData.startDate, tripData.endDate);
        
        let html = '';
        
        // Basic trip info
        html += `
            <div class="preference-item">
                <div class="preference-label">📍 Route</div>
                <div class="preference-value">${tripData.origin} → ${tripData.destination}</div>
            </div>
        `;
        
        html += `
            <div class="preference-item">
                <div class="preference-label">📅 Duration</div>
                <div class="preference-value">${duration} days (${tripData.startDate} to ${tripData.endDate})</div>
            </div>
        `;
        
        html += `
            <div class="preference-item">
                <div class="preference-label">💰 Budget</div>
                <div class="preference-value">₹${parseInt(tripData.budget).toLocaleString()}</div>
            </div>
        `;
        
        html += `
            <div class="preference-item">
                <div class="preference-label">👥 Travelers</div>
                <div class="preference-value">${tripData.travelers}</div>
            </div>
        `;
        
        html += `
            <div class="preference-item">
                <div class="preference-label">🏨 Accommodation</div>
                <div class="preference-value">${tripData.accommodation.charAt(0).toUpperCase() + tripData.accommodation.slice(1)}</div>
            </div>
        `;
        
        // Themes
        if (tripData.themes.length > 0) {
            html += `
                <div class="preference-item">
                    <div class="preference-label">🎯 Travel Themes</div>
                    <div class="preference-themes">
                        ${tripData.themes.map(theme => `<span class="theme-tag">${theme}</span>`).join('')}
                    </div>
                </div>
            `;
        }
        
        // Optional preferences
        if (tripData.foodPreference) {
            html += `
                <div class="preference-item">
                    <div class="preference-label">🍽️ Food Preference</div>
                    <div class="preference-value">${tripData.foodPreference.charAt(0).toUpperCase() + tripData.foodPreference.slice(1)}</div>
                </div>
            `;
        }
        
        if (tripData.pace) {
            html += `
                <div class="preference-item">
                    <div class="preference-label">⏱️ Travel Pace</div>
                    <div class="preference-value">${tripData.pace.charAt(0).toUpperCase() + tripData.pace.slice(1)}</div>
                </div>
            `;
        }
        
        if (tripData.flightPreference) {
            html += `
                <div class="preference-item">
                    <div class="preference-label">✈️ Flight Preference</div>
                    <div class="preference-value">${tripData.flightPreference.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                </div>
            `;
        }
        
        if (tripData.specialRequirements) {
            html += `
                <div class="preference-item">
                    <div class="preference-label">📝 Special Requirements</div>
                    <div class="preference-value">${tripData.specialRequirements}</div>
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
        const planButton = document.querySelector('.plan-btn');
        if (planButton) {
            planButton.disabled = true;
            planButton.textContent = '🔄 Sending Preferences...';
        }
        
        // Create natural language prompt from preferences
        const prompt = createNaturalLanguagePrompt();
        
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
                planButton.textContent = '🚀 Plan My Trip';
            }
            
            // Re-enable chat input
            chatInput.disabled = false;
            sendButton.disabled = false;
            sendButton.textContent = 'Send';
            chatInput.focus();
        });
    }
    
    function createNaturalLanguagePrompt() {
        const duration = calculateDuration(tripData.startDate, tripData.endDate);
        
        let prompt = `I would like you to plan a detailed ${duration}-day trip for me. Here are all my preferences:

🗺️ **Trip Details:**
- From: ${tripData.origin}
- To: ${tripData.destination}
- Dates: ${tripData.startDate} to ${tripData.endDate} (${duration} days)
- Budget: ₹${parseInt(tripData.budget).toLocaleString()}
- Number of travelers: ${tripData.travelers}
- Accommodation preference: ${tripData.accommodation}`;

        if (tripData.themes.length > 0) {
            prompt += `\n- Travel themes I'm interested in: ${tripData.themes.join(', ')}`;
        }
        
        if (tripData.foodPreference) {
            prompt += `\n- Food preference: ${tripData.foodPreference}`;
        }
        
        if (tripData.pace) {
            prompt += `\n- Preferred travel pace: ${tripData.pace}`;
        }
        
        if (tripData.flightPreference) {
            const flightTime = tripData.flightPreference.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
            prompt += `\n- Flight time preference: ${flightTime}`;
        }
        
        if (tripData.specialRequirements) {
            prompt += `\n- Special requirements: ${tripData.specialRequirements}`;
        }
        
        prompt += `\n\n📋 **Please provide:**
1. A complete day-by-day itinerary with specific activities and timings
2. Flight recommendations (considering my time preferences)
3. Hotel/accommodation suggestions within my budget
4. Restaurant recommendations (considering my food preferences)
5. Transportation options between activities
6. Estimated costs for major expenses
7. Local tips and insider recommendations
8. Any booking requirements or advance reservations needed

Please make sure the itinerary matches my interests and stays within my budget. Thank you!`;

        return prompt;
    }

    function editPreferences() {
        // Show wizard again
        chatContainer.style.display = 'none';
        wizard.style.display = 'block';
        
        // Reset to first step
        currentStep = 1;
        updateWizardUI();
        
        // Reset plan trip button
        planTripBtn.disabled = false;
        planTripBtn.textContent = '🚀 Plan My Trip!';
    }

    // Add form validation on input
    document.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('input', updateWizardUI);
        input.addEventListener('change', updateWizardUI);
    });
});