document.addEventListener('DOMContentLoaded', () => {
    // Session management
    let sessionId = null;
    let sessionInitializationPromise = null; // Track ongoing initialization
    
    // DOM elements
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    
    // Initialize
    setupEventListeners();
    initializeSession();
    
    function setupEventListeners() {
        // Chat functionality
        sendButton.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
    
    async function initializeSession() {
        // If initialization is already in progress, return the existing promise
        if (sessionInitializationPromise) {
            return sessionInitializationPromise;
        }
        
        // Create a new initialization promise
        sessionInitializationPromise = (async () => {
            try {
                const response = await fetch('/api/sessions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent_type: 'budget' })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to create session');
                }
                
                const data = await response.json();
                sessionId = data.id;
                console.log('Session initialized:', sessionId);
                return sessionId;
            } catch (error) {
                console.error('Error initializing session:', error);
                addMessage('system', 'Failed to initialize session. Please refresh the page.');
                throw error;
            } finally {
                // Clear the promise after completion so it can be retried if needed
                sessionInitializationPromise = null;
            }
        })();
        
        return sessionInitializationPromise;
    }
    
    function processStreamEvent(event) {
        // Debug: log the event structure (only for errors or unusual cases)
        // console.log('Processing event:', event);
        
        // Check for content.parts structure (most common)
        if (event.content && event.content.parts) {
            const parts = event.content.parts;
            if (parts && Array.isArray(parts) && parts.length > 0) {
                // Check for text in parts first
                for (const part of parts) {
                    if (part.text) {
                        return part.text;
                    }
                }
                
                // Skip function_call and function_response events - don't show them
                for (const part of parts) {
                    // Skip function calls (agent transfers and tool calls)
                    if (part.function_call) {
                        return null; // Don't show function calls
                    }
                    
                    // Skip function responses (tool responses)
                    if (part.function_response) {
                        return null; // Don't show function responses
                    }
                }
            }
        }
        
        // Check for tool calls (like planner.js) - skip these too
        if (event.actions && event.actions.tool_code) {
            return null; // Don't show tool calls
        }
        
        // Check for tool calls in different format - skip these too
        if (event.tool_calls) {
            return null; // Don't show tool calls
        }
        
        // Try direct text field
        if (event.text) {
            return event.text;
        }
        
        // Try nested message structure
        if (event.message && event.message.content && event.message.content.parts) {
            const parts = event.message.content.parts;
            if (parts && Array.isArray(parts) && parts.length > 0) {
                // Check for text first
                for (const part of parts) {
                    if (part.text) {
                        return part.text;
                    }
                }
                // Skip function calls and responses
                for (const part of parts) {
                    if (part.function_call || part.function_response) {
                        return null;
                    }
                }
            }
        }
        
        // Try candidates array (Gemini format)
        if (event.candidates && Array.isArray(event.candidates) && event.candidates.length > 0) {
            const candidate = event.candidates[0];
            if (candidate.content && candidate.content.parts) {
                const parts = candidate.content.parts;
                if (parts && Array.isArray(parts) && parts.length > 0) {
                    // Check for text first
                    for (const part of parts) {
                        if (part.text) {
                            return part.text;
                        }
                    }
                    // Skip function calls and responses
                    for (const part of parts) {
                        if (part.function_call || part.function_response) {
                            return null;
                        }
                    }
                }
            }
        }
        
        // Try response structure
        if (event.response && event.response.text) {
            return event.response.text;
        }
        
        // Log if we can't parse the event (but don't spam console)
        if (event.content && event.content.parts && event.content.parts.length > 0) {
            // This might be a function_response or other non-text event - that's OK
            return null;
        }
        
        console.warn('Could not extract text from event:', event);
        return null;
    }
    
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Ensure session is initialized before sending message
        if (!sessionId) {
            try {
                await initializeSession();
            } catch (error) {
                addMessage('assistant', 'Failed to initialize session. Please refresh the page.');
                return;
            }
        }
        
        addMessage('user', message);
        chatInput.value = '';
        
        // Show loading message
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('message', 'assistant', 'loading');
        loadingElement.id = 'loading-message';
        loadingElement.innerHTML = '<div class="message-content">Thinking...</div>';
        chatMessages.appendChild(loadingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        try {
            const response = await fetch(`/api/sessions/${sessionId}/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: message,
                    agent_type: 'budget'
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let botMessageElement = null;
            let fullMessageText = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    // Remove loading message
                    const loadingMsg = document.getElementById('loading-message');
                    if (loadingMsg) loadingMsg.remove();
                    
                    // Apply final formatting only at the end (like planner.js)
                    if (botMessageElement && fullMessageText) {
                        const formattedText = formatBotMessage(fullMessageText);
                        botMessageElement.querySelector('.message-content').innerHTML = formattedText;
                    } else if (fullMessageText) {
                        // Create message if we have text but no element
                        addMessage('assistant', fullMessageText);
                    }
                    break;
                }
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';
                
                for (const line of lines) {
                    if (line.startsWith('data:')) {
                        const jsonStr = line.substring(5).trim();
                        if (jsonStr && jsonStr !== '') {
                            try {
                                const event = JSON.parse(jsonStr);
                                
                                if (event.error) {
                                    const loadingMsg = document.getElementById('loading-message');
                                    if (loadingMsg) loadingMsg.remove();
                                    addMessage('assistant', `Error: ${event.error}`);
                                    continue;
                                }
                                
                                const text = processStreamEvent(event);
                                if (text !== null && text !== undefined) { // null/undefined means skip, empty string is valid
                                    // Remove loading message when first actual text comes
                                    if (!botMessageElement) {
                                        const loadingMsg = document.getElementById('loading-message');
                                        if (loadingMsg) loadingMsg.remove();
                                        
                                        botMessageElement = document.createElement('div');
                                        botMessageElement.classList.add('message', 'assistant');
                                        botMessageElement.innerHTML = '<div class="message-content"></div>';
                                        chatMessages.appendChild(botMessageElement);
                                    }
                                    
                                    // Accumulate text (use textContent during streaming for better performance)
                                    fullMessageText += text;
                                    
                                    // Use textContent during streaming, format at end
                                    if (botMessageElement) {
                                        botMessageElement.querySelector('.message-content').textContent = fullMessageText;
                                    }
                                    
                                    // Scroll to bottom
                                    chatMessages.scrollTop = chatMessages.scrollHeight;
                                }
                            } catch (e) {
                                console.error('Failed to parse JSON chunk:', jsonStr, e);
                            }
                        }
                    }
                }
            }
            
            // If no message was received, show a helpful message
            if (!fullMessageText.trim() && !botMessageElement) {
                const loadingMsg = document.getElementById('loading-message');
                if (loadingMsg) loadingMsg.remove();
                addMessage('assistant', 'I received your message but didn\'t get a text response. The agent may still be processing - please wait a moment.');
            } else if (!fullMessageText.trim() && botMessageElement) {
                // We have a message element but no text - might be still processing
                const loadingMsg = document.getElementById('loading-message');
                if (loadingMsg) loadingMsg.remove();
                addMessage('assistant', 'Processing complete, but no text response received. The agent may have completed the task using tools.');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            const loadingMsg = document.getElementById('loading-message');
            if (loadingMsg) loadingMsg.remove();
            addMessage('assistant', `Sorry, I encountered an error: ${error.message}. Please try again.`);
        }
    }
    
    function formatBotMessage(text) {
        // Format markdown-like text for display
        let formatted = escapeHtml(text);
        
        // Split into lines for processing
        const lines = formatted.split('\n');
        const processedLines = [];
        let inList = false;
        let listType = null; // 'ul' or 'ol'
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            // Check for bullet points with bold: "* **Text**"
            const bulletBoldMatch = line.match(/^\*\s+\*\*(.+?)\*\*(.*)$/);
            if (bulletBoldMatch) {
                if (!inList) {
                    processedLines.push('<ul>');
                    inList = true;
                    listType = 'ul';
                }
                processedLines.push(`<li><strong>${bulletBoldMatch[1]}</strong>${bulletBoldMatch[2]}</li>`);
                continue;
            }
            
            // Check for regular bullet points: "* Text"
            const bulletMatch = line.match(/^\*\s+(.+)$/);
            if (bulletMatch) {
                if (!inList) {
                    processedLines.push('<ul>');
                    inList = true;
                    listType = 'ul';
                }
                processedLines.push(`<li>${bulletMatch[1]}</li>`);
                continue;
            }
            
            // Check for numbered lists: "1. Text"
            const numberMatch = line.match(/^\d+\.\s+(.+)$/);
            if (numberMatch) {
                if (!inList || listType !== 'ol') {
                    if (inList) {
                        processedLines.push(`</${listType}>`);
                    }
                    processedLines.push('<ol>');
                    inList = true;
                    listType = 'ol';
                }
                processedLines.push(`<li>${numberMatch[1]}</li>`);
                continue;
            }
            
            // Not a list item - close any open list
            if (inList) {
                processedLines.push(`</${listType}>`);
                inList = false;
                listType = null;
            }
            
            // Add the line as-is (will be converted to <br> later)
            processedLines.push(line);
        }
        
        // Close any remaining open list
        if (inList) {
            processedLines.push(`</${listType}>`);
        }
        
        // Join lines and convert remaining **bold** to <strong>
        formatted = processedLines.join('\n');
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert remaining line breaks to <br>
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
    
    function addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        // Format bot messages with markdown-like formatting
        if (role === 'assistant') {
            const formattedContent = formatBotMessage(content);
            messageDiv.innerHTML = `<div class="message-content">${formattedContent}</div>`;
        } else {
            messageDiv.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
