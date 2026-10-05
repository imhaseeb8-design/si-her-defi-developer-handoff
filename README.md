# Si Her DeFi — Season 1 developer handoff

Latest website and newsletter handoff, prepared **October 5, 2026** from the published Site source commit `9916f990a039401fd2a12d8bcd5f28cc979f9d6c` (Site version 16).

- **Live calendar page:** https://si-her-defi-calendar.imhaseeb8.chatgpt.site/
- **Live newsletter preview:** https://si-her-defi-calendar.imhaseeb8.chatgpt.site/newsletter/
- **Latest newsletter MJML:** [email/newsletter.mjml](email/newsletter.mjml)
- **Latest compiled HTML:** [email/newsletter.html](email/newsletter.html)
- **Ready-to-upload Loops ZIP:** [email/loops-upload.zip](email/loops-upload.zip)

The repository includes the seven real Ro.am session destinations, original source, supplied artwork, compiled website, full guest flow and the approved date-specific ET/UTC schedule. The root live page shows **Token Fundamentals**; each other module has its own calendar URL.

## Developer reading order

| Document | What it explains |
|---|---|
| [Developer handoff](docs/DEVELOPER_HANDOFF.md) | Architecture, source files, dependencies, deployment and editing rules |
| [Guest flow](docs/GUEST_FLOW.md) | Newsletter → session page → join, copy, calendar providers or manual calendar entry |
| [Session reference](docs/SESSION_REFERENCE.md) | Every session, speaker, full time range, calendar page and real destination |
| [Email and Loops](docs/EMAIL_AND_LOOPS.md) | Responsive design, dark mode, upload package, personalization and Guardian warning |
| [Verification and pending work](docs/VERIFICATION.md) | Completed checks, remaining device testing and missing registration links |
| [Asset inventory](docs/ASSETS.md) | Current image files, dimensions, usage and retained older images |
| [Original live-source README](docs/LIVE_SOURCE_README.md) | Unmodified README from the hosted source checkout |

## Approved schedule

**All modules:** 12:00–1:00 PM ET. **Both LinkedIn Lives:** 1:00–2:00 PM ET, one hour later than modules. `sessions.json` is anchored to `America/New_York`; UTC changes when Eastern daylight saving ends November 1, 2026.

| Events | ET | UTC |
|---|---|---|
| October modules | 12:00–1:00 PM | 4:00–5:00 PM |
| November/December modules | 12:00–1:00 PM | 5:00–6:00 PM |
| Nov 4 and Dec 2 LinkedIn Lives | 1:00–2:00 PM | 6:00–7:00 PM |

Earlier requests for fixed CST or LinkedIn Lives one hour earlier were superseded by this approved schedule. National Web3 Women’s Day has no confirmed hourly range in this package.

## Run locally

Requirements: Python 3.9+ with IANA time zone data, Node.js 18+ and npm. MJML is pinned to the version used for the latest email, **4.18.0**.

```sh
npm ci
npm test
npm run build
npm run preview
```

Open http://localhost:8000/ for Token Fundamentals and http://localhost:8000/newsletter/ for the email preview. Preview serves the complete `dist/` directory, so `/assets/` resolves correctly. Calendar-provider buttons prefill real session events; review before saving.

The default build preserves the exact URLs used in the uploaded Loops draft. To move to another HTTPS host:

```sh
python3 tools/rebuild.py --base-url https://your-domain.example
```

This changes both newsletter calendar links and hosted email asset URLs. Publish the new site before uploading or sending the rebuilt email.

## Project layout and source of truth

```text
sessions.json               Approved session dates, ET times, speakers and destinations
build.py                    Calendar page and provider-link generator
page.html                   Calendar page layout, local-time display and Copy behavior
newsletter.py               EMAIL SOURCE OF TRUTH; writes newsletter.mjml
package_site.py             Compiles the static routes into a Cloudflare-compatible Worker
cta-links.json              Generated newsletter destinations
email-ctas.mjml             Generated CTA snippets
assets/                     Supplied logos, speaker artwork and social icons
email/newsletter.mjml       Latest generated MJML snapshot
email/newsletter.html       Latest compiled/minified HTML snapshot
email/loops-upload.zip      MJML + 14 images with relative paths, ready for Loops
email/asset-manifest.json   Referenced email assets and SHA-256 checksums
dist/                      Generated website, email preview, assets and Worker
tools/                     Rebuild and ZIP packaging utilities
test_calendar.py           Eight calendar/time-zone/provider-link tests
docs/                      Complete handoff and verification notes
 legacy/invitation.py       Archived unused invitation prototype; not a live feature
```

`tools/rebuild.py` orchestrates the original generators, strict MJML compilation, website packaging and fresh email snapshots. Root `newsletter.mjml` / `newsletter.html` are intermediate outputs ignored by Git. **Edit `newsletter.py`, `sessions.json`, `page.html` or other source files, then rebuild. Do not hand-edit `email/`, `dist/` or the ZIP.**

## Current delivery state

The site is published. The latest email was reuploaded to Loops and verified as **Draft**; no campaign or preview email was sent. The public site does not collect email addresses, send invitations, require Mailgun or offer .ics downloads. Proton and Apple users create an event manually using the page details.

Proof of Adoption and The Capital Table still have **“Speakers to be announced”** and **“Registration coming soon”**, with no registration buttons. Their destination URLs are not supplied.

This public repository intentionally contains the real Ro.am URLs as requested. It contains no recipient list, API keys, browser session data, credentials, account tokens or source-repository history. Brand artwork is supplied project material; no additional redistribution license has been assigned.
