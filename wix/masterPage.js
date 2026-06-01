/*
 * Philly Steak & Gyros - Wix masterPage.js hotfix
 *
 * Install in Wix:
 * 1. Enable Dev Mode / Velo.
 * 2. Open the site-wide "masterPage.js" file.
 * 3. Paste this file's contents.
 * 4. Preview desktop and mobile, then Publish.
 *
 * Notes:
 * - This runtime hotfix is for the current Wix site. It does not replace
 *   local-site/css/site.css.
 * - Wix can change generated class names after editor saves, so selectors are
 *   scoped to stable HTML tags, ARIA attributes, href patterns, and our own IDs.
 * - If the Velo environment blocks direct DOM access, use the same CSS/HTML via
 *   Settings -> Custom Code -> Body End instead.
 */

const PSG_HOTFIX_STYLE_ID = "psg-wix-mobile-hotfix-style";
const PSG_CTA_ID = "psg-cta-bar";

const PHONE_NUMBER = "+18045621174";
const DISPLAY_PHONE = "(804) 562-1174";
const ADDRESS = "3443 W Cary St Richmond VA 23221";
const DIRECTIONS_URL =
  "https://www.google.com/maps/dir/?api=1&destination=3443+W+Cary+St+Richmond+VA+23221";

const HOTFIX_CSS = `
  :root {
    --psg-brand: #c8102e;
    --psg-brand-dark: #8a0a1e;
    --psg-ink: #1a1a1a;
    --psg-line: #e8e2d6;
    --psg-safe-bottom: env(safe-area-inset-bottom, 0px);
  }

  @supports (height: 100dvh) {
    .full-height-strip,
    [data-mesh-id$="hero"],
    .hero-section,
    section[id*="hero" i] {
      min-height: 100dvh !important;
    }
  }

  @media (max-width: 480px) {
    html,
    body {
      overflow-x: hidden !important;
      max-width: 100% !important;
    }

    img,
    video,
    iframe {
      max-width: 100% !important;
      height: auto !important;
    }
  }

  @media (max-width: 768px) {
    a,
    button,
    [role="button"] {
      min-height: 44px;
    }
  }

  @media (min-width: 414px) and (max-width: 480px) {
    [data-mesh-id$="contentWrapper"] {
      padding-left: 12px !important;
      padding-right: 12px !important;
    }
  }

  #${PSG_CTA_ID} {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 99999;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    background: #fff;
    border-top: 1px solid var(--psg-line);
    box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.12);
    padding-bottom: var(--psg-safe-bottom);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  #${PSG_CTA_ID} a {
    min-height: 56px;
    padding: 12px 4px;
    border-left: 1px solid var(--psg-line);
    color: var(--psg-ink);
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    text-decoration: none;
    font-size: 14px;
    font-weight: 700;
    line-height: 1.2;
  }

  #${PSG_CTA_ID} a:first-child {
    border-left: 0;
  }

  #${PSG_CTA_ID} a[data-primary] {
    background: var(--psg-brand);
    color: #fff;
  }

  #${PSG_CTA_ID} a:hover,
  #${PSG_CTA_ID} a:focus {
    text-decoration: underline;
  }

  body {
    padding-bottom: calc(60px + var(--psg-safe-bottom)) !important;
  }

  @media (min-width: 769px) {
    #${PSG_CTA_ID} {
      display: none;
    }

    body {
      padding-bottom: 0 !important;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    html {
      scroll-behavior: auto !important;
    }
  }
`;

$w.onReady(() => {
  installHotfix();
});

function installHotfix() {
  if (!canUseDom()) {
    console.warn(
      "PSG hotfix: DOM access is unavailable in this Wix environment. " +
        "Install the CSS/HTML through Wix Settings -> Custom Code -> Body End."
    );
    return;
  }

  injectCss();
  injectMobileCta();
}

function canUseDom() {
  return (
    typeof document !== "undefined" &&
    document.head &&
    document.body &&
    typeof document.createElement === "function"
  );
}

function injectCss() {
  if (document.getElementById(PSG_HOTFIX_STYLE_ID)) {
    return;
  }

  const style = document.createElement("style");
  style.id = PSG_HOTFIX_STYLE_ID;
  style.type = "text/css";
  style.appendChild(document.createTextNode(HOTFIX_CSS));
  document.head.appendChild(style);
}

function injectMobileCta() {
  if (document.getElementById(PSG_CTA_ID)) {
    return;
  }

  const cta = document.createElement("nav");
  cta.id = PSG_CTA_ID;
  cta.setAttribute("aria-label", "Quick actions");
  cta.innerHTML = `
    <a href="tel:${PHONE_NUMBER}" aria-label="Call Philly Steak and Gyros at ${DISPLAY_PHONE}">
      Call
    </a>
    <a href="${DIRECTIONS_URL}" aria-label="Get directions to ${ADDRESS}" rel="noopener">
      Directions
    </a>
    <a data-primary href="#order" aria-label="Order online">
      Order
    </a>
  `;

  const orderLink = cta.querySelector("[data-primary]");
  orderLink.addEventListener("click", scrollToOrdering);

  document.body.appendChild(cta);
}

function scrollToOrdering(event) {
  const orderTarget = document.querySelector(
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

function prefersReducedMotion() {
  return (
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}
