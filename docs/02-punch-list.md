# Punch-list — Fix-in-place on Wix

For applying the Day-One fixes without leaving Wix. Each item is independently shippable and can be done in the Wix editor + Custom Code panel (Settings → Custom Code) without dev hand-off.

Estimated total effort: **6–8 hours** of editor work, **2 hours** of design polish.

---
## 1. SEO meta — 30 min

In the Wix Editor:

1. **Site Menu → SEO Settings → Homepage**
    - Page title:
     `Best Cheesesteaks & Gyros in Carytown, Richmond VA | Philly Steak & Gyros`
    - Meta description:
     `Hand-grilled Philly cheesesteaks, gyros, falafel and wings in Carytown, Richmond VA. Open daily — dine in, pickup, or order delivery via DoorDash, Uber Eats, and Grubhub.`
2. Repeat per page (Menu, Contact, etc.) with page-specific titles.
3. Add a real `<h1>` element on each page via the editor; Wix's "Heading 1" widget. There should be exactly one per page.
4. Upload an Open Graph image (1200×630, < 200 KB).

## 2. Structured data (JSON-LD) — 20 min

Settings → **Custom Code → Add Custom Code → Head** → all pages.

Paste the `LocalBusiness` JSON-LD from `local-site/index.html`.

Paste the `Menu` JSON-LD from `local-site/menu.html` scoped to the menu page only.

Validate at https://search.google.com/test/rich-results.

## 3. Google Business Profile — 1 hr

- Claim/verify the listing.
- Categories: **Primary** = "Cheesesteak restaurant"; secondaries = "Greek restaurant", "Mediterranean
  restaurant", "Wings restaurant".
- Upload 20+ photos (food close-ups, storefront, interior).
- Set Q&A seeds (parking? vegetarian options? group ordering?).
- Enable messaging.
- Set up weekly Google Posts (specials, events).
- Wire reviews to flow to owner's phone via GBP app notifications.

## 4. Instagram — 30 min editor + ongoing

- Confirm handle (`@phillysteakgyros` placeholder — verify).
- Add a link + icon to the global header + footer in the Wix Editor.
- Drop the Wix "Instagram Feed" widget on the homepage, point at the account, set 6 tiles.

## 5. Per-item "Order Now" — 2 hr

- In the Wix Menu app, each item has a "More Info" button. Replace with a custom external link button labeled
  **"Order"** that opens the delivery app modal.
- Build a 3-tab modal (DoorDash / Uber Eats / Grubhub) via Wix's Lightbox feature.
- Pre-populate the modal links with `?search=<itemname>` for each item where the platform supports it.
- Cleaner version (recommended Tier-2 upgrade): add Toast or ChowNow direct ordering and skip third-party for in-house customers.

## 6. Alt text — 1 hr

In every image manager: write descriptive alt text. **Format:** `<item name> with <visible toppings>`.

Examples:
- `Philly steak sub with grilled onions, lettuce, tomato, and provolone cheese on a hoagie`
- `Lamb gyro platter with rice, salad, pita, and tzatziki sauce`
- ❌ Never: `IMG_3429.jpg`, `food`, `image`, `picture of food`

## 7. Mobile CTA trio — 1.5 hr

In Settings → **Custom Code → Body End → Mobile only**, paste the snippet from `docs/03-wix-mobile-hotfix.md` (separate file, ready to copy).

The snippet injects a fixed bottom bar with three tap targets: **Call · Directions · Order**. Safe to ship without touching the Wix layout.

---

## Acceptance criteria

- [ ] `LocalBusiness` JSON-LD validates clean in Rich Results Test.
- [ ] Homepage has exactly one `<h1>` containing "Carytown" or "Richmond".
- [ ] Every food image has non-empty descriptive `alt` text.
- [ ] On iPhone 11 Safari, the bottom CTA bar appears and stays sticky during scroll.
- [ ] Each menu item has at least one delivery-app deep-link.
- [ ] Google Business Profile is claimed and has ≥ 20 photos.
- [ ] At least one Open Graph share preview renders a real image when the homepage URL is pasted into iMessage.
