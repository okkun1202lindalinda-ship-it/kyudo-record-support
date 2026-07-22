(() => {
  "use strict";

  const measurementId = "G-K09RH58W5E";
  const googleTagBaseUrl = "https://www.googletagmanager.com/gtag/js";
  const googleTagSelector = `script[src^="${googleTagBaseUrl}"]`;

  if (window.__kyudoJapanGa4Initialized) {
    return;
  }
  window.__kyudoJapanGa4Initialized = true;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag() {
    window.dataLayer.push(arguments);
  };

  const loadGoogleTag = () => {
    if (document.querySelector(googleTagSelector)) {
      return;
    }

    const googleTag = document.createElement("script");
    googleTag.async = true;
    googleTag.src =
      `${googleTagBaseUrl}?id=${encodeURIComponent(measurementId)}`;
    document.head.append(googleTag);
  };

  if (document.readyState === "complete") {
    loadGoogleTag();
  } else {
    window.addEventListener("load", loadGoogleTag, { once: true });
  }

  window.gtag("js", new Date());
  window.gtag("config", measurementId);
})();
