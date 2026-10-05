# Developer handoff

## Current production reference

Prepared October 5, 2026. The latest published Site is version 16, sourced from commit `9916f990a039401fd2a12d8bcd5f28cc979f9d6c`. This handoff preserves its calendar pages, email content, artwork and session destinations. The added build wrapper and documentation organize the files for an independent developer.

Production origin: `https://si-her-defi-calendar.imhaseeb8.chatgpt.site`.

The current newsletter's seven session-page buttons and original email asset paths use `https://si-her-defi-calendar-test.imhaseeb8.chatgpt.site`. That earlier origin redirects to the production Site. Preserve these URLs for the existing draft; use `tools/rebuild.py --base-url` when intentionally migrating both assets and CTA URLs.

## Architecture

The production site is static. Python generators produce HTML and provider URLs; no server-side session database, email sender, SMTP account, mailing list or Mailgun integration is involved.

1. `sessions.json` defines the approved schedule and destinations.
2. `build.py` reads the config, creates seven calendar pages, copies assets, writes `cta-links.json` and `email-ctas.mjml`, and places the Token Fundamentals page at `/`.
3. `newsletter.py` reads the same config and CTA map, builds all email content and writes `newsletter.mjml`.
4. MJML 4.18.0 compiles with strict validation to `newsletter.html`.
5. `package_site.py` minifies the compiled HTML as part of packaging, copies it to `dist/newsletter/index.html` and generates `dist/server/index.js`.
6. The handoff wrapper copies the generated email to `email/` and packages the Loops ZIP.

Generated `dist/server/index.js` embeds every static route and binary asset as base64. Its default export exposes `fetch(request)`, accepts GET/HEAD, resolves directory index pages, redirects slashless directory routes with HTTP 308, returns 404 for unknown routes and 405 for other methods, and supplies appropriate HTML/PNG content types with `X-Content-Type-Options: nosniff`. Its .ics MIME branch is retained helper code; the production build has no .ics files or download action.

## Data and time conversion

`sessions.json` uses `timezone: America/New_York`, `timezone_label: Eastern time`, and 24-hour `start`/`end` strings. All modules are `12:00`–`13:00`; LinkedIn Lives are `13:00`–`14:00`. Women's Day uses null start/end values because its hourly schedule is not supplied.

`build.utc_times()` converts each event's date/time using Python `zoneinfo`, then all providers and visible labels derive from that event instant. Never substitute a constant UTC offset for Eastern time. The October and November conversion difference is intentional.

`action: calendar` means a hosted session page can be generated. `action: register` means a direct registration destination when supplied. `confirmed: true` confirms the session information; it does not create a registration destination when `url` is null. The generator omits those two unprovided registration CTAs.

The Google URL carries title, UTC date range, speaker/session details, the real Ro.am location and `stz`/`etz`. Outlook personal and Microsoft 365 URLs carry title, start/end in UTC, body, location and `allday=false`. The user reviews and saves in their provider; the site does not save a calendar entry on their behalf.

## Website page behavior

- Full session title, speaker, date including 2026, and full Mexico City / ET / UTC hour ranges.
- Black rendered high-resolution Si Her DeFi logo (`site-logo.png`, CSS brightness filter).
- Real Ro.am link remains visible, wraps long URLs at a readable line height and opens in a separate tab.
- Copy uses `navigator.clipboard.writeText`. Success changes the label to “Copied” for two seconds. Failure changes the label to “Select link” and focuses the link. Clipboard support/permissions depend on the recipient's browser and HTTPS.
- Local time uses the UTC timestamps in `data-start`/`data-end` and `Intl.DateTimeFormat` with the browser's own time-zone settings. It shows the date, time and zone, plus **“Based on your local time zone settings.”**
- Local time is a convenience based on browser/OS settings, not a location lookup. If the device's zone is wrong, the local label can be wrong; the explicit ET/UTC ranges remain authoritative. If JavaScript or formatting fails, the local label remains hidden and the main schedule stays visible.
- Proton/Apple instructions describe manual event creation. No email form, invite delivery, automatic Proton event link or calendar download exists in production.
- Mobile page sizing uses `min(100%,440px)`, wrapping links and a 420px media query. Semantic headings, labeled images, focus outlines and reduced-motion support remain intact.

## Editing and rebuild rules

For schedule/destination edits, modify `sessions.json`. For email copy or styles, modify `newsletter.py`. For website markup, CSS or browser behavior, modify `page.html`. Artwork changes belong in `assets/`, with the email generator updated to the chosen filename. Keep session order aligned with the artwork/role list in `newsletter.py` when adding sessions.

After every change:

```sh
npm test
npm run build
```

The wrapper runs `build.py`, `newsletter.py`, strict MJML compilation and `package_site.py` in that order. Build scripts stop on failures. Rebuilding on another host needs IANA time-zone data; Linux normally supplies it, and minimal Python images may require the operating-system tzdata package or Python tzdata package.

## Deployment and local preview

To host static pages, deploy `dist/` with `/` and `/calendar/<id>/` resolving to `index.html`. To use a Cloudflare-compatible Worker, deploy the generated `dist/server/index.js` as the ESM Worker entrypoint. Run at the origin root so absolute `/assets/` paths resolve.

The original platform-owned Sites credentials and `.openai/hosting.json` were not copied. This GitHub repository is a developer handoff, not a new connection to that hosted Site. Publishing this repository does not change the live website. The owner must grant the developer access to the existing hosting project separately or the developer can deploy a new HTTPS origin and rebuild with that origin.

Keep the existing live deployment serving the newsletter's URLs until any migration is complete. Update the email package and its corresponding pages together, then verify the saved Loops draft. Campaign recipients, Loops login and sender configuration are outside this repository.

## Historical utilities

`build.make_ics()` remains a tested utility, but is not exposed as a website download. `legacy/invitation.py` is an archived prototype that prepares an .eml message and does not send mail. Its test body contains superseded fixed-CST wording; do not reuse it as production email. It was deliberately separated from the active source and deployment.

`test-email-template.mjml` supports the generator's explicit `--test` mode; that mode substitutes test destinations and must not be used when rebuilding the production campaign. The handoff's normal build does not enable it.
