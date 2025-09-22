/**
 * Main script for the Telegram Feed Kiosk Display - UNIFIED TIME FINAL VERSION
 */
document.addEventListener('DOMContentLoaded', function() {
    // --- Riferimenti al DOM ---
    var dom = {
        title: document.getElementById('feed-title'),
        content: document.getElementById('message-content'),
        author: document.getElementById('message-author'),
        timestamp: document.getElementById('message-timestamp'),
        progressBarContainer: document.getElementById('progress-bar-container'),
        clock: document.getElementById('live-clock'),
        classroomName: document.getElementById('classroom-name'),
        currentDate: document.getElementById('current-date'),
        body: document.body
    };

    // --- Stato e Configurazione Centralizzati ---
    var state = {
        messages: [],
        currentIndex: 0,
        currentLanguage: 'it',
        params: new URLSearchParams(window.location.search),
        timeDifference: 0 // Differenza tra ora server e ora locale
    };

    var config = {
        messageRotationInterval: 10,
        feedUpdateInterval: 60,
        languageToggleInterval: 15,
        timeServiceUrl: 'http://172.16.32.13/api/time/',
        dataRefreshInterval: 5 * 60
    };

    var translations = {
        it: {
            loading: "Caricamento messaggi...",
            missingChat: "Parametro 'chat' mancante nell'URL.",
            loadingError: "Impossibile caricare i messaggi.",
            noMessages: "Nessun messaggio da visualizzare."
        },
        en: {
            loading: "Loading messages...",
            missingChat: "Missing 'chat' parameter in URL.",
            loadingError: "Could not load messages.",
            noMessages: "No messages to display."
        }
    };

    var formatMarkdown = function(text) { return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>'); };

    // Funzione per sincronizzare l'orario con il server
    function syncTimeWithServer() {
        fetch(config.timeServiceUrl)
            .then(function(response) {
                if (!response.ok) throw new Error('Time API not responding');
                return response.json();
            })
            .then(function(data) {
                var serverNow = new Date(data.time);
                var clientNow = new Date();
                state.timeDifference = serverNow - clientNow;
                dom.clock.style.color = '';
                console.log('Time synchronized. Server/client difference:', state.timeDifference, 'ms');
            })
            .catch(function(error) {
                console.error('Could not sync time with server:', error);
                state.timeDifference = 0;
                dom.clock.style.color = 'red';
            });
    }

    // MODIFICATO: Ora aggiorna sia orologio che data usando l'ora locale di Roma
    function updateTimeDisplay() {
        var serverTime = new Date(new Date().getTime() + state.timeDifference);
        
        // --- Orologio (ora locale di Roma) ---
        var clockOptions = {
            timeZone: 'Europe/Rome',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        };
        dom.clock.textContent = serverTime.toLocaleTimeString('it-IT', clockOptions);

        // --- Data (data locale di Roma) ---
        var dateOptions = {
            timeZone: 'Europe/Rome',
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        var locale = (state.currentLanguage === 'it') ? 'it-IT' : 'en-GB';
        var formattedDate = serverTime.toLocaleDateString(locale, dateOptions);
        dom.currentDate.textContent = formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1);
    }

    function updateStaticUI() {
        dom.classroomName.textContent = state.params.get("classroom") || "Kiosk Display";
    }
    
    function toggleLanguage() {
        state.currentLanguage = (state.currentLanguage === 'en') ? 'it' : 'en';
        dom.body.className = 'lang-' + state.currentLanguage;
        updateStaticUI();
    }
    
    function createProgressBars(total) {
        dom.progressBarContainer.innerHTML = "";
        for (var i = 0; i < total; i++) {
            var barWrapper = document.createElement("div");
            barWrapper.className = 'progress-bar';
            var fill = document.createElement("div");
            fill.className = 'progress-fill';
            barWrapper.appendChild(fill);
            dom.progressBarContainer.appendChild(barWrapper);
        }
    }

    function updateProgressBars() {
        var bars = dom.progressBarContainer.children;
        for (var i = 0; i < bars.length; i++) {
            bars[i].classList.remove('active', 'seen');
            if (i < state.currentIndex) {
                bars[i].classList.add('seen');
            } else if (i === state.currentIndex) {
                bars[i].classList.add('active');
            }
        }
    }

    function displayMessage() {
        if (state.messages.length === 0) return;
        
        state.currentIndex = state.currentIndex % state.messages.length;
        var msg = state.messages[state.currentIndex];
        
        dom.content.innerHTML = '<span>' + formatMarkdown(msg.content) + '</span>';
        dom.author.textContent = msg.author;
        dom.timestamp.textContent = msg.timestamp;

        dom.content.classList.remove('scroll');
        setTimeout(function() {
            var contentHeight = dom.content.clientHeight;
            var span = dom.content.querySelector('span');
            var spanHeight = span ? span.clientHeight : 0;
            if (spanHeight > contentHeight) {
                dom.content.classList.add('scroll');
            }
        }, 100);

        updateProgressBars();
        state.currentIndex++;
    }

    function fetchMessages() {
        try {
            var chatId = state.params.get("chat");
            if (!chatId) {
                dom.title.textContent = "Error";
                dom.content.textContent = translations[state.currentLanguage].missingChat;
                return;
            }

            fetch('feed.json?chat=' + encodeURIComponent(chatId))
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('HTTP error! Status: ' + response.status);
                    }
                    return response.json();
                })
                .then(function(data) {
                    dom.title.textContent = data.title || "Message Feed";
                    if (JSON.stringify(data.messages) !== JSON.stringify(state.messages)) {
                        state.messages = data.messages || [];
                        state.currentIndex = 0;
                        createProgressBars(state.messages.length);
                        if (state.messages.length > 0) {
                            displayMessage();
                        } else {
                            dom.content.textContent = translations[state.currentLanguage].noMessages;
                        }
                    }
                })
                .catch(function(error) {
                    console.error("Error fetching messages:", error);
                    dom.content.textContent = translations[state.currentLanguage].loadingError;
                });
        } catch (e) {
            console.error("Errore critico in fetchMessages:", e);
        }
    }
    
    window.onload = function() {
        var loader = document.getElementById('loader');
        if (loader) {
            loader.classList.add('hidden');
        }
    };
    
    function init() {
        dom.body.className = 'lang-' + state.currentLanguage;
        updateStaticUI();
        dom.content.textContent = translations[state.currentLanguage].loading;

        syncTimeWithServer();
        fetchMessages();
        
        var secondsCounter = 0;
        
        setInterval(function() {
            try {
                secondsCounter++;
                updateTimeDisplay();

                if (secondsCounter % config.messageRotationInterval === 0) {
                    displayMessage();
                }
                if (secondsCounter % config.languageToggleInterval === 0) {
                    toggleLanguage();
                }
                if (secondsCounter % config.feedUpdateInterval === 0) {
                    fetchMessages();
                }
                if (secondsCounter % config.dataRefreshInterval === 0) {
                    syncTimeWithServer();
                }
            } catch (e) {
                console.error("Errore nell'intervallo principale:", e);
            }
        }, 1000);
        
        setTimeout(function() { 
            window.location.reload(true); 
        }, 4 * 60 * 60 * 1000);
    }

    init();
});