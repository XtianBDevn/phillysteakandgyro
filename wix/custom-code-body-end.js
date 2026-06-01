/*
 * Philly Steak & Gyros - JavaScript-only Wix hotfix
 *
 * Use this when you need JavaScript, not Python.
 *
 * Wix admin Custom Code:
 * - If Wix asks for HTML, wrap this file in:
 *   <script> ...paste this file... </script>
 * - Place it in Body - end.
 * - Apply to all pages, preferably mobile only if Wix offers that option.
 *
 * Wix Velo:
 * - Paste inside the site-wide masterPage.js file.
 */
(function () {
  var STYLE_ID = "psg-wix-mobile-hotfix-style";
  var CTA_ID = "psg-cta-bar";
  var PHONE_NUMBER = "+18045621174";
  var DISPLAY_PHONE = "(804) 562-1174";
  var ADDRESS = "3443 W Cary St Richmond VA 23221";
  var DIRECTIONS_URL =
    "https://www.google.com/maps/dir/?api=1&destination=3443+W+Cary+St+Richmond+VA+23221";

  var CSS = [
    ":root {",
    "  --psg-brand: #c8102e;",
    "  --psg-ink: #1a1a1a;",
    "  --psg-line: #e8e2d6;",
    "  --psg-safe-bottom: env(safe-area-inset-bottom, 0px);",
    "}",
    "",
    "@supports (height: 100dvh) {",
    "  .full-height-strip,",
    "  [data-mesh-id$=\"hero\"],",
    "  .hero-section,",
    "  section[id*=\"hero\" i] {",
    "    min-height: 100dvh !important;",
    "  }",
    "}",
    "",
    "@media (max-width: 480px) {",
    "  html,",
    "  body {",
    "    max-width: 100% !important;",
    "    overflow-x: hidden !important;",
    "  }",
    "",
    "  img,",
    "  video,",
    "  iframe {",
    "    max-width: 100% !important;",
    "    height: auto !important;",
    "  }",
    "}",
    "",
    "@media (max-width: 768px) {",
    "  a,",
    "  button,",
    "  [role=\"button\"] {",
    "    min-height: 44px;",
    "  }",
    "}",
    "",
    "@media (min-width: 414px) and (max-width: 480px) {",
    "  [data-mesh-id$=\"contentWrapper\"] {",
    "    padding-left: 12px !important;",
    "    padding-right: 12px !important;",
    "  }",
    "}",
    "",
    "#" + CTA_ID + " {",
    "  position: fixed;",
    "  left: 0;",
    "  right: 0;",
    "  bottom: 0;",
    "  z-index: 99999;",
    "  display: grid;",
    "  grid-template-columns: 1fr 1fr 1fr;",
    "  background: #fff;",
    "  border-top: 1px solid var(--psg-line);",
    "  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.12);",
    "  padding-bottom: var(--psg-safe-bottom);",
    "  font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif;",
    "}",
    "",
    "#" + CTA_ID + " a {",
    "  min-height: 56px;",
    "  padding: 12px 4px;",
    "  border-left: 1px solid var(--psg-line);",
    "  color: var(--psg-ink);",
    "  display: flex;",
    "  align-items: center;",
    "  justify-content: center;",
    "  text-align: center;",
    "  text-decoration: none;",
    "  font-size: 14px;",
    "  font-weight: 700;",
    "  line-height: 1.2;",
    "}",
    "",
    "#" + CTA_ID + " a:first-child {",
    "  border-left: 0;",
    "}",
    "",
    "#" + CTA_ID + " a[data-primary] {",
    "  background: var(--psg-brand);",
    "  color: #fff;",
    "}",
    "",
    "#" + CTA_ID + " a:focus,",
    "#" + CTA_ID + " a:hover {",
    "  text-decoration: underline;",
    "}",
    "",
    "body {",
    "  padding-bottom: calc(60px + var(--psg-safe-bottom)) !important;",
    "}",
    "",
    "@media (min-width: 769px) {",
    "  #" + CTA_ID + " {",
    "    display: none;",
    "  }",
    "",
    "  body {",
    "    padding-bottom: 0 !important;",
    "  }",
    "}",
    "",
    "@media (prefers-reduced-motion: reduce) {",
    "  html {",
    "    scroll-behavior: auto !important;",
    "  }",
    "}",
  ].join("\n");

  function hasDom() {
    return (
      typeof document !== "undefined" &&
      document.head &&
      document.body &&
      typeof document.createElement === "function"
    );
  }

  function ready(callback) {
    if (!hasDom()) {
      return;
    }

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback);
    } else {
      callback();
    }
  }

  function injectCss() {
    if (document.getElementById(STYLE_ID)) {
      return;
    }

    var style = document.createElement("style");
    style.id = STYLE_ID;
    style.type = "text/css";
    style.appendChild(document.createTextNode(CSS));
    document.head.appendChild(style);
  }

  function prefersReducedMotion() {
    return (
      typeof window !== "undefined" &&
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
  }

  function scrollToOrdering(event) {
    var orderTarget = document.querySelector(
      '[href*="doordash"], [href*="ubereats"], [href*="grubhub"], #order'
    );

    if (!orderTarget) {
      return;
    }

    event.preventDefault();
    orderTarget.scrollIntoView({
      behavior: prefersReducedMotion() ? "auto" : "smooth",
      block: "center",
    });
  }

  function injectMobileCta() {
    if (document.getElementById(CTA_ID)) {
      return;
    }

    var cta = document.createElement("nav");
    cta.id = CTA_ID;
    cta.setAttribute("aria-label", "Quick actions");
    cta.innerHTML =
      '<a href="tel:' +
      PHONE_NUMBER +
      '" aria-label="Call Philly Steak and Gyros at ' +
      DISPLAY_PHONE +
      '">Call</a>' +
      '<a href="' +
      DIRECTIONS_URL +
      '" aria-label="Get directions to ' +
      ADDRESS +
      '" rel="noopener">Directions</a>' +
      '<a data-primary href="#order" aria-label="Order online">Order</a>';

    cta.querySelector("[data-primary]").addEventListener("click", scrollToOrdering);
    document.body.appendChild(cta);
  }

  ready(function () {
    injectCss();
    injectMobileCta();
  });
})();
