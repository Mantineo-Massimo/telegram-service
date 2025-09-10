/**
 * Main script for the Telegram Feed Kiosk Display - Robust & Legacy Browser Compatible Version.
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
        params: new URLSearchParams(window.location.search)
    };

    var config = {
        messageRotationInterval: 10,
        feedUpdateInterval: 60,
        languageToggleInterval: 15,
    };

    var translations = {
        it: {
            days: ["Domenica", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"],
            months: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
            loading: "Caricamento messaggi...",
            missingChat: "Parametro 'chat' mancante nell'URL.",
            loadingError: "Impossibile caricare i messaggi.",
            noMessages: "Nessun messaggio da visualizzare."
        },
        en: {
            days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            loading: "Loading messages...",
            missingChat: "Missing 'chat' parameter in URL.",
            loadingError: "Could not load messages.",
            noMessages: "No messages to display."
        }
    };

    // Correzione per compatibilità
    var padZero = function(n) { return n < 10 ? '0' + n : String(n); };
    var formatMarkdown = function(text) { return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>'); };

    function updateClock() {
        var now = new Date();
        dom.clock.textContent = padZero(now.getHours()) + ':' + padZero(now.getMinutes()) + ':' + padZero(now.getSeconds());
    }

    function updateStaticUI() {
        var lang = translations[state.currentLanguage];
        var now = new Date();
        var dayName = lang.days[now.getDay()];
        var monthName = lang.months[now.getMonth()];
        dom.currentDate.textContent = dayName + ' ' + now.getDate() + ' ' + monthName + ' ' + now.getFullYear();
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

    // Aggiunto try...catch per robustezza
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

        // --- Logica per la Schermata di Caricamento ---
    // Aspetta che l'intera pagina (immagini, stili, etc.) sia completamente caricata
    window.onload = function() {
        var loader = document.getElementById('loader');
        if (loader) {
            // Aggiunge la classe 'hidden' per far scomparire il loader con una transizione
            loader.classList.add('hidden');
        }
    };
    
    function init() {
        dom.body.className = 'lang-' + state.currentLanguage;
        updateStaticUI();
        dom.content.textContent = translations[state.currentLanguage].loading;

        fetchMessages();
        
        var secondsCounter = 0;
        
        // Aggiunto try...catch per robustezza
        setInterval(function() {
            try {
                secondsCounter++;
                updateClock();

                if (secondsCounter % config.messageRotationInterval === 0) {
                    displayMessage();
                }
                if (secondsCounter % config.languageToggleInterval === 0) {
                    toggleLanguage();
                }
                if (secondsCounter % config.feedUpdateInterval === 0) {
                    fetchMessages();
                }
            } catch (e) {
                console.error("Errore nell'intervallo principale:", e);
            }
        }, 1000);

        // Aggiunto ricaricamento pagina per stabilità
        setTimeout(function() { 
            window.location.reload(true); 
        }, 4 * 60 * 60 * 1000);
    }

    init();
});