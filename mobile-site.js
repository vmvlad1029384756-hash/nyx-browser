/* NYX website install support: PWA install prompt + iOS home-screen guidance. */
(() => {
  "use strict";

  const installButton = document.getElementById("pwa-install-button");
  const status = document.getElementById("pwa-install-status");
  let installPrompt = null;

  const language = () => document.documentElement.lang === "en" ? "en" : "ru";
  const copy = {
    ru: {
      install: "Установить сайт NYX",
      ready: "Браузер поддерживает установку. Нажми кнопку, чтобы добавить сайт на главный экран.",
      done: "NYX добавлен на главный экран.",
      dismissed: "Установка не завершена. Её можно запустить позже из меню браузера.",
      ios: "Открой эту страницу в Safari → «Поделиться» → «На экран Домой».",
      android: "Открой меню Chrome (⋮) → «Установить приложение» или «Добавить на главный экран».",
      standalone: "Сайт уже открыт в установленном режиме.",
      failed: "Установка сейчас недоступна. Проверь меню своего браузера."
    },
    en: {
      install: "Install the NYX website",
      ready: "Your browser supports installation. Use this button to add the website to your home screen.",
      done: "NYX was added to your home screen.",
      dismissed: "Installation was not completed. You can try again from the browser menu later.",
      ios: "Open this page in Safari → Share → Add to Home Screen.",
      android: "Open Chrome menu (⋮) → Install app or Add to Home screen.",
      standalone: "The website is already running in its installed mode.",
      failed: "Installation is not available right now. Check your browser menu."
    }
  };

  const isStandalone = () =>
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;

  const isIOS = () => /iphone|ipad|ipod/i.test(navigator.userAgent) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);

  const setStatus = (key) => {
    if (status) status.textContent = copy[language()][key];
  };

  const updateLanguage = () => {
    document.querySelectorAll("[data-mobile-ru][data-mobile-en]").forEach((element) => {
      element.textContent = element.getAttribute("data-mobile-" + language()) || "";
    });
    if (installButton) installButton.textContent = copy[language()].install;
    if (isStandalone()) setStatus("standalone");
    else if (installPrompt && installButton && !installButton.hidden) setStatus("ready");
    else if (isIOS()) setStatus("ios");
    else setStatus("android");
  };

  if (installButton) {
    installButton.addEventListener("click", async () => {
      if (!installPrompt) {
        setStatus("failed");
        return;
      }
      installPrompt.prompt();
      const choice = await installPrompt.userChoice;
      installPrompt = null;
      installButton.hidden = true;
      setStatus(choice && choice.outcome === "accepted" ? "done" : "dismissed");
    });
  }

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    installPrompt = event;
    if (installButton && !isStandalone()) {
      installButton.hidden = false;
      setStatus("ready");
    }
  });

  window.addEventListener("appinstalled", () => {
    if (installButton) installButton.hidden = true;
    setStatus("done");
  });

  const languageButton = document.getElementById("language-toggle");
  if (languageButton) languageButton.addEventListener("click", updateLanguage);
  updateLanguage();

  if ("serviceWorker" in navigator && window.isSecureContext) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/service-worker.js", { scope: "/" })
        .catch((error) => console.warn("NYX offline support could not be enabled:", error));
    }, { once: true });
  }
})();
