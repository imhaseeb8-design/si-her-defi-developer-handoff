# Si Her DeFi session pages

The newsletter links to seven session pages. Each page shows the confirmed date, full time ranges in Mexico City time, ET and UTC, speaker, and Kara's Ro.am session URL. Visitors can open a prefilled Google Calendar, Outlook personal, or Microsoft 365 event. They can also copy the session URL. Proton and Apple Calendar users are shown the details needed to create an event manually. The site offers no calendar-file download or email-invitation form.

The newsletter is sent separately through Loops as a campaign. Its MJML uses Loops `{firstName}` and `{unsubscribe_link}` tags. The site itself sends no email. `invitation.py` is a development utility only and is not connected to the public page.

## Current content

The seven Ro.am links came from Kara Howard's ClickUp message. National Web3 Women's Day links to the supplied public site. Proof of Adoption and The Capital Table are listed without registration buttons until their destinations are supplied.

All calendar modules run 12:00–1:00 PM ET, anchored to `America/New_York`. October sessions are 4:00–5:00 PM UTC (10:00–11:00 AM Mexico City time). November and December sessions are 5:00–6:00 PM UTC (11:00 AM–12:00 PM Mexico City time), because Eastern daylight saving ends November 1, 2026.

The two LinkedIn Live events, Proof of Adoption on November 4 and The Capital Table on December 2, run one hour later than the modules: 1:00–2:00 PM ET / 6:00–7:00 PM UTC / 12:00–1:00 PM Mexico City time. Their speakers and registration links are pending. This schedule was confirmed by the user and Kara on October 5, 2026.

## Build

```sh
python3 build.py --base-url https://si-her-defi-calendar-test.imhaseeb8.chatgpt.site
python3 newsletter.py
npm exec --yes --package=mjml -- mjml newsletter.mjml -o newsletter.html --config.validationLevel=strict
python3 package_site.py
python3 -m unittest test_calendar.py
```

`dist/` is the public output. It contains seven calendar pages, the newsletter preview, assets, and the Worker. It must be published before the Loops campaign is sent, because the campaign's buttons use its public URLs. Calendar-provider links prefill an event but visitors must review and save. A real provider-account save and Proton manual-entry test should be done on recipient devices.
