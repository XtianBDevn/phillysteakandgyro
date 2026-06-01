# Live CSS/HTML Update Walkthrough

Purpose: compare the local working copy with production and document the steps needed to update CSS and HTML on the live site.

## Source checked

- Requested local path: `~/Sites/philly-steak-and-gyro`
- Cloud-agent path available here: `local-site/`
- Production URL: `https://www.phillysteakgyros.com/`
- Production menu URL: `https://www.phillysteakgyros.com/menu-1`
- Date checked: 2026-06-01

The `~/Sites/philly-steak-and-gyro` directory was not mounted in this cloud environment. This comparison uses the repository's `local-site/` directory, which matches the docs' stated local working copy.

## Comparison summary

| Area | Production | Local working copy |
|---|---|---|
| Platform | Wix Thunderbolt, served by `Pepyaka` | Static HTML/CSS/JS under `local-site/` |
| Homepage file | Wix-generated HTML at `/` | `local-site/index.html` |
| Menu file | Wix-generated menu app at `/menu-1` | `local-site/menu.html` |
| CSS ownership | Wix runtime CSS plus generated component styles | `local-site/css/site.css` |
| JS ownership | Wix runtime bundles | `local-site/js/site.js` only |
| Homepage title | `Home \| PhillySteak&Gyros` | Local-intent SEO title for Carytown/Richmond |
| Meta description | Missing | Present |
| Viewport | `width=device-width, initial-scale=1` | `width=device-width, initial-scale=1, viewport-fit=cover` |
| Semantic H1 | Homepage H1 resolves to the phone number | Homepage H1 targets "Cheesesteaks & Gyros in Carytown, Richmond" |
| Structured data | Not present in production source | Restaurant JSON-LD and Menu JSON-LD in local files |
| Mobile CTA | Not native on production | Sticky Call / Directions / Order CTA in local files |

Key takeaway: production is not serving the local `index.html`, `menu.html`, or `css/site.css` files. Live changes must either be applied through Wix, or the domain must be moved to a host that serves the local files.

## Choose the update path

Use one of these two paths before making live changes.

### Path A: update the current Wix site

Use this when the business wants to keep Wix live.

This path can ship targeted CSS and HTML snippets, SEO metadata, JSON-LD, and content changes. It cannot replace the full Wix-generated page source with `local-site/index.html`.

### Path B: replace Wix with the local static rebuild

Use this when the business is ready to make `local-site/` the live website.

This path makes `index.html`, `menu.html`, `css/site.css`, `js/site.js`, and `assets/` the production files. It requires a static host, WordPress/theme migration, or another web server plus a DNS cutover.

---

## Path A: update CSS/HTML live in Wix

### 1. Back up current production

1. Log in to Wix.
2. Open **Site History** and confirm there is a restore point before editing.
3. Save a local production mirror if needed:

   ```sh
   python3 mirror.py
   ```

4. Keep `local-site/pages/home.original.html` and `local-site/pages/menu.original.html` as reference snapshots.

### 2. Preview the local target

From the repo root:

```sh
npm run local-site
```

Then open `http://127.0.0.1:3333/`.

Check:

- `local-site/index.html`
- `local-site/menu.html`
- `local-site/css/site.css`
- `local-site/js/site.js`

### 3. Move SEO HTML into Wix fields

Do not paste the full `<head>` from `local-site/index.html` into Wix. Use Wix's page settings instead.

Homepage:

1. Go to **Wix Dashboard -> Marketing & SEO -> SEO -> Main Pages -> Homepage**.
2. Set the page title from `local-site/index.html`.
3. Set the meta description from `local-site/index.html`.
4. Set the canonical URL to `https://www.phillysteakgyros.com/`.
5. Add or update the visible homepage heading in the Wix editor so the page has one real restaurant/location-focused H1.

Menu page:

1. Go to the menu page SEO settings.
2. Set the title and meta description from `local-site/menu.html`.
3. Keep the current live URL if staying on Wix (`/menu-1`) unless redirects are configured.

### 4. Add JSON-LD through Wix Custom Code

Restaurant schema:

1. In Wix, go to **Settings -> Custom Code -> Add Custom Code**.
2. Paste the `<script type="application/ld+json">...</script>` block from `local-site/index.html`.
3. Place it in **Head**.
4. Apply it to **Homepage only** unless the code is intentionally global.

Menu schema:

1. Add a second Custom Code entry.
2. Paste the Menu JSON-LD block from `local-site/menu.html`.
3. Place it in **Head**.
4. Apply it to the menu page only.

Validate both with Google's Rich Results Test after publishing.

### 5. Add CSS safely in Wix

Wix-generated class names and component IDs can change after editor saves. Prefer Custom Code snippets that are scoped to stable custom IDs or injected elements.

Recommended process:

1. Open **Settings -> Custom Code -> Add Custom Code**.
2. Add a `<style>...</style>` block.
3. Place it in **Head** for styles that should apply before paint, or **Body End** for a snippet that also injects HTML.
4. Scope rules tightly:
   - Good: `#psg-cta-bar`, `.psg-custom-*`, `[data-testid="richTextElement"]` only when necessary.
   - Risky: Wix hashed classes such as `.comp-kb66xuoj`, `.YzqVVZ`, `.MMl86N`.
5. Start from `docs/03-wix-mobile-hotfix.md` for the current mobile CTA and layout fixes.
6. Preview desktop and mobile before publishing.

Use `!important` sparingly. It is often necessary when overriding Wix inline styles, but every `!important` should be scoped to the smallest selector possible.

### 6. Add HTML safely in Wix

For small HTML additions:

1. Use **Settings -> Custom Code -> Body End** for snippets that inject elements such as a sticky CTA.
2. Use the Wix editor for visible page content, buttons, and images when possible.
3. Use **Embed HTML** only for self-contained widgets that do not need to control the whole page.

Do not paste the full `local-site/index.html` body into a Wix HTML embed. It will create a page inside an iframe-like widget instead of replacing the Wix page.

### 7. Publish and verify

Before publishing:

- Use Wix Preview for desktop and mobile.
- Check that the menu page still loads menu items.
- Confirm delivery links open in a new tab.
- Confirm phone links use `tel:+18045621174`.

After publishing:

1. Open `https://www.phillysteakgyros.com/` in a private browser window.
2. Open `https://www.phillysteakgyros.com/menu-1`.
3. Use browser devtools to verify the new `<style>` or JSON-LD exists on the live page.
4. Run Rich Results Test for the homepage and menu page.
5. Test mobile layout on iPhone Safari or BrowserStack.

Rollback:

1. Disable the Custom Code entry that introduced the issue, or restore the previous Wix Site History version.
2. Republish.
3. Clear browser cache and retest.

---

## Path B: make the local files live

### 1. Prepare the local static files

Production file mapping:

| Local file/folder | Live destination |
|---|---|
| `local-site/index.html` | `/index.html` and `/` |
| `local-site/menu.html` | `/menu.html` or `/menu/` |
| `local-site/css/site.css` | `/css/site.css` |
| `local-site/js/site.js` | `/js/site.js` |
| `local-site/assets/` | `/assets/` |

Before upload:

1. Decide whether the menu URL should be `/menu`, `/menu.html`, or the current Wix URL `/menu-1`.
2. Update canonical URLs in `index.html` and `menu.html` to match the chosen live URLs.
3. If preserving `/menu-1`, configure a redirect to the new menu URL or serve the menu file at `/menu-1`.
4. Confirm all links are relative or use the final production domain.

### 2. Test the static site locally

From the repo root:

```sh
npm run local-site
```

Open:

- `http://127.0.0.1:3333/`
- `http://127.0.0.1:3333/menu.html`

Check the browser console for 404s or JavaScript errors.

### 3. Deploy to a staging host

Any static host works if it can serve plain HTML/CSS/JS and configure redirects. Examples: Netlify, Vercel, Cloudflare Pages, S3/CloudFront, or a traditional cPanel/SFTP host.

Minimum staging requirements:

- HTTPS enabled.
- `index.html` served at `/`.
- `css/`, `js/`, and `assets/` served with correct MIME types.
- A redirect from `/menu-1` to the chosen menu URL.
- A custom 404 page or redirect behavior that does not hide missing assets.

### 4. Upload files

For a traditional file host:

1. Back up the current web root.
2. Upload the contents of `local-site/` to the host's public web root.
3. Preserve the folder structure.
4. Ensure files are readable by the web server.
5. Clear server/CDN cache.

For a Git-connected static host:

1. Set the publish directory to `local-site`.
2. Leave the build command empty unless the host requires a no-op command.
3. Add redirect rules for legacy Wix URLs, especially `/menu-1`.
4. Deploy to a preview URL first.

### 5. Cut over the domain

1. Lower DNS TTL ahead of the cutover if the DNS provider allows it.
2. Point `www.phillysteakgyros.com` to the new host using the host's required CNAME or A records.
3. Ensure the apex/root domain redirects to `www` or is also configured on the new host.
4. Provision SSL for both `phillysteakgyros.com` and `www.phillysteakgyros.com`.
5. Keep the Wix site unchanged until the new host is verified.

### 6. Post-cutover verification

Run these checks from a clean browser and a terminal:

```sh
curl -I https://www.phillysteakgyros.com/
curl -I https://www.phillysteakgyros.com/css/site.css
curl -I https://www.phillysteakgyros.com/menu.html
```

Expected:

- Homepage returns `200`.
- CSS returns `200` with `text/css`.
- Menu URL returns `200` or redirects intentionally.
- Old `/menu-1` URL redirects to the new menu page if the URL changed.

Manual QA:

- Homepage hero, delivery links, hours, address, and phone.
- Menu item cards and order links.
- Sticky mobile CTA on iPhone Safari and Android Chrome.
- Rich Results Test for Restaurant and Menu structured data.
- Lighthouse mobile pass for no horizontal scroll and usable tap targets.

Rollback:

1. Restore the previous DNS records to Wix, or repoint the domain to the prior host.
2. Clear CDN cache.
3. Verify Wix production is back online before making another cutover attempt.

---

## Practical recommendation

For a fast live update, use **Path A** and ship the Wix custom-code/mobile hotfix plus SEO fields and JSON-LD. For full control over `index.html`, `menu.html`, and `css/site.css`, use **Path B** and deploy the static rebuild to a real host before moving DNS.

Do not expect edits to `local-site/css/site.css` or `local-site/index.html` to affect production until Path B is complete.
