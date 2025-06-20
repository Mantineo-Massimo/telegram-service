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

// EN: IDs of key DOM elements
// IT: ID dei principali elementi del DOM
const IDS = {
  TITLE:            'title',
  CONTAINER:        'container',
  CONTENT:          'content',
  AUTHOR:           'author',
  DATE:             'date',
  PROGRESS_BAR:     'progress-bar',
  CLOCK:            'clock',
  CLASSROOM_NAME:   'classroom-name',
  CURRENT_DATE:     'current-date'
};

// EN: CSS class names used for dynamic styling
// IT: Nomi delle classi CSS per lo styling dinamico
const CLASSES = {
  SCROLL:            'scroll',
  SEEN:              'seen',
  PROGRESS_BAR_ITEM: 'progress-bar',
  PROGRESS_FILL:     'progress-fill'
};

let messages       = [];               // EN: Fetched message objects   IT: Oggetti messaggio recuperati
let currentIndex   = 0;                // EN: Index of currently shown   IT: Indice del messaggio corrente
const LANGUAGES    = ["it","en"];      // EN: Supported languages         IT: Lingue supportate
let languageIndex  = 0;                // EN: Current language index      IT: Indice lingua corrente
let currentLanguage = LANGUAGES[languageIndex];

const italianDayNames = [              // IT: Nomi giorni in italiano
  "domenica","lunedì","martedì","mercoledì",
  "giovedì","venerdì","sabato"
];
const italianMonthNames = [            // IT: Nomi mesi in italiano
  "gennaio","febbraio","marzo","aprile","maggio","giugno",
  "luglio","agosto","settembre","ottobre","novembre","dicembre"
];

/*
EN: Converts markdown-like **bold** and *italic* to HTML.
IT: Converte **grassetto** e *corsivo* in HTML.
*/
function formatMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

/*
EN: Creates 'total' progress-bar items inside the PROGRESS_BAR container.
IT: Crea 'total' elementi progress-bar nel contenitore PROGRESS_BAR.
*/
function createProgressBars(total) {
  const container = document.getElementById(IDS.PROGRESS_BAR);
  container.innerHTML = "";  // clear existing

  for (let i = 0; i < total; i++) {
    const bar = document.createElement("div");
    bar.className = CLASSES.PROGRESS_BAR_ITEM;

    const fill = document.createElement("div");
    fill.className = CLASSES.PROGRESS_FILL;

    bar.appendChild(fill);
    container.appendChild(bar);
  }
}

/*
EN: Updates each progress bar's fill and animation based on currentIndex.
IT: Aggiorna larghezza e animazione di ogni barra in base a currentIndex.
*/
function updateProgressBars() {
  const bars = document.querySelectorAll(`.${CLASSES.PROGRESS_BAR_ITEM}`);
  bars.forEach((bar, i) => {
    const fill = bar.querySelector(`.${CLASSES.PROGRESS_FILL}`);
    fill.style.animation = 'none';
    fill.offsetHeight;  // force reflow

    if (i < currentIndex) {
      bar.classList.add(CLASSES.SEEN);
      fill.style.width = '100%';
    } else {
      bar.classList.remove(CLASSES.SEEN);
      fill.style.width = '0%';
    }

    if (i === currentIndex) {
      fill.style.animation = 'fill 20s linear forwards';
    }
  });
}

/*
EN: Displays the message at currentIndex:
    - Inserts formatted content
    - Applies scrolling if overflow
    - Updates author/date
    - Advances currentIndex
IT: Mostra il messaggio a currentIndex:
    - Inserisce contenuto formattato
    - Abilita scroll in caso di overflow
    - Aggiorna autore/data
    - Incrementa currentIndex
*/
function showMessage() {
  if (messages.length === 0) return;

  const msg = messages[currentIndex];
  const contentEl = document.getElementById(IDS.CONTENT);
  contentEl.innerHTML = `<span>${formatMarkdown(msg.content)}</span>`;
  contentEl.classList.remove(CLASSES.SCROLL);

  // check for overflow to add scrolling
  setTimeout(() => {
    const span = contentEl.querySelector('span');
    const lineHeight = parseFloat(getComputedStyle(contentEl).lineHeight);
    const maxHeight  = parseFloat(getComputedStyle(contentEl).maxHeight);
    if (span.scrollHeight > maxHeight + lineHeight) {
      contentEl.classList.add(CLASSES.SCROLL);
    }
  }, 100);

  document.getElementById(IDS.AUTHOR).textContent = msg.author;
  document.getElementById(IDS.DATE).textContent   = msg.date;

  updateProgressBars();
  currentIndex = (currentIndex + 1) % messages.length;
}

/*
EN: Retrieves the value of a URL parameter by name.
IT: Recupera il valore di un parametro URL per nome.
*/
function getURLParameter(name) {
  return new URLSearchParams(window.location.search).get(name);
}

/*
EN: Fetches messages from the backend API for the given chat ID,
    updates the messages array, and initializes or updates UI.
IT: Recupera messaggi dall’API per il chat ID,
    aggiorna l’array messages e aggiorna l’interfaccia.
*/
function loadMessages() {
  const chatId = getURLParameter("chat");
  if (!chatId) {
    console.error("Missing 'chat' parameter in URL");
    return;
  }

  fetch(`/feed.json?chat=${encodeURIComponent(chatId)}`)
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then(data => {
      const newMessages = data.messages || [];

      if (data.title) {
        document.getElementById(IDS.TITLE).textContent = data.title;
      }

      if (messages.length === 0) {
        messages = newMessages;
        createProgressBars(messages.length);
        showMessage();
      } else if (JSON.stringify(newMessages) !== JSON.stringify(messages)) {
        const seen = messages.slice(0, currentIndex);
        messages = newMessages;
        currentIndex = seen.length % messages.length;
        createProgressBars(messages.length);
      }
    })
    .catch(err => {
      console.error("Error fetching messages:", err);
    });
}

/*
EN: Pads single-digit numbers with a leading zero.
IT: Aggiunge zero a sinistra ai numeri a una cifra.
*/
function padTwo(n) {
  return (n < 10 ? "0" : "") + n;
}

/*
EN: Updates the digital clock element every second.
IT: Aggiorna l’orologio digitale ogni secondo.
*/
function updateClock() {
  const now = new Date();
  document.getElementById(IDS.CLOCK).textContent =
    `${padTwo(now.getHours())}:${padTwo(now.getMinutes())}:${padTwo(now.getSeconds())}`;
}

/*
EN: Updates the date display in the current language.
IT: Aggiorna la visualizzazione della data nella lingua corrente.
*/
function updateDate() {
  const today = new Date();
  const dayName = (currentLanguage === "it")
    ? italianDayNames[today.getDay()]
    : today.toLocaleDateString("en-GB", { weekday: "long" }).toLowerCase();
  const monthName = (currentLanguage === "it")
    ? italianMonthNames[today.getMonth()]
    : today.toLocaleDateString("en-GB", { month: "long" });
  const formatted =
    `${dayName.charAt(0).toUpperCase() + dayName.slice(1)} ${today.getDate()} ${monthName} ${today.getFullYear()}`;
  document.getElementById(IDS.CURRENT_DATE).textContent = formatted;
}

/*
EN: Toggles UI language between Italian and English every 15 seconds.
IT: Alterna lingua italiano/inglese ogni 15 secondi.
*/
function toggleLanguage() {
  languageIndex = 1 - languageIndex;
  currentLanguage = LANGUAGES[languageIndex];
  updateClock();
  updateDate();
}

/*
EN: Mapping of classroom IDs to human-readable names.
IT: Mappatura degli ID delle aule in nomi leggibili.
*/
const CLASSROOM_NAMES = {
  "5f775da9bb0c1600171ae370": "A-1-1",
  "5f778ceabab2280018354c66": "A-1-2",
  "5f77a3c28e23b1001b1b8dd1": "A-1-3",
  "5f77ac63caaa8600182d1aa3": "A-1-4",
  "5f7ede92090abe00160f2b63": "A-1-5",
  "5f7eebfa090abe00160f3069": "A-1-6",
  "6038e6b089cb050017681bc6": "A-1-7",
  "6038e6f495192a0018abbe35": "A-1-8",
  "6144b30f4478e70018ec408f": "A-S-1",
  "6144b36b4478e70018ec4091": "A-S-2",
  "6144b4404478e70018ec409d": "A-S-3",
  "6144b4a006477900174b0ce3": "A-S-6",
  "6144b4c14478e70018ec40d5": "A-S-7",
  "6144b4da06477900174b0cf2": "A-S-8",
  "6144b558dec1980017698b99": "A-T-1",
  "6144b5bbdec1980017698b9d": "A-T-2",
  "6144b5f7dec1980017698ba9": "A-T-3",
  "6144b62e06477900174b0cfd": "A-T-4",
  "6144b6dedec1980017698bae": "A-T-5",
  "6144b73f4478e70018ec4130": "A-T-6",
  "6144b6bb4478e70018ec412c": "A-T-7",
  "6144b77e4478e70018ec4133": "A-T-8",
  "6144b7af06477900174b0d23": "A-T-9",
  "6144b65ea673ee001710c74f": "A-T-10",
  "6144b7d7a673ee001710c7bf": "A-T-11"
};


/*
EN: Sets the classroom name based on URL parameter or default.
IT: Imposta il nome aula dal parametro URL o default.
*/
const classroomId = getURLParameter("classroom");
document.getElementById(IDS.CLASSROOM_NAME).textContent =
  (classroomId && CLASSROOM_NAMES[classroomId])
    ? CLASSROOM_NAMES[classroomId]
    : "Undefined Classroom";

// initialize everything
loadMessages();
setInterval(showMessage, 20000);
setInterval(loadMessages, 60000);
setInterval(updateClock, 1000);
setInterval(toggleLanguage, 15000);
updateClock();
updateDate();
