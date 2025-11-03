document.addEventListener('DOMContentLoaded', () => {
    // Session management
    let sessionId = null;
    let appName = null;
    let sessionInitializationPromise = null; // Track ongoing initialization
    
    // DOM elements
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const receiptUpload = document.getElementById('receipt-upload');
    const receiptPreview = document.getElementById('receipt-preview');
    const receiptImage = document.getElementById('receipt-image');
    const removeReceiptBtn = document.getElementById('remove-receipt');
    const refreshSummaryBtn = document.getElementById('refresh-summary-btn');
    const expenseSummaryContent = document.getElementById('expense-summary-content');
    const quickActionBtns = document.querySelectorAll('.quick-action-btn-modern');
    
    // Tab management
    const expenseTabs = document.querySelectorAll('.expense-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    let currentReceiptFile = null;
    
    // Initialize
    setupEventListeners();
    initializeSession().then(() => {
        loadDashboard();
    });
    
    function setupEventListeners() {
        // Tab switching
        expenseTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;
                switchTab(tabName);
            });
        });
        
        // Chat functionality
        sendButton.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        // Receipt upload
        receiptUpload.addEventListener('change', handleReceiptUpload);
        removeReceiptBtn.addEventListener('click', removeReceipt);
        
        // Quick actions
        quickActionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                handleQuickAction(action);
            });
        });
        
        // Refresh summary
        if (refreshSummaryBtn) {
            refreshSummaryBtn.addEventListener('click', refreshSummary);
        }
        
        // Date filter handlers
        const applyDateFilterBtn = document.getElementById('apply-date-filter');
        const clearDateFilterBtn = document.getElementById('clear-date-filter');
        
        if (applyDateFilterBtn) {
            applyDateFilterBtn.addEventListener('click', () => {
                const startDate = document.getElementById('start-date').value;
                const endDate = document.getElementById('end-date').value;
                if (startDate && endDate) {
                    loadDashboard(startDate, endDate);
                } else {
                    alert('Please select both start and end dates');
                }
            });
        }
        
        if (clearDateFilterBtn) {
            clearDateFilterBtn.addEventListener('click', () => {
                document.getElementById('start-date').value = '';
                document.getElementById('end-date').value = '';
                loadDashboard();
            });
        }
        
        // Drag and drop for receipt upload
        const uploadLabel = document.querySelector('.upload-label-modern');
        if (uploadLabel) {
            uploadLabel.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadLabel.style.opacity = '0.7';
            });
            
            uploadLabel.addEventListener('dragleave', () => {
                uploadLabel.style.opacity = '1';
            });
            
            uploadLabel.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadLabel.style.opacity = '1';
                const files = e.dataTransfer.files;
                if (files.length > 0 && files[0].type.startsWith('image/')) {
                    receiptUpload.files = files;
                    handleReceiptUpload({ target: { files: files } });
                }
            });
        }
    }
    
    function switchTab(tabName) {
        // Update tab buttons
        expenseTabs.forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
        
        // Update tab content
        tabContents.forEach(content => {
            if (content.id === `${tabName}-tab-content`) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
        
        // Refresh dashboard when switching to dashboard tab
        if (tabName === 'dashboard') {
            loadDashboard();
        }
    }
    
    async function initializeSession() {
        // If initialization is already in progress, return the existing promise
        if (sessionInitializationPromise) {
            return sessionInitializationPromise;
        }
        
        // Create a new initialization promise
        sessionInitializationPromise = (async () => {
            try {
                console.log('🔄 Initializing expense tracker session...');
                const response = await fetch('/api/expense/sessions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({})
                });
                
                // Handle both 200 (session exists) and 201 (created) as success
                if (!response.ok && response.status !== 200 && response.status !== 201) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}`);
                }
                
                const data = await response.json();
                sessionId = data.id;
                appName = data.app_name;
                
                console.log('✅ Expense tracker session initialized:', sessionId);
                
                // Add welcome message only if we don't already have messages
                if (chatMessages.children.length === 0) {
                    addMessage("👋 Hello! I'm your Expense Tracker Assistant. I can help you:\n\n• Add expenses manually\n• Process receipts from photos\n• View your expense history\n• Track spending by category\n• Get expense summaries\n\nTry uploading a receipt or asking me about your expenses!", 'bot');
                }
                
                return { sessionId, appName };
            } catch (error) {
                console.error('❌ Error initializing session:', error);
                // Only show error in UI if it's not a 409 conflict (session exists)
                if (!error.message.includes('409') && !error.message.includes('Conflict')) {
                    addMessage(`Sorry, there was an error setting up the expense tracker. Please refresh the page. Error: ${error.message}`, 'bot');
                }
                throw error;
            } finally {
                // Clear the promise after completion so it can be retried if needed
                sessionInitializationPromise = null;
            }
        })();
        
        return sessionInitializationPromise;
    }
    
    async function handleReceiptUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        if (!file.type.startsWith('image/')) {
            addMessage('Please upload an image file (JPG, PNG, etc.)', 'bot');
            return;
        }
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            receiptImage.src = e.target.result;
            receiptPreview.style.display = 'block';
            currentReceiptFile = file;
        };
        reader.readAsDataURL(file);
        
        // Process receipt
        await processReceipt(file);
    }
    
    function removeReceipt() {
        receiptPreview.style.display = 'none';
        receiptUpload.value = '';
        currentReceiptFile = null;
    }
    
    async function processReceipt(file) {
        // Ensure session is initialized before processing
        if (!sessionId || !appName) {
            try {
                await initializeSession();
            } catch (error) {
                addMessage('Failed to initialize session. Please refresh the page.', 'bot');
                return;
            }
        }
        
        addMessage('📷 Processing receipt...', 'bot');
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('app_name', appName);
            formData.append('session_id', sessionId);
            
            const response = await fetch('/api/expense/upload-receipt', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || 'Failed to process receipt');
            }
            
            const data = await response.json();
            
            // Remove the processing message
            chatMessages.removeChild(chatMessages.lastChild);
            
            // Add user message showing receipt was uploaded
            addMessage('📷 Receipt uploaded', 'user');
            
            // Display the agent's response
            if (data.events && Array.isArray(data.events)) {
                // Process and display agent response
                let expenseAdded = false;
                for (const event of data.events) {
                    if (event.content && event.content.parts) {
                        const parts = event.content.parts;
                        for (const part of parts) {
                            if (part.text) {
                                addMessage(part.text, 'bot');
                                // Check if expense was added
                                if (part.text.toLowerCase().includes('added') || 
                                    part.text.toLowerCase().includes('successfully')) {
                                    expenseAdded = true;
                                }
                            }
                        }
                    }
                }
                // Refresh dashboard if expense was added
                if (expenseAdded) {
                    setTimeout(() => loadDashboard(), 1500);
                }
            } else {
                addMessage('✅ Receipt processed successfully!', 'bot');
                setTimeout(() => loadDashboard(), 1500);
            }
            
            // Clear receipt preview after successful processing
            setTimeout(() => {
                removeReceipt();
            }, 1000);
            
        } catch (error) {
            console.error('Error processing receipt:', error);
            // Remove the processing message
            const loadingMsg = chatMessages.querySelector('.loading');
            if (loadingMsg) loadingMsg.remove();
            
            addMessage(`Sorry, there was an error processing the receipt: ${error.message}`, 'bot');
        }
    }
    
    async function sendMessage() {
        const messageText = chatInput.value.trim();
        
        // If there's a receipt file, process it first
        if (currentReceiptFile) {
            await processReceipt(currentReceiptFile);
            chatInput.value = '';
            return;
        }
        
        if (messageText === '') return;
        
        // Ensure session is initialized before sending message
        if (!sessionId || !appName) {
            try {
                await initializeSession();
            } catch (error) {
                addMessage('Failed to initialize session. Please refresh the page.', 'bot');
                return;
            }
        }
        
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
    
    async function sendMessageToAgent(message) {
        try {
            const response = await fetch(`/api/expense/run_sse`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    app_name: appName,
                    session_id: sessionId,
                    message: message,
                    streaming: false
                }),
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
                                        
                                        // Check if expense was added and refresh dashboard
                                        if (text.toLowerCase().includes('added') || 
                                            text.toLowerCase().includes('successfully') ||
                                            text.toLowerCase().includes('expense added')) {
                                            setTimeout(() => loadDashboard(), 1500);
                                        }
                                    }
                                    
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
    
    function showLoadingMessage() {
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('message', 'loading');
        loadingElement.id = 'loading-message';
        loadingElement.innerHTML = `
            <div class="loading-text">Processing...</div>
            <div class="spinner"></div>
        `;
        chatMessages.appendChild(loadingElement);
        smoothScrollToBottom();
    }
    
    function hideLoadingMessage() {
        const loadingElement = document.getElementById('loading-message');
        if (loadingElement) {
            loadingElement.remove();
        }
    }
    
    function addMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        
        if (sender === 'bot') {
            const formattedText = formatBotMessage(text);
            messageElement.innerHTML = formattedText;
        } else {
            messageElement.textContent = text;
        }
        
        chatMessages.appendChild(messageElement);
        smoothScrollToBottom();
    }
    
    function formatBotMessage(text) {
        let formatted = text;
        
        // Format bold text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Format lists
        formatted = formatted.replace(/\* (.*?)(?=\n|$)/g, '<li>$1</li>');
        if (formatted.includes('<li>')) {
            formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        }
        
        // Handle line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
    
    function smoothScrollToBottom() {
        requestAnimationFrame(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    }
    
    async function handleQuickAction(action) {
        if (!sessionId || !appName) {
            addMessage('Please wait while the session is being initialized...', 'bot');
            return;
        }
        
        // Switch to chat tab for quick actions
        switchTab('chat');
        
        let message = '';
        switch (action) {
            case 'view-all':
                message = 'Show me all my expenses';
                break;
            case 'view-month':
                message = 'Show me my expenses for this month';
                break;
            case 'view-categories':
                message = 'Show me expenses grouped by category';
                break;
            case 'view-summary':
                message = 'Give me a summary of my expenses';
                break;
            default:
                return;
        }
        
        chatInput.value = message;
        await sendMessage();
    }
    
    async function refreshSummary() {
        try {
            await loadDashboard();
        } catch (error) {
            console.error('Error refreshing summary:', error);
            addMessage('Sorry, there was an error refreshing the summary.', 'bot');
        }
    }
    
    async function loadDashboard(startDate = null, endDate = null) {
        try {
            let url = '/api/expense/dashboard';
            if (startDate && endDate) {
                url = `/api/expense/dashboard/range?start_date=${startDate}&end_date=${endDate}`;
            } else if (startDate || endDate) {
                url = `/api/expense/dashboard?${startDate ? `start_date=${startDate}` : ''}${endDate ? `&end_date=${endDate}` : ''}`;
            }
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success && result.data) {
                updateSummaryDisplay(result.data, startDate, endDate);
            } else {
                throw new Error(result.error || 'Failed to load dashboard data');
            }
            
        } catch (error) {
            console.error('Error loading dashboard:', error);
            expenseSummaryContent.innerHTML = `
                <div class="summary-placeholder">
                    <div class="placeholder-icon">⚠️</div>
                    <p>Error loading dashboard</p>
                    <p class="placeholder-hint">${error.message}</p>
                </div>
            `;
        }
    }
    
    function updateSummaryDisplay(data, startDate, endDate) {
        if (!data || data.expense_count === 0) {
            expenseSummaryContent.innerHTML = `
                <div class="summary-placeholder">
                    <div class="placeholder-icon">📈</div>
                    <p>No expenses yet</p>
                    <p class="placeholder-hint">Start adding expenses to see your dashboard!</p>
                </div>
            `;
            return;
        }
        
        const totalAmount = data.total_amount || 0;
        const expenseCount = data.expense_count || 0;
        const averageExpense = data.average_expense || 0;
        const categories = data.categories || {};
        const dateRange = data.date_range || {};
        
        // Format currency (INR)
        const formatCurrency = (amount) => {
            return new Intl.NumberFormat('en-IN', {
                style: 'currency',
                currency: 'INR',
                maximumFractionDigits: 2
            }).format(amount);
        };
        
        // Format date
        const formatDate = (dateStr) => {
            if (!dateStr) return '';
            try {
                const date = new Date(dateStr);
                return date.toLocaleDateString('en-IN', { 
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric' 
                });
            } catch {
                return dateStr;
            }
        };
        
        // Build category breakdown HTML
        let categoryHtml = '';
        const sortedCategories = Object.entries(categories)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5); // Show top 5 categories
        
        if (sortedCategories.length > 0) {
            categoryHtml = '<div class="category-breakdown">';
            categoryHtml += '<h4>Top Categories</h4>';
            sortedCategories.forEach(([category, amount]) => {
                const percentage = totalAmount > 0 ? ((amount / totalAmount) * 100).toFixed(1) : 0;
                categoryHtml += `
                    <div class="category-item">
                        <div class="category-name">${category}</div>
                        <div class="category-amount">${formatCurrency(amount)}</div>
                        <div class="category-bar">
                            <div class="category-bar-fill" style="width: ${percentage}%"></div>
                        </div>
                        <div class="category-percentage">${percentage}%</div>
                    </div>
                `;
            });
            categoryHtml += '</div>';
        }
        
        // Build date range info
        let dateRangeHtml = '';
        if (dateRange.first_expense || dateRange.last_expense) {
            dateRangeHtml = `
                <div class="date-range-info">
                    ${dateRange.first_expense ? `<div><strong>First expense:</strong> ${formatDate(dateRange.first_expense)}</div>` : ''}
                    ${dateRange.last_expense ? `<div><strong>Last expense:</strong> ${formatDate(dateRange.last_expense)}</div>` : ''}
                </div>
            `;
        }
        
        // Build filter info if date range is applied
        let filterInfoHtml = '';
        if (startDate || endDate) {
            filterInfoHtml = `
                <div class="filter-info">
                    <small>Filtered: ${startDate ? formatDate(startDate) : 'beginning'} - ${endDate ? formatDate(endDate) : 'today'}</small>
                </div>
            `;
        }
        
        // Build the complete dashboard HTML
        let summaryHtml = `
            <div class="dashboard-content">
                ${filterInfoHtml}
                <div class="dashboard-stats">
                    <div class="stat-card total-card">
                        <div class="stat-label">Total Spent</div>
                        <div class="stat-value">${formatCurrency(totalAmount)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Expenses</div>
                        <div class="stat-value">${expenseCount}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Average</div>
                        <div class="stat-value">${formatCurrency(averageExpense)}</div>
                    </div>
                </div>
                ${categoryHtml}
                ${dateRangeHtml}
            </div>
        `;
        
        expenseSummaryContent.innerHTML = summaryHtml;
    }
});

