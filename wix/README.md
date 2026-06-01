# Wix Velo Files

This folder contains code intended to be copied into the Wix platform.

## `masterPage.js`

Use `masterPage.js` for the current Wix live site when you want a site-wide runtime hotfix instead of deploying the static `local-site/` files.

Install steps:

1. Open the Wix editor.
2. Enable **Dev Mode / Velo**.
3. Open the site-wide **masterPage.js** file.
4. Paste the contents of `wix/masterPage.js`.
5. Preview desktop and mobile.
6. Publish after confirming the CTA and mobile CSS fixes behave correctly.

What it does:

- Injects scoped CSS for the mobile viewport, tap targets, horizontal-scroll prevention, and iOS safe-area padding.
- Adds a mobile sticky **Call / Directions / Order** CTA.
- Keeps selectors scoped to stable tags/attributes and the custom `#psg-cta-bar` ID.

Important limitation:

Some Wix/Velo environments restrict direct `document` access in frontend page code. If the browser console logs the warning from `masterPage.js`, install the same CSS/HTML through **Wix Settings -> Custom Code -> Body End -> All pages -> Mobile only** using `docs/03-wix-mobile-hotfix.md`.
