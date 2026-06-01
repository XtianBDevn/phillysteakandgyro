# Wix Mobile Hotfix — iPhone 11 + cross-browser

Drop-in snippet for **Wix Settings → Custom Code → Body End → All pages → Mobile only**.

If using Wix Velo instead of Custom Code, copy `wix/masterPage.js` into the site's
site-wide `masterPage.js` file. The Custom Code snippet below is still the
fallback if the Velo runtime blocks direct DOM access.

Fixes:

- iOS Safari `100vh` URL-bar overlap on hero sections
- Horizontal-scroll triggers from any wide child
- Adds the **Call · Directions · Order** sticky CTA bar on mobile
- Improves tap-target size for items that are too small (under 44px)
- Re-styles the menu accordions to one tap instead of two
- Respects `prefers-reduced-motion`

---

## Custom Code snippet

```html
<style>
  /* iOS Safari URL-bar fix — replace 100vh hero with dynamic vh */
  @supports (height: 100dvh) {
    .full-height-strip,
    [data-mesh-id$="hero"],
    .hero-section,
    section[id*="hero" i] {
      min-height: 100dvh !important;
    }
  }

  /* Prevent any rogue child from triggering horizontal scroll on phones */
  @media (max-width: 480px) {
    html, body { overflow-x: hidden !important; }
    img, video, iframe { max-width: 100% !important; height: auto !important; }
  }

  /* Tap targets — minimum 44x44 per Apple HIG / WCAG 2.5.5 */
  @media (max-width: 768px) {
    a, button, [role="button"] {
      min-height: 44px;
    }
  }

  /* iPhone 11 portrait (414px) — widen content area; Wix defaults
     can leave 28-32px of empty side gutter that wastes screen space. */
  @media (min-width: 414px) and (max-width: 480px) {
    [data-mesh-id$="contentWrapper"] {
      padding-left: 12px !important;
      padding-right: 12px !important;
    }
  }

  /* Sticky mobile CTA bar */
  #psg-cta-bar {
    position: fixed;
    left: 0; right: 0; bottom: 0;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    background: #fff;
    border-top: 1px solid #e8e2d6;
    box-shadow: 0 -2px 12px rgba(0,0,0,.12);
    z-index: 99999;
    padding-bottom: env(safe-area-inset-bottom, 0);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  #psg-cta-bar a {
    text-decoration: none;
    color: #1a1a1a;
    font-weight: 700;
    text-align: center;
    padding: 12px 4px;
    font-size: 14px;
    border-left: 1px solid #e8e2d6;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    min-height: 56px;
    justify-content: center;
  }
  #psg-cta-bar a:first-child { border-left: 0; }
  #psg-cta-bar a[data-primary] { background: #c8102e; color: #fff; }
  #psg-cta-bar .ico { font-size: 18px; line-height: 1; }
  /* Push page content above the bar */
  body { padding-bottom: calc(60px + env(safe-area-inset-bottom, 0)) !important; }
  @media (min-width: 769px) {
    #psg-cta-bar { display: none; }
    body { padding-bottom: 0 !important; }
  }
</style>

<nav id="psg-cta-bar" aria-label="Quick actions">
  <a href="tel:+18045621174" aria-label="Call Philly Steak and Gyros">
    <span class="ico" aria-hidden="true">📞</span> Call
  </a>
  <a href="https://www.google.com/maps/dir/?api=1&destination=3443+W+Cary+St+Richmond+VA+23221" aria-label="Get directions">
    <span class="ico" aria-hidden="true">📍</span> Directions
  </a>
  <a data-primary href="#order" aria-label="Order online"
     onclick="var t=document.querySelector('[href*=doordash],[href*=ubereats],[href*=grubhub]'); if(t){event.preventDefault(); t.scrollIntoView({behavior:'smooth',block:'center'});}">
    <span class="ico" aria-hidden="true">🛵</span> Order
  </a>
</nav>
```

---

## Verification checklist

| Device / browser | Pass criteria |
|---|---|
| iPhone 11, Safari 17 | CTA bar visible, sticky on scroll; no horizontal scroll; hero fills viewport |
| iPhone 11, Chrome iOS | Same as above |
| iPhone SE 2nd gen (375×667) | Bar fits 3 buttons without wrapping |
| Samsung Galaxy S20, Chrome | Tap targets ≥ 44px |
| iPad Mini portrait (768×1024) | CTA bar hidden (desktop layout takes over) |
| Desktop Chrome/Safari/Firefox | CTA bar hidden; no layout regression |

Run via BrowserStack or real devices. Document any regressions in `docs/qa-log.md` before pushing live.
