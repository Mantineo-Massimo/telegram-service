/**
 * EN:
 * Main script for the Telegram feed display.
 * This script fetches messages from a Telegram channel via the backend,
 * displays them one by one in a carousel-style rotation, and handles
 * progress bars, a live clock, and other dynamic UI elements.
 *
 * IT:
 * Script principale per il display del feed di Telegram.
 * Questo script recupera i messaggi da un canale Telegram tramite il backend,
 * li mostra uno a uno in una rotazione stile carosello e gestisce
 * le barre di progresso, un orologio in tempo reale e altri elementi dinamici della UI.
 */
document.addEventListener('DOMContentLoaded', function() {

    // EN: Centralized object for DOM element references for performance and clarity.
    // IT: Oggetto centralizzato per i riferimenti agli elementi del DOM per performance e chiarezza.
    const dom = {
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
    const state = {
        messages: [],
        currentIndex: 0,
        chatId: null,
        carouselInterval: null,
        currentLanguage: 'it' // EN: Start with Italian / IT: Inizia con l'italiano
    };

    // EN: Static configuration values for timings and intervals.
    // IT: Valori di configurazione statici per tempistiche e intervalli.
    const config = {
        messageDuration: 10000, // EN: 10 seconds per message / IT: 10 secondi per messaggio
        dataRefreshInterval: 5 * 60 * 1000, // EN: 5 minutes / IT: 5 minuti
        languageToggleInterval: 15 // EN: 15 seconds / IT: 15 secondi
    };

    // EN: Object containing all translation strings with correct capitalization.
    // IT: Oggetto contenente tutte le stringhe di traduzione con le maiuscole corrette.
    const translations = {
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
     * EN: Fetches the message feed from the backend API for the configured chat ID.
     * IT: Recupera il feed dei messaggi dall'API del backend per l'ID della chat configurato.
     */
    async function fetchFeed() {
        if (!state.chatId) {
            console.error("Chat ID is not set. Cannot fetch feed.");
            dom.content.textContent = "Error: 'chat' parameter is missing in the URL.";
            return;
        }
        try {
            const response = await fetch(`/telegram/feed.json?chat=${state.chatId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            state.messages = data.messages || [];
            if (dom.title) dom.title.textContent = data.title || "Telegram Feed";

            if (state.messages.length === 0) {
                dom.content.textContent = "No messages found in this feed.";
            } else {
                setupCarousel();
            }
        } catch (error) {
            console.error("Failed to fetch feed:", error);
            dom.content.textContent = "Could not load messages. Please check the connection and Chat ID.";
        } finally {
            if (dom.loader) dom.loader.classList.add('hidden');
        }
    }

    /**
     * EN: Sets up the carousel by creating progress bars and starting the message rotation.
     * IT: Imposta il carosello creando le barre di progresso e avviando la rotazione dei messaggi.
     */
    function setupCarousel() {
        dom.progressContainer.innerHTML = '';
        state.messages.forEach(() => {
            const bar = document.createElement('div');
            bar.className = 'progress-bar';
            bar.innerHTML = '<div class="progress-fill"></div>';
            dom.progressContainer.appendChild(bar);
        });

        clearInterval(state.carouselInterval);
        state.currentIndex = 0;
        displayMessage();
        state.carouselInterval = setInterval(nextMessage, config.messageDuration);
    }

    /**
     * EN: Displays the message at the current index and updates the UI.
     * IT: Mostra il messaggio all'indice corrente e aggiorna la UI.
     */
    function displayMessage() {
        const msg = state.messages[state.currentIndex];
        if (!msg) return;

        dom.content.innerHTML = `<span>${msg.content.replace(/\n/g, '<br>')}</span>`;
        dom.author.textContent = msg.author;
        dom.timestamp.textContent = msg.timestamp;

        const contentSpan = dom.content.querySelector('span');
        if (contentSpan && contentSpan.scrollHeight > dom.content.clientHeight) {
            dom.content.classList.add('scroll');
        } else {
            dom.content.classList.remove('scroll');
        }

        updateProgressBars();
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
    function updateProgressBars() {
        const bars = dom.progressContainer.children;
        for (let i = 0; i < bars.length; i++) {
            bars[i].classList.remove('active', 'seen');
            if (i < state.currentIndex) {
                bars[i].classList.add('seen');
            } else if (i === state.currentIndex) {
                bars[i].classList.add('active');
            }
        }
    }

    /**
     * EN: Updates the live clock and date display in the corners of the screen.
     * IT: Aggiorna l'orologio e la data in tempo reale negli angoli dello schermo.
     */
    function updateClockAndDate() {
        const now = new Date();
        const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false, timeZone: 'Europe/Rome' };
        dom.clock.textContent = now.toLocaleTimeString('it-IT', timeOptions);

        // EN: Manually construct the date string using translations for correct capitalization.
        // IT: Costruisce manualmente la stringa della data usando le traduzioni per la maiuscola corretta.
        const lang = translations[state.currentLanguage];
        const dayName = lang.days[now.getDay()];
        const monthName = lang.months[now.getMonth()];
        dom.date.textContent = `${dayName}, ${now.getDate()} ${monthName} ${now.getFullYear()}`;
    }

    /**
     * EN: Toggles the display language between Italian and English.
     * IT: Alterna la lingua di visualizzazione tra italiano e inglese.
     */
    function toggleLanguage() {
        state.currentLanguage = (state.currentLanguage === 'it') ? 'en' : 'en';
        dom.body.className = 'lang-' + state.currentLanguage;
        // EN: Update date immediately after language change.
        // IT: Aggiorna la data immediatamente dopo il cambio di lingua.
        updateClockAndDate();
    }

    /**
     * EN: Initialization function that runs once the page is loaded.
     * IT: Funzione di inizializzazione che viene eseguita una volta caricata la pagina.
     */
    function init() {
        dom.body.className = 'lang-' + state.currentLanguage;

        const urlParams = new URLSearchParams(window.location.search);
        state.chatId = urlParams.get('chat');

        const classroom = urlParams.get('classroom');
        if (classroom && dom.classroomName) {
            dom.classroomName.textContent = classroom;
        }

        updateClockAndDate();
        fetchFeed();

        let secondsCounter = 0;
        setInterval(() => {
            secondsCounter++;
            updateClockAndDate();

            // EN: Toggle language at the specified interval.
            // IT: Cambia la lingua all'intervallo specificato.
            if (secondsCounter % config.languageToggleInterval === 0) {
                toggleLanguage();
            }

            // EN: Refresh data periodically.
            // IT: Aggiorna i dati periodicamente.
            if (secondsCounter % (config.dataRefreshInterval / 1000) === 0) {
                fetchFeed();
            }
        }, 1000);

        // EN: Full page reload every few hours to prevent long-term issues.
        // IT: Ricarica completa della pagina ogni qualche ora per prevenire problemi a lungo termine.
        setTimeout(() => window.location.reload(true), 4 * 60 * 60 * 1000);
    }

    init();
});