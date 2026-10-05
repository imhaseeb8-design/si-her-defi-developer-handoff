# Newsletter and Loops

## Latest files and source of truth

- [`../newsletter.py`](../newsletter.py): authoritative generator for copy, styles, structure, artwork mapping and button presentation.
- [`../sessions.json`](../sessions.json): authoritative event dates, local ET times and destinations.
- [`../email/newsletter.mjml`](../email/newsletter.mjml): latest generated email, unchanged from the uploaded draft's content and style.
- [`../email/newsletter.html`](../email/newsletter.html): latest compiled/minified HTML.
- [`../email/loops-upload.zip`](../email/loops-upload.zip): `index.mjml` plus 14 referenced images under `assets/`; ready for Loops.

The MJML snapshot references hosted assets, while the ZIP changes only those asset URLs to relative `assets/...` paths so Loops can ingest the images. All 12 newsletter links stay intact, including the unsubscribe template variable.

## Design to preserve

- 640px email body and Arial/Helvetica typography.
- Purple header/footer and primary CTA: `#642d9a`, with white text and header logo whose PNG background matches that purple.
- Fluid kickoff CTA (`width="100%"`) with mobile inline-width override. Preserve it; do not restore the old fixed 520px button width.
- Upcoming session cards: `#f8f6ff` fill, 6px radius, 1px `#e6d9ef` border and 24px gaps.
- Upcoming artwork retains its natural aspect ratio; the latest supplied taller images replace the earlier artwork. Kara's image is `tradfi-tall.png`, sourced from the corrected image with the SI<3> logo fully visible.
- Compact shared upcoming-card style, including Kara's **Co-Founder, Ecosystem Lead · SI<3>** role, and **Tokenomics Consultant · FinDaS** for Diana.
- Smaller lavender buttons: `#f2e8fa`, width 142px.
- Dark-mode metadata, `prefers-color-scheme: dark` CSS and mirrored `[data-ogsc]` selectors. Purple backgrounds/text and lavender-button contrast are explicitly locked. Actual clients differ in support and require recipient-device testing.
- Local-time conversion is a website feature. The newsletter itself has explicit ET and UTC time ranges; it does not dynamically detect recipient time zones.

## Personalization and links

Loops tags: `{firstName}` and `{unsubscribe_link}`. The existing draft's first-name fallback was “there”. Preserve the tags during upload.

The footer LinkedIn URL is **https://www.linkedin.com/company/si3-ecosystem/**. X is `https://x.com/si3_ecosystem`; website is `https://www.si3.space/`.

No registration button is included for either LinkedIn Live while the destination is unprovided. Women's Day uses the supplied public registration website. See [Session reference](SESSION_REFERENCE.md) for all calendar CTAs and Ro.am links.

## Upload procedure

1. Run `npm run build` after source changes.
2. In the existing Loops campaign's Compose step, choose **Upload another email**.
3. Select `email/loops-upload.zip` and choose **Upload file**.
4. Review the rendered preview, event times, all images, personalized tags and links.
5. Reload the draft to check that the upload persisted.
6. Leave the campaign in **Draft**. The owner chooses the audience and send time separately.

No Loops API key is needed to build the package. This repository does not contain Loops credentials, recipient contacts or an audience export. No automated script sends a campaign or a preview email.

## Guardian warning observed in Loops

The current draft displayed one Guardian **“Missing button link”** finding. Expanding it showed **“Buttons won't work without href value”** and **“(No text)”**. All 12 rendered anchors had destinations, and no rendered unlinked cursor-pointer button was found.

The MJML contains one **style-default** `<mj-button>` inside `<mj-attributes>` with no `href` or text; every actual `<mj-button>` in `<mj-body>` has a real `href`. This suggests Guardian is scanning the default declaration as though it were an actionable button. It is a hypothesis, not a verified explanation of Loops' internal validator. The warning was not cleared or dismissed before this handoff.

Developer follow-up: distinguish the attribute-default declaration from rendered body buttons, inspect the finding in Loops, and if needed move default button styling into a named MJML class or explicit attributes. Regenerate with strict MJML, confirm visual/content parity, reupload and verify whether Guardian clears. Do not insert a dummy URL into defaults or change real destinations just to suppress a warning.
