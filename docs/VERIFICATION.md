# Verification and remaining work

## Completed on the latest published version

- Strict MJML 4.18.0 compilation completed with no reported errors or warnings.
- All **8** `test_calendar` tests passed.
- The approved schedule is shared by newsletter labels, generated calendar pages, their UTC data attributes, and all Google/Outlook/Microsoft 365 provider parameters.
- October modules remain at 16:00–17:00 UTC; November/December modules changed to 17:00–18:00 UTC; the two LinkedIn Lives changed to 18:00–19:00 UTC.
- An exact before/after comparison of generated MJML and compiled HTML found only the five approved newsletter schedule-line changes. All other email copy, styles, images and 12 links were identical.
- The latest saved Loops draft was reloaded and inspected. All updated schedule lines persisted, the 12 destinations were unchanged and all 14 images loaded at their expected source dimensions.
- Site version 16 deployment returned success. Its source commit is recorded in the README.
- No email campaign or preview email was sent.

## Handoff checks

See [`HANDOFF_VERIFICATION.json`](../HANDOFF_VERIFICATION.json) for the results of rebuilding this repository, comparing the generated email/website against the published-source artifacts, validating the 14-image Loops ZIP and scanning selected public files for credential patterns. Public content includes the real session links because the owner explicitly requested them.

## What the automated tests cover

| Check | Coverage |
|---|---|
| Calendar conversion | Date-specific IANA time zones and daylight saving transitions |
| Configured modules | All seven modules stay at noon ET, including November/December |
| LinkedIn Lives | Both start at 1 PM ET, one hour after modules, and 18:00 UTC |
| Provider destinations | Google, personal Outlook and Microsoft 365 UTC ranges and real locations |
| Rendered pages | Full Mexico City/ET/UTC ranges, correct UTC data attributes and escaped URLs |
| Draft safety | Disabled unconfirmed provider links and no downloadable .ics action |
| ICS helper | Separate test UID, UTF-8 folding and text escaping; helper is not a live download |

## Outstanding items for the developer/owner

1. Supply registration URLs and speakers for Proof of Adoption and The Capital Table. Until then, keep the two “Registration coming soon” text labels and omit registration buttons.
2. Resolve or confirm the Loops Guardian “(No text)” missing-link warning described in [Email and Loops](EMAIL_AND_LOOPS.md). The validator finding remains open; it is not proof of a missing rendered CTA destination.
3. Test actual provider-account save flows on intended devices. Generated-link validation is not proof that a signed-in account saved the event.
4. Test manual Proton/Apple entry on recipient devices and confirm the real Ro.am room is accessible with the intended attendee permissions. No Ro.am room access or attendance test is claimed here.
5. Review the uploaded email at 390px and in the intended mail clients' dark modes. Responsive CSS and color locks are present, but cross-client inbox rendering is not guaranteed by browser preview or MJML validation.
6. The owner manages the Loops audience, sender verification, unsubscribe behavior and final send after testing. Do not send or schedule the campaign as part of a build or upload.

## Timing decisions

The final approval supersedes earlier fixed-CST and LinkedIn-earlier requests. The owner reviewed a before/after table and confirmed Kara approved it:

- All modules: **12:00–1:00 PM ET**.
- Both LinkedIn Lives: **1:00–2:00 PM ET**.
- October module UTC: **4:00–5:00 PM**.
- November/December module UTC: **5:00–6:00 PM**.
- LinkedIn Live UTC: **6:00–7:00 PM**.

Eastern daylight saving ends November 1, 2026. The schedule is anchored to `America/New_York`, not a fixed offset.
