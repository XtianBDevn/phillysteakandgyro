# Wix Platform Files

This folder contains code intended to be copied into the Wix platform.

## `custom-code-body-end.html`

Use `custom-code-body-end.html` for the Wix admin area.

Install steps:

1. Open the Wix dashboard.
2. Go to **Settings -> Custom Code -> Add Custom Code**.
3. Paste the full contents of `wix/custom-code-body-end.html`.
4. Set **Add Code to Pages** to **All pages**.
5. Set **Place Code in** to **Body - end**.
6. Enable **Load code on each new page** if Wix shows that option.
7. Choose **Mobile only** if Wix shows a device option; otherwise leave it on all devices.
8. Preview desktop and mobile, then Publish.

## `masterPage.js`

Use `masterPage.js` for Wix Velo if you are editing the site-wide Velo `masterPage.js` file instead of the admin Custom Code area.

Install steps:

1. Open the Wix editor.
2. Enable **Dev Mode / Velo**.
3. Open the site-wide **masterPage.js** file.
4. Paste the contents of `wix/masterPage.js`.
5. Preview desktop and mobile.
6. Publish after confirming the CTA and mobile CSS fixes behave correctly.

What both hotfixes do:

- Inject scoped CSS for the mobile viewport, tap targets, horizontal-scroll prevention, and iOS safe-area padding.
- Add a mobile sticky **Call / Directions / Order** CTA.
- Keep selectors scoped to stable tags/attributes and the custom `#psg-cta-bar` ID.

Important limitation:

Some Wix/Velo environments restrict direct `document` access in frontend page code. If the browser console logs the warning from `masterPage.js`, use the admin Custom Code snippet in `wix/custom-code-body-end.html` instead.
