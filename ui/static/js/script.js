/**
 * Main script for the Telegram Feed Kiosk Display.
 * - Fetches messages from the backend JSON feed.
 * - Rotates through messages with a progress bar indicator.
 * - Handles auto-scrolling for long messages.
 * - Displays a live clock and date with bilingual support.
 * - Dynamically sets a classroom name from URL parameters.
 */
document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const dom = {
        title: document.getElementById('feed-title'),
        content: document.getElementById('message-content'),
        author: document.getElementById('message-author'),
        timestamp: document.getElementById('message-timestamp'),
        progressBarContainer: document.getElementById('progress-bar-container'),
        clock: document.getElementById('live-clock'),
        classroomName: document.getElementById('classroom-name'),
        currentDate: document.getElementById('current-date')
    };

    // --- State and Configuration ---
    let state = {
        messages: [],
        currentIndex: 0,
        currentLanguage: 'it'
    };
    const config = {
        messageRotationInterval: 10000, // 10 seconds
        feedUpdateInterval: 5000,       // 5 seconds
        languageToggleInterval: 15000,  // 15 seconds
        languages: ['it', 'en']
    };

    // --- Language Data ---
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
    
    // --- Utility Functions ---
    const getUrlParam = (name) => new URLSearchParams(window.location.search).get(name);
    const padZero = (n) => (n < 10 ? "0" : "") + n;
    const formatMarkdown = (text) => text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');

    // --- Core Functions ---
    function updateClockAndDate() {
        const now = new Date();
        const lang = translations[state.currentLanguage];
        dom.clock.textContent = `${padZero(now.getHours())}:${padZero(now.getMinutes())}:${padZero(now.getSeconds())}`;
        const dayName = lang.days[now.getDay()];
        const monthName = lang.months[now.getMonth()];
        dom.currentDate.textContent = `${dayName} ${now.getDate()} ${now.getFullYear()}`;
    }

    function toggleLanguage() {
        const currentIndex = config.languages.indexOf(state.currentLanguage);
        const nextIndex = (currentIndex + 1) % config.languages.length;
        state.currentLanguage = config.languages[nextIndex];
        updateClockAndDate();
    }
    
    function setupClassroomName() {
        const classroomNameFromUrl = getUrlParam("classroom");
        dom.classroomName.textContent = classroomNameFromUrl || "Kiosk Display";
    }

    function createProgressBars(total) {
        dom.progressBarContainer.innerHTML = "";
        for (let i = 0; i < total; i++) {
            const barWrapper = document.createElement("div");
            barWrapper.className = 'progress-bar';
            const fill = document.createElement("div");
            fill.className = 'progress-fill';
            barWrapper.appendChild(fill);
            dom.progressBarContainer.appendChild(barWrapper);
        }
    }

    function updateProgressBars() {
        const bars = dom.progressBarContainer.children;
        for (let i = 0; i < bars.length; i++) {
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
        const msg = state.messages[state.currentIndex];
        dom.content.innerHTML = `<span>${formatMarkdown(msg.content)}</span>`;
        dom.author.textContent = msg.author;
        dom.timestamp.textContent = msg.timestamp;
        dom.content.classList.remove('scroll');
        setTimeout(() => {
            const contentHeight = dom.content.clientHeight;
            const spanHeight = dom.content.querySelector('span').clientHeight;
            if (spanHeight > contentHeight) {
                dom.content.classList.add('scroll');
            }
        }, 100);
        updateProgressBars();
        state.currentIndex++;
    }

    async function fetchMessages() {
        const chatId = getUrlParam("chat");
        if (!chatId) {
            dom.title.textContent = "Error";
            dom.content.textContent = "Missing 'chat' parameter in URL.";
            return;
        }
        try {
            const response = await fetch(`/feed.json?chat=${encodeURIComponent(chatId)}`);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const data = await response.json();
            dom.title.textContent = data.title || "Message Feed";
            if (JSON.stringify(data.messages) !== JSON.stringify(state.messages)) {
                state.messages = data.messages || [];
                state.currentIndex = 0;
                createProgressBars(state.messages.length);
                if (state.messages.length > 0) {
                    displayMessage();
                }
            }
        } catch (error) {
            console.error("Error fetching messages:", error);
            dom.content.textContent = "Could not load messages.";
        }
    }

    // --- Initialization ---
    function init() {
        fetchMessages();
        updateClockAndDate();
        setupClassroomName();
        setInterval(displayMessage, config.messageRotationInterval);
        setInterval(fetchMessages, config.feedUpdateInterval);
        setInterval(updateClockAndDate, 1000);
        setInterval(toggleLanguage, config.languageToggleInterval);
    }

    init();
});