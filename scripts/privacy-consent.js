(function () {
  var CONSENT_KEY = "midwestflip_analytics_consent_v1";
  var BANNER_ID = "privacy-consent-banner";
  var MATOMO_URL = "https://matomo.alphalockandsafe.com/matomo/";
  var MATOMO_SCRIPT = "https://matomo.alphalockandsafe.com/matomo/matomo.js";
  var MATOMO_SITE_ID = "4";

  function getStorageValue() {
    try {
      return window.localStorage.getItem(CONSENT_KEY);
    } catch (error) {
      return null;
    }
  }

  function setStorageValue(value) {
    try {
      window.localStorage.setItem(CONSENT_KEY, value);
    } catch (error) {
      return;
    }
  }

  function getRootPathFromScript() {
    var script = document.currentScript;
    if (!script || !script.src) {
      var scripts = document.getElementsByTagName("script");
      for (var i = scripts.length - 1; i >= 0; i -= 1) {
        if (scripts[i].src && scripts[i].src.indexOf("/scripts/privacy-consent.js") !== -1) {
          script = scripts[i];
          break;
        }
      }
    }

    if (script && script.src) {
      try {
        var scriptUrl = new URL(script.src, window.location.href);
        return scriptUrl.pathname.replace(/\/scripts\/privacy-consent\.js$/, "/");
      } catch (error) {
        return "/";
      }
    }

    return "/";
  }

  function buildSiteUrl(fileName) {
    var rootPath = getRootPathFromScript();
    return rootPath + fileName;
  }

  function loadMatomo() {
    if (window.__midwestMatomoLoaded) {
      return;
    }

    var _paq = (window._paq = window._paq || []);
    _paq.push(["setDoNotTrack", true]);
    _paq.push(["disableCookies"]);
    _paq.push(["setSecureCookie", true]);
    _paq.push(["setTrackerUrl", MATOMO_URL + "matomo.php"]);
    _paq.push(["setSiteId", MATOMO_SITE_ID]);
    _paq.push(["trackPageView"]);
    _paq.push(["enableLinkTracking"]);

    var script = document.createElement("script");
    script.async = true;
    script.src = MATOMO_SCRIPT;
    script.referrerPolicy = "strict-origin-when-cross-origin";
    document.head.appendChild(script);

    window.__midwestMatomoLoaded = true;
  }

  function hideBanner() {
    var banner = document.getElementById(BANNER_ID);
    if (!banner) {
      return;
    }

    banner.classList.remove("is-visible");
    banner.setAttribute("hidden", "hidden");
  }

  function showBanner() {
    var banner = ensureBanner();
    banner.removeAttribute("hidden");

    // Ensure the browser paints the unhidden state before transition.
    window.requestAnimationFrame(function () {
      banner.classList.add("is-visible");
    });
  }

  function applyConsent(choice) {
    setStorageValue(choice);

    if (choice === "accepted") {
      loadMatomo();
    }

    hideBanner();
  }

  function createBanner() {
    var banner = document.createElement("section");
    banner.id = BANNER_ID;
    banner.className = "consent-banner";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-live", "polite");
    banner.setAttribute("aria-label", "Privacy preferences");
    banner.setAttribute("hidden", "hidden");

    var privacyUrl = buildSiteUrl("privacy-policy.html");
    var termsUrl = buildSiteUrl("terms-of-service.html");

    banner.innerHTML =
      '<div class="consent-banner-inner">' +
      '<p class="consent-title">Privacy choices</p>' +
      '<p class="consent-text">We use privacy-first analytics only after approval. You can change this choice anytime.</p>' +
      '<p class="consent-links"><a href="' +
      privacyUrl +
      '">Privacy Policy</a> · <a href="' +
      termsUrl +
      '">Terms of Service</a></p>' +
      '<div class="consent-actions">' +
      '<button type="button" class="btn ghost" data-consent-action="reject">Decline</button>' +
      '<button type="button" class="btn" data-consent-action="accept">Accept Analytics</button>' +
      '</div>' +
      '</div>';

    var acceptButton = banner.querySelector('[data-consent-action="accept"]');
    var rejectButton = banner.querySelector('[data-consent-action="reject"]');

    if (acceptButton) {
      acceptButton.addEventListener("click", function () {
        applyConsent("accepted");
      });
    }

    if (rejectButton) {
      rejectButton.addEventListener("click", function () {
        applyConsent("rejected");
      });
    }

    return banner;
  }

  function ensureBanner() {
    var existing = document.getElementById(BANNER_ID);
    if (existing) {
      return existing;
    }

    var banner = createBanner();
    document.body.appendChild(banner);
    return banner;
  }

  function bindSettingsButtons() {
    var buttons = document.querySelectorAll("[data-open-consent]");
    for (var i = 0; i < buttons.length; i += 1) {
      buttons[i].addEventListener("click", function (event) {
        event.preventDefault();
        showBanner();
      });
    }
  }

  function initialize() {
    bindSettingsButtons();

    var consent = getStorageValue();
    if (consent === "accepted") {
      loadMatomo();
      return;
    }

    if (consent === "rejected") {
      return;
    }

    showBanner();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    initialize();
  }
})();
