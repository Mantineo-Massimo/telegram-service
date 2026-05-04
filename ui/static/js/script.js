/**
 * EN:
 * Main script for the Telegram feed display.
 * This script fetches messages from a Telegram channel via the backend,
 * displays them one by one in a carousel-style rotation, and handles
 * progress bars, a server-synced live clock, and other dynamic UI elements.
 *
 * IT:
 * Script principale per il display del feed di Telegram.
 * Questo script recupera i messaggi da un canale Telegram tramite il backend,
 * li mostra uno a uno in una rotazione stile carosello e gestisce
 * le barre di progresso, un orologio in tempo reale sincronizzato col server 
 * e altri elementi dinamici della UI.
 */
document.addEventListener('DOMContentLoaded', function () {

    // EN: Centralized object for DOM element references for performance and clarity.
    // IT: Oggetto centralizzato per i riferimenti agli elementi del DOM per performance e chiarezza.
    var dom = {
        title: document.getElementById('feed-title'),
        content: document.getElementById('message-content'),
        author: document.getElementById('message-author'),
        timestamp: document.getElementById('message-timestamp'),
        progressContainer: document.getElementById('progress-bar-container'),
        clock: document.getElementById('live-clock'),
        date: document.getElementById('current-date'),
        loader: document.getElementById('loader'),
        classroomName: document.getElementById('classroom-name'),
        body: document.body
    };

    // EN: Centralized state management object to hold dynamic data.
    // IT: Oggetto centralizzato per la gestione dello stato per contenere dati dinamici.
    var state = {
        messages: [],
        currentIndex: 0,
        chatId: null,
        carouselTimeout: null,
        currentLanguage: 'it', // EN: Start with Italian / IT: Inizia con l'italiano
        timeDifference: 0 // EN: Difference in ms between server and client time. / IT: Differenza in ms tra ora del server e del client.
    };

    // EN: Static configuration values for timings and intervals.
    // IT: Valori di configurazione statici per tempistiche e intervalli.
    var config = {
        messageDuration: 10000, // EN: 10 seconds per message / IT: 10 secondi per messaggio
        dataRefreshInterval: 5 * 60 * 1000, // EN: 5 minutes / IT: 5 minuti
        languageToggleInterval: 15, // EN: 15 seconds / IT: 15 secondi
        timeServiceUrl: '/api/time/', // EN: URL for the server time API / IT: URL per l'API dell'ora del server
    };

    // EN: Object containing all translation strings with correct capitalization.
    // IT: Oggetto contenente tutte le stringhe di traduzione con le maiuscole corrette.
    var translations = {
        it: {
            days: ["Domenica", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"],
            months: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
        },
        en: {
            days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        }
    };

    /**
     * EN: Syncs the local time with the server's time to correct for client-side clock drift.
     * IT: Sincronizza l'ora locale con quella del server per correggere imprecisioni dell'orologio del client.
     */
    function syncTimeWithServer() {
        fetch(config.timeServiceUrl)
            .then(response => {
                if (!response.ok) throw new Error('Time API not responding');
                return response.json();
            })
            .then(data => {
                const serverNow = new Date(data.time);
                const clientNow = new Date();
                state.timeDifference = serverNow - clientNow;
                console.log('Time synchronized. Server/client difference:', state.timeDifference, 'ms');
                // EN: Reset clock color on successful sync / IT: Reimposta il colore dell'orologio in caso di successo
                dom.clock.style.color = '';
            })
            .catch(error => {
                console.error('Could not sync time with server:', error);
                state.timeDifference = 0; // EN: Fallback to client time on error. / IT: Ripiega sull'ora del client in caso di errore.
                dom.clock.style.color = 'red'; // EN: Indicate time sync error / IT: Indica errore di sincr. orologio
            });
    }

    /**
     * EN: Fetches the message feed from the backend API for the configured chat ID.
     * IT: Recupera il feed dei messaggi dall'API del backend per l'ID della chat configurato.
     */
    function fetchFeed() {
        if (!state.chatId) {
            console.error("Chat ID is not set. Cannot fetch feed.");
            dom.content.textContent = "Error: 'chat' parameter is missing in the URL.";
            return;
        }

        fetch('/telegram/feed.json?chat=' + state.chatId)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('HTTP error! status: ' + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                state.messages = data.messages || [];
                if (dom.title) dom.title.textContent = data.title || "Telegram Feed";

                if (state.messages.length === 0) {
                    dom.content.textContent = "No messages found in this feed.";
                } else {
                    setupCarousel();
                }
            })
            .catch(function (error) {
                console.error("Failed to fetch feed:", error);
                dom.content.textContent = "Could not load messages. Please check the connection and Chat ID.";
            })
            .finally(function () {
                if (dom.loader) dom.loader.classList.add('hidden');
            });
    }

    /**
     * EN: Sets up the carousel by creating progress bars and starting the message rotation.
     * IT: Imposta il carosello creando le barre di progresso e avviando la rotazione dei messaggi.
     */
    function setupCarousel() {
        dom.progressContainer.innerHTML = '';
        state.messages.forEach(function() {
            var bar = document.createElement('div');
            bar.className = 'progress-bar';
            bar.innerHTML = '<div class="progress-fill"></div>';
            dom.progressContainer.appendChild(bar);
        });

        clearTimeout(state.carouselTimeout);
        state.currentIndex = 0;
        displayMessage();
    }

    /**
     * EN: Displays the message at the current index and updates the UI.
     * IT: Mostra il messaggio all'indice corrente e aggiorna la UI.
     */
    function displayMessage() {
        var msg = state.messages[state.currentIndex];
        if (!msg) return;

        dom.content.innerHTML = '<span>' + msg.content.replace(/\n/g, '<br>') + '</span>';
        dom.author.textContent = msg.author;
        dom.timestamp.textContent = msg.timestamp;

        var contentSpan = dom.content.querySelector('span');
        var messageDuration = config.messageDuration;

        if (contentSpan && contentSpan.scrollHeight > dom.content.clientHeight) {
            dom.content.classList.add('scroll');
            
            // IT: Calcola la durata in base all'altezza del testo per leggere tutto.
            var scrollDistance = contentSpan.scrollHeight - dom.content.clientHeight;
            var scrollTimeSec = Math.max(8, scrollDistance / 25);
            
            // IT: Imposta l'animazione personalizzata con andata e ritorno (alternate)
            contentSpan.style.animation = 'scroll-vertical ' + scrollTimeSec + 's linear 1s infinite alternate';
            
            // IT: Tempo sufficiente per scendere e risalire
            messageDuration = (scrollTimeSec * 2 * 1000) + 2000;
        } else {
            dom.content.classList.remove('scroll');
            if (contentSpan) {
                contentSpan.style.animation = 'none';
            }
        }

        updateProgressBars(messageDuration);
        
        clearTimeout(state.carouselTimeout);
        state.carouselTimeout = setTimeout(nextMessage, messageDuration);
    }

    /**
     * EN: Moves to the next message in the carousel, looping back to the start.
     * IT: Passa al messaggio successivo nel carosello, tornando all'inizio alla fine.
     */
    function nextMessage() {
        state.currentIndex = (state.currentIndex + 1) % state.messages.length;
        displayMessage();
    }

    /**
     * EN: Updates the progress bars to reflect the currently displayed message.
     * IT: Aggiorna le barre di progresso per riflettere il messaggio attualmente visualizzato.
     */
    function updateProgressBars(duration) {
        var bars = dom.progressContainer.children;
        for (var i = 0; i < bars.length; i++) {
            bars[i].classList.remove('active', 'seen');
            var fill = bars[i].querySelector('.progress-fill');
            if (fill) fill.style.animationDuration = ''; // reset
            
            if (i < state.currentIndex) {
                bars[i].classList.add('seen');
            } else if (i === state.currentIndex) {
                bars[i].classList.add('active');
                if (fill && duration) {
                    fill.style.animationDuration = duration + 'ms';
                }
            }
        }
    }

    /**
     * EN: Updates the live clock and date display using server-synced time.
     * IT: Aggiorna l'orologio e la data in tempo reale usando l'ora sincronizzata con il server.
     */
    function updateClockAndDate() {
        // EN: Use server-synced time / IT: Usa l'ora sincronizzata con il server
        const now = new Date(new Date().getTime() + state.timeDifference);

        const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false, timeZone: 'Europe/Rome' };
        dom.clock.textContent = now.toLocaleTimeString('it-IT', timeOptions);

        // EN: Manually construct the date string using translations for correct capitalization.
        // IT: Costruisce manualmente la stringa della data usando le traduzioni per la maiuscola corretta.
        var lang = translations[state.currentLanguage];
        var dayName = lang.days[now.getDay()];
        var monthName = lang.months[now.getMonth()];
        dom.date.textContent = dayName + ', ' + now.getDate() + ' ' + monthName + ' ' + now.getFullYear();
    }

    /**
     * EN: Toggles the display language between Italian and English.
     * IT: Alterna la lingua di visualizzazione tra italiano e inglese.
     */
    function toggleLanguage() {
        state.currentLanguage = (state.currentLanguage === 'it') ? 'en' : 'it'; // Fixed logic too
        dom.body.className = 'lang-' + state.currentLanguage;
        // EN: Update date immediately after language change.
        // IT: Aggiorna la data immediatamente dopo il cambio di lingua.
        updateClockAndDate();
    }

    /**
     * EN: Helper to get URL parameters without URLSearchParams (for broad compatibility).
     */
    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        var results = regex.exec(window.location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    /**
     * EN: Initialization function that runs once the page is loaded.
     * IT: Funzione di inizializzazione che viene eseguita una volta caricata la pagina.
     */
    function init() {
        dom.body.className = 'lang-' + state.currentLanguage;

        state.chatId = getUrlParameter('chat');

        var classroom = getUrlParameter('classroom');
        if (classroom && dom.classroomName) {
            dom.classroomName.textContent = classroom;
        }

        // EN: Sync time first, then update clock and fetch data
        // IT: Sincronizza l'ora, poi aggiorna l'orologio e recupera i dati
        syncTimeWithServer();
        updateClockAndDate();
        fetchFeed();

        var secondsCounter = 0;
        setInterval(function() {
            secondsCounter++;
            updateClockAndDate(); // EN: This now uses synced time / IT: Ora usa l'ora sincronizzata

            // EN: Toggle language at the specified interval.
            // IT: Cambia la lingua all'intervallo specificato.
            if (secondsCounter % config.languageToggleInterval === 0) {
                toggleLanguage();
            }

            // EN: Refresh data and re-sync time periodically.
            // IT: Aggiorna i dati e risincronizza l'ora periodicamente.
            if (secondsCounter % (config.dataRefreshInterval / 1000) === 0) {
                syncTimeWithServer();
                fetchFeed();
            }
        }, 1000);

        // EN: Full page reload every few hours to prevent long-term issues.
        // IT: Ricarica completa della pagina ogni qualche ora per prevenire problemi a lungo termine.
        setTimeout(function() { window.location.reload(true); }, 4 * 60 * 60 * 1000);
    }

    init();
});