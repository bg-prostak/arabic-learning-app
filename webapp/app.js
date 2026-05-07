const tg = window.Telegram?.WebApp;

if (tg) {
  tg.ready();
  tg.expand();
}

const app = document.querySelector("#app");
const navButtons = [...document.querySelectorAll(".nav-item")];
const imageDialog = document.querySelector("#imageDialog");
const dialogImage = document.querySelector("#dialogImage");
const closeImage = document.querySelector("#closeImage");
const themeButton = document.querySelector("#themeButton");

const catalog = {
  chapters: [],
  rules: []
};

const state = {
  view: "home",
  words: {},
  search: "",
  activeChapter: "",
  flashcard: null,
  flashcardRevealed: false,
  test: null
};

const progress = loadProgress();

function loadProgress() {
  try {
    return JSON.parse(localStorage.getItem("arabicAcademyProgress")) || {};
  } catch {
    return {};
  }
}

function saveProgress() {
  localStorage.setItem("arabicAcademyProgress", JSON.stringify(progress));
}

async function loadCatalog() {
  const response = await fetch("content/chapters.json");
  const content = await response.json();
  catalog.chapters = content.chapters;
  catalog.rules = content.rules || [];
  state.activeChapter = catalog.chapters[0]?.id || "";
}

async function loadWords(chapterId) {
  if (state.words[chapterId]) {
    return state.words[chapterId];
  }

  const chapter = chapterById(chapterId);
  const response = await fetch(chapter.webWords || chapter.words);
  const words = await response.json();
  state.words[chapterId] = words;
  return words;
}

function chapterById(chapterId) {
  return catalog.chapters.find((chapter) => chapter.id === chapterId) || catalog.chapters[0];
}

function currentChapter() {
  return chapterById(state.activeChapter);
}

function sample(items, count) {
  return [...items].sort(() => Math.random() - 0.5).slice(0, count);
}

function pickRandom(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function assetPath(item) {
  return item.webPath || item.path;
}

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
}

function openImage(path, title) {
  dialogImage.src = path;
  dialogImage.alt = title;
  imageDialog.showModal();
}

function setView(view) {
  state.view = view;
  state.test = null;
  navButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });
  render();
}

function chapterTabs() {
  return `
    <div class="chapter-tabs">
      ${catalog.chapters.map((chapter) => `
        <button class="tab-button ${chapter.id === state.activeChapter ? "active" : ""}" data-chapter-tab="${chapter.id}" type="button">
          ${escapeHtml(chapter.title)}
        </button>
      `).join("")}
    </div>
  `;
}

function renderHero() {
  return `
    <section class="hero">
      <p class="eyebrow">Курс академии</p>
      <h2>Арабский в кармане</h2>
      <p>Главы, диалоги, правила, словари и тренировки собраны в одном месте. Добавляем материалы по мере прохождения курса.</p>
    </section>

    <section class="grid">
      <button class="card" data-open="home">
        <strong>Главы</strong>
        <span>Выбери нужную главу, открой диалоги или переходи к словарю и повторению.</span>
      </button>
    </section>
  `;
}

function renderHome() {
  const chapterCards = catalog.chapters.map((chapter) => `
    <button class="card" data-open="chapter" data-chapter="${chapter.id}">
      <strong>${escapeHtml(chapter.title)}</strong>
      <span>${escapeHtml(chapter.subtitle || "Материалы главы")}</span>
    </button>
  `).join("");

  app.innerHTML = `
    ${renderHero()}
    <section>
      <h2>Главы</h2>
      <div class="grid">${chapterCards}</div>
    </section>
  `;
}

async function renderDictionary(resetSearch = true) {
  if (resetSearch) {
    state.search = "";
  }
  const chapter = currentChapter();
  const words = await loadWords(chapter.id);
  const query = state.search.trim().toLowerCase();
  const filtered = words.filter((word) => {

    const arabic = String(word.arabic || "").normalize("NFC");

    const translation = String(word.translation || "")
      .toLowerCase()
      .normalize("NFC");

    return arabic.includes(query) ||
      translation.includes(query);

  });

  app.innerHTML = `
    <section class="panel">
      <h2>Словарь</h2>
      ${chapterTabs()}
      <p class="muted">${escapeHtml(chapter.title)}. Найдено: ${filtered.length}</p>
      <div class="toolbar">
        <input class="search" id="searchInput" type="search" placeholder="Найти слово или перевод" value="${escapeHtml(state.search)}">
      </div>
      <div class="word-list">
        ${filtered.map((word) => `
          <article class="word-card">
            <div>
              <div class="arabic">${escapeHtml(word.arabic)}</div>
              <div class="translation">${escapeHtml(word.translation)}</div>
            </div>
          </article>
        `).join("")}
      </div>
    </section>
  `;

  document.querySelector("#searchInput").addEventListener("input", async (event) => {

    state.search = event.target.value;

    await renderDictionary(false);

    const input = document.querySelector("#searchInput");

    input.focus();

    input.setSelectionRange(
      state.search.length,
      state.search.length
    );
  });
}

function renderRules() {
  app.innerHTML = `
    <section class="panel">
      <h2>Правила</h2>
      <p class="muted">Общий справочник правил по всему курсу. Любой конспект можно открыть крупно.</p>
      <div class="media-grid">
        ${catalog.rules.map((rule) => `
          <button class="media-card" data-image="${assetPath(rule)}" data-title="${escapeHtml(rule.title)}">
            <img src="${assetPath(rule)}" alt="${escapeHtml(rule.title)}">
            <div>${escapeHtml(rule.title)}</div>
          </button>
        `).join("") || `<p class="muted">Правила ещё не добавлены.</p>`}
      </div>
    </section>
  `;
}

function renderChapter(chapterId) {
  const chapter = chapterById(chapterId);

  app.innerHTML = `
    <section class="panel">
      <button class="ghost-button" data-open="home" type="button">← Назад</button>
      <h2>${escapeHtml(chapter.title)}</h2>
      <p class="muted">${escapeHtml(chapter.subtitle || "Материалы главы")}</p>
      <h3>Диалоги</h3>
      <div class="media-grid">
        ${(chapter.dialogs || []).map((dialog) => `
          <button class="media-card" data-image="${assetPath(dialog)}" data-title="${escapeHtml(dialog.title)}">
            <img src="${assetPath(dialog)}" alt="${escapeHtml(dialog.title)}">
            <div>${escapeHtml(dialog.title)}</div>
          </button>
        `).join("") || `<p class="muted">Диалоги для этой главы ещё не добавлены.</p>`}
      </div>
    </section>
  `;
}

async function renderPractice() {
  const chapter = currentChapter();
  const words = await loadWords(chapter.id);

  if (!state.flashcard || state.flashcardChapter !== chapter.id) {
    state.flashcard = pickRandom(words);
    state.flashcardChapter = chapter.id;
    state.flashcardRevealed = false;
  }

  app.innerHTML = `
    <section class="panel">
      <h2>Повторение</h2>
      ${chapterTabs()}
      <p class="muted">${escapeHtml(chapter.title)}</p>
      <div class="grid two">
        <button class="primary-button" type="button">Карточки</button>
        <button class="ghost-button" id="startTest" type="button">Тест на 10 слов</button>
      </div>
    </section>

    <section class="flashcard">
      <div>
        <p class="eyebrow">${state.flashcardRevealed ? "Перевод" : "Вспомни перевод"}</p>
        <div class="${state.flashcardRevealed ? "result-score" : "arabic"}">
          ${escapeHtml(state.flashcardRevealed ? state.flashcard.translation : state.flashcard.arabic)}
        </div>
      </div>
    </section>

    <section class="grid two">
      <button class="ghost-button" id="revealCard" type="button">${state.flashcardRevealed ? "Скрыть" : "Показать перевод"}</button>
      <button class="primary-button" id="nextCard" type="button">Следующее слово</button>
    </section>
  `;

  document.querySelector("#revealCard").addEventListener("click", () => {
    state.flashcardRevealed = !state.flashcardRevealed;
    renderPractice();
  });

  document.querySelector("#nextCard").addEventListener("click", () => {
    progress.known = (progress.known || 0) + 1;
    saveProgress();
    state.flashcard = pickRandom(words);
    state.flashcardRevealed = false;
    renderPractice();
  });

  document.querySelector("#startTest").addEventListener("click", () => {
    startWebTest(words);
  });
}

function startWebTest(words) {
  const questions = sample(words, Math.min(10, words.length));
  state.test = {
    questions,
    index: 0,
    score: 0,
    answered: false,
    selected: null,
    options: null
  };
  renderTest();
}

function getTestOptions(words, currentWord) {
  const wrong = words
    .filter((word) => word.translation !== currentWord.translation)
    .map((word) => word.translation);

  return sample(wrong, Math.min(3, wrong.length))
    .concat(currentWord.translation)
    .sort(() => Math.random() - 0.5);
}

async function renderTest() {
  const words = await loadWords(state.activeChapter);
  const test = state.test;

  if (!test) {
    renderPractice();
    return;
  }

  if (test.index >= test.questions.length) {
    app.innerHTML = `
      <section class="panel">
        <h2>Тест завершён</h2>
        <p class="muted">Результат по главе: ${escapeHtml(currentChapter().title)}</p>
        <div class="result-score">${test.score} / ${test.questions.length}</div>
        <div class="grid two">
          <button class="primary-button" id="restartTest" type="button">Пройти ещё раз</button>
          <button class="ghost-button" id="backPractice" type="button">К карточкам</button>
        </div>
      </section>
    `;

    document.querySelector("#restartTest").addEventListener("click", () => startWebTest(words));
    document.querySelector("#backPractice").addEventListener("click", () => {
      state.test = null;
      renderPractice();
    });
    return;
  }

  const current = test.questions[test.index];

  if (!test.options) {
    test.options = getTestOptions(words, current);
  }

  app.innerHTML = `
    <section class="panel">
      <p class="eyebrow">Вопрос ${test.index + 1} / ${test.questions.length}</p>
      <h2 class="arabic">${escapeHtml(current.arabic)}</h2>
      <div class="grid">
        ${test.options.map((option, index) => {
    const isCorrect = option === current.translation;
    const selected = test.selected === index;
    const className = test.answered && isCorrect ? "correct" : test.answered && selected ? "wrong" : "";
    return `<button class="option-button ${className}" data-answer="${index}" type="button">${escapeHtml(option)}</button>`;
  }).join("")}
      </div>
      <div class="toolbar">
        <button class="ghost-button" id="cancelTest" type="button">К карточкам</button>
        <button class="primary-button" id="nextQuestion" type="button" ${test.answered ? "" : "disabled"}>${test.index + 1 === test.questions.length ? "Завершить" : "Дальше"}</button>
      </div>
    </section>
  `;

  document.querySelectorAll("[data-answer]").forEach((button) => {
    button.addEventListener("click", () => {
      if (test.answered) {
        return;
      }

      const selected = Number(button.dataset.answer);
      test.selected = selected;
      test.answered = true;

      if (test.options[selected] === current.translation) {
        test.score += 1;
      }

      renderTest();
    });
  });

  document.querySelector("#nextQuestion").addEventListener("click", () => {
    test.index += 1;
    test.answered = false;
    test.selected = null;
    test.options = null;
    renderTest();
  });

  document.querySelector("#cancelTest").addEventListener("click", () => {
    state.test = null;
    renderPractice();
  });
}

async function render() {
  if (state.view === "home") {
    renderHome();
  }

  if (state.view === "dictionary") {
    await renderDictionary();
  }

  if (state.view === "rules") {
    renderRules();
  }

  if (state.view === "practice") {
    await renderPractice();
  }
}

app.addEventListener("click", (event) => {
  const target = event.target.closest("[data-open], [data-image], [data-chapter-tab]");

  if (!target) {
    return;
  }

  if (target.dataset.chapterTab) {
    state.activeChapter = target.dataset.chapterTab;
    state.search = "";
    state.flashcard = null;
    state.test = null;
    render();
    return;
  }

  if (target.dataset.image) {
    openImage(target.dataset.image, target.dataset.title);
    return;
  }

  const open = target.dataset.open;

  if (open === "chapter") {
    renderChapter(target.dataset.chapter);
    return;
  }

  setView(open);
});

navButtons.forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.view));
});

closeImage.addEventListener("click", () => imageDialog.close());

themeButton.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  localStorage.setItem("arabicAcademyTheme", document.body.classList.contains("dark") ? "dark" : "light");
});

if (localStorage.getItem("arabicAcademyTheme") === "dark") {
  document.body.classList.add("dark");
}

loadCatalog()
  .then(() => loadWords(state.activeChapter))
  .then(render)
  .catch(() => {
    app.innerHTML = `
      <section class="panel">
        <h2>Не удалось загрузить материалы</h2>
        <p class="muted">Проверь файл webapp/content/chapters.json и запусти локальный сервер заново.</p>
      </section>
    `;
  });
