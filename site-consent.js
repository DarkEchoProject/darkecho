/* Dark Echo: opt-in Google Analytics, shared by all indexable pages. */
(function () {
  "use strict";

  const storageKey = "darkecho-analytics-choice-v1";
  const measurementId = "G-QSKD08ZSXE";
  let decision = null;
  let panel = null;
  let analyticsLoaded = false;

  try {
    const stored = window.localStorage.getItem(storageKey);
    if (stored === "yes" || stored === "no") decision = stored;
  } catch (_) {
    // If storage is unavailable, ask again rather than assuming consent.
  }

  function loadAnalytics() {
    if (analyticsLoaded) return;
    analyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("consent", "default", {
      analytics_storage: "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied"
    });
    window.gtag("consent", "update", { analytics_storage: "granted" });
    window.gtag("js", new Date());
    window.gtag("config", measurementId, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });
    const tag = document.createElement("script");
    tag.async = true;
    tag.src = "https://www.googletagmanager.com/gtag/js?id=" + measurementId;
    document.head.appendChild(tag);
  }

  function saveChoice(value) {
    const previous = decision;
    decision = value;
    try { window.localStorage.setItem(storageKey, value); } catch (_) {}
    if (panel) panel.hidden = true;
    if (value === "yes") {
      loadAnalytics();
    } else if (previous === "yes" && analyticsLoaded) {
      if (typeof window.gtag === "function") {
        window.gtag("consent", "update", { analytics_storage: "denied" });
      }
      window.location.reload();
    }
  }

  function showChoices() {
    if (!panel) return;
    panel.hidden = false;
    const allow = panel.querySelector("[data-choice='yes']");
    if (allow) allow.focus();
  }

  function buildPanel() {
    panel = document.createElement("div");
    panel.className = "de-consent-panel";
    panel.id = "de-consent-panel";
    panel.setAttribute("role", "region");
    panel.setAttribute("aria-label", "Analytics privacy choices");
    panel.hidden = decision !== null;
    panel.innerHTML =
      '<p>May we use optional Google Analytics to understand visits and improve this site? ' +
      'You can refuse and still browse normally. <a href="privacy.html">Privacy policy</a>.</p>' +
      '<div class="de-consent-actions">' +
      '<button type="button" data-choice="yes">Allow analytics</button>' +
      '<button type="button" data-choice="no">Reject analytics</button>' +
      '</div>';
    panel.addEventListener("click", function (event) {
      const button = event.target.closest("button[data-choice]");
      if (button) saveChoice(button.dataset.choice);
    });
    document.body.appendChild(panel);
    const manage = document.getElementById("de-privacy-manage");
    if (manage) {
      manage.setAttribute("aria-controls", "de-consent-panel");
      manage.addEventListener("click", showChoices);
    }
  }

  if (decision === "yes") loadAnalytics();
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildPanel, { once: true });
  } else {
    buildPanel();
  }
})();