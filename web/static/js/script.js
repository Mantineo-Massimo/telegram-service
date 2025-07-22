/*
EN: Main script for the kiosk display application.
    - Defines all element IDs and CSS class names as constants
    - Rotates messages fetched from Telegram via API
    - Formats markdown syntax in message content
    - Shows progress bars for messages
    - Displays live clock and date with bilingual support
    - Toggles language between Italian and English
    - Maps classroom IDs to readable names
IT: Script principale per l’applicazione kiosk.
    - Definisce tutti gli ID degli elementi e i nomi delle classi CSS come costanti
    - Ruota i messaggi recuperati da Telegram tramite API
    - Format markdown nei contenuti dei messaggi
    - Mostra barre di progresso per i messaggi
    - Visualizza orologio e data con supporto bilingue
    - Alterna lingua tra italiano e inglese
    - Mappa ID aula in nomi leggibili
*/

// IDs of key DOM elements
const IDS = {
    TITLE: 'title',
    CONTAINER: 'container',
    CONTENT: 'content',
    AUTHOR: 'author',
    DATE: 'date',
    PROGRESS_BAR: 'progress-bar',
    CLOCK: 'clock',
    CLASSROOM_NAME: 'classroom-name',
    CURRENT_DATE: 'current-date'
};

// CSS class names used for dynamic styling
const CLASSES = {
    SCROLL: 'scroll',
    SEEN: 'seen',
    PROGRESS_BAR_ITEM: 'progress-bar',
    PROGRESS_FILL: 'progress-fill'
};

// Global variables
let messages = [];
let currentIndex = 0;
const LANGUAGES = ["it", "en"];
let languageIndex = 0;
let currentLanguage = LANGUAGES[languageIndex];
const italianDayNames = ["domenica", "lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato"];
const italianMonthNames = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"];
let messageIntervalId = null; // Holds the ID of the message rotation interval

/**
 * Converts markdown-like **bold** and *italic* to HTML.
 * @param {string} text - The text to format.
 * @returns {string} The HTML formatted text.
 */
function formatMarkdown(text) {
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>');
}

/**
 * Creates progress bar elements based on the total number of messages.
 * @param {number} total - The total number of messages.
 */
function createProgressBars(total) {
    const container = document.getElementById(IDS.PROGRESS_BAR);
    container.innerHTML = "";
    for (let i = 0; i < total; i++) {
        const bar = document.createElement("div");
        bar.className = CLASSES.PROGRESS_BAR_ITEM;
        const fill = document.createElement("div");
        fill.className = CLASSES.PROGRESS_FILL;
        bar.appendChild(fill);
        container.appendChild(bar);
    }
}

/**
 * Updates the fill and animation of each progress bar.
 */
function updateProgressBars() {
    const bars = document.querySelectorAll(`.${CLASSES.PROGRESS_BAR_ITEM}`);
    bars.forEach((bar, i) => {
        const fill = bar.querySelector(`.${CLASSES.PROGRESS_FILL}`);
        fill.style.animation = 'none';
        fill.offsetHeight; // Force reflow to restart animation
        if (i < currentIndex) {
            bar.classList.add(CLASSES.SEEN);
            fill.style.width = '100%';
        } else {
            bar.classList.remove(CLASSES.SEEN);
            fill.style.width = '0%';
        }
        if (i === currentIndex) {
            fill.style.animation = 'fill 10s linear forwards';
        }
    });
}

/**
 * Displays the message at the current index.
 */
function showMessage() {
    if (messages.length === 0) return;
    const msg = messages[currentIndex];
    const contentEl = document.getElementById(IDS.CONTENT);

    contentEl.innerHTML = `<span>${formatMarkdown(msg.content)}</span>`;
    contentEl.classList.remove(CLASSES.SCROLL); // Heavy animation removed for performance

    document.getElementById(IDS.AUTHOR).textContent = msg.author;
    document.getElementById(IDS.DATE).textContent = msg.date;

    updateProgressBars();
    currentIndex = (currentIndex + 1) % messages.length;
}

/**
 * Retrieves a URL parameter by its name.
 * @param {string} name - The name of the parameter.
 * @returns {string|null} The value of the parameter or null.
 */
function getURLParameter(name) {
    return new URLSearchParams(window.location.search).get(name);
}

/**
 * Fetches messages from the backend and initializes the display loop.
 */
function loadMessages() {
    const chatId = getURLParameter("chat");
    if (!chatId) {
        console.error("Missing 'chat' parameter in URL");
        document.getElementById(IDS.CONTENT).textContent = "Errore: parametro 'chat' mancante.";
        return;
    }

    fetch(`/feed.json?chat=${encodeURIComponent(chatId)}`)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(data => {
            messages = data.messages || [];
            if (data.title) {
                document.getElementById(IDS.TITLE).textContent = data.title;
            }

            if (messages.length > 0) {
                // If messages are loaded successfully
                createProgressBars(messages.length);
                showMessage(); // Show the first message immediately

                // And ONLY NOW start the interval for subsequent messages
                if (messageIntervalId) {
                    clearInterval(messageIntervalId);
                }
                messageIntervalId = setInterval(showMessage, 10000);
            } else {
                // If there are no messages to display
                document.getElementById(IDS.CONTENT).textContent = "Nessun messaggio da visualizzare.";
            }
        })
        .catch(err => {
            console.error("Error fetching messages:", err);
            document.getElementById(IDS.CONTENT).textContent = "Impossibile caricare i messaggi.";
        });
}

/**
 * Pads a number with a leading zero if it's a single digit.
 * @param {number} n - The number to pad.
 * @returns {string} The padded number as a string.
 */
function padTwo(n) {
    return (n < 10 ? "0" : "") + n;
}

/**
 * Updates the digital clock every second.
 */
function updateClock() {
    const now = new Date();
    document.getElementById(IDS.CLOCK).textContent = `${padTwo(now.getHours())}:${padTwo(now.getMinutes())}:${padTwo(now.getSeconds())}`;
}

/**
 * Updates the date display in the current language.
 */
function updateDate() {
    const today = new Date();
    const dayName = (currentLanguage === "it") ? italianDayNames[today.getDay()] : today.toLocaleDateString("en-GB", { weekday: "long" }).toLowerCase();
    const monthName = (currentLanguage === "it") ? italianMonthNames[today.getMonth()] : today.toLocaleDateString("en-GB", { month: "long" });
    const formatted = `${dayName.charAt(0).toUpperCase() + dayName.slice(1)} ${today.getDate()} ${monthName} ${today.getFullYear()}`;
    document.getElementById(IDS.CURRENT_DATE).textContent = formatted;
}

/**
 * Toggles the UI language and updates language-dependent elements.
 */
function toggleLanguage() {
    languageIndex = 1 - languageIndex;
    currentLanguage = LANGUAGES[languageIndex];
    updateDate(); // Only the date needs a language update
}


// --- INITIALIZATION BLOCK ---

// Set the classroom name from URL parameter
const classroomId = getURLParameter("classroom");
document.getElementById(IDS.CLASSROOM_NAME).textContent = classroomId ? classroomId : "Aula non definita";

// Start the functions that do not depend on fetched data
updateClock();
updateDate();
setInterval(updateClock, 1000);
setInterval(toggleLanguage, 15000);

// Finally, load the messages from the server
loadMessages();