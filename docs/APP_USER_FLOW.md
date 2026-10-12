# Si Her DeFi app: user flow and state rules

Last reviewed: 12 October 2026. This describes the **app prototype** at `/siherdefi`, not the separate calendar and newsletter site. Routes below omit the `/siherdefi` base path. The prototype mirrors the live app's API shapes; wallet signing, minting, and CMS data are simulated. Rules marked **needs production work** must be implemented or confirmed in the real backend.

## End-to-end path

`Claim seat → verify email → create profile → connect wallet → dashboard → Part 1 → sessions and quizzes → Part 2 → certificate → mint on Base → dashboard with minted certificate`

Returning members resume at the first incomplete setup step. The separate `/verified` success screen is skipped after code verification. Signed-in routes require authentication; the certificate sidebar item is locked until all module quizzes are resolved. The dashboard is the home for ongoing work; completing a stage updates its cards rather than creating a new dashboard route.

| Stage | Route and main action | Completion rule | Next destination |
|---|---|---|---|
| Claim seat | `/` or `/login` → Send my code | Applicant email accepted by `POST /auth/claim-seat` | `/verify?email=…` |
| Verify | `/verify` → Verify email | Six digits accepted by `POST /auth/verify-otp` | `/profile`, `/wallet`, or `/dashboard` based on saved profile and wallet |
| Profile | `/profile` → Save & continue | Name is nonempty; profile saved | `/wallet` |
| Wallet | `/wallet` → connect and sign nonce | Base wallet address linked | `/dashboard` |
| Part 1 | `/onboard` → watch, follow, answer | 80% of intro actually played; required socials followed; required questions answered; submission succeeds | `/dashboard` |
| Module | `/module/[slug]` → watch/session, quiz | Quiz passed, or deliberately skipped after exhausting attempts | Next module or dashboard |
| Part 2 | `/onboard/part-2` → Finish Part 2 | Part 1 complete and every module quiz passed or skipped; required reflections answered | Done screen, then `/certificate?mint=1` |
| Certificate | `/certificate` → Mint on Base | All module quizzes resolved and wallet connected; mint succeeds | Minted certificate and dashboard |

## Rules by step, including failures

### Email and code

- Email is required and must be valid. Keep **Send my code** enabled so submitting empty or malformed input gives an inline field error; show loading while requesting a code. If the applicant email is not found, show the API error under the field and let the member edit it.
- The code page shows six numeric boxes. Verify is disabled until all six are filled. A wrong code highlights the boxes and shows an inline error; editing clears it. `000000` is the prototype's wrong-code case.
- Resend becomes available after the 40-second countdown. Resending clears the boxes and restarts the countdown. The UI says codes expire after 10 minutes; the mock server does **not** enforce expiration (**needs production work**).
- A missing email query sends the member back to `/login`. Returning members go to the first incomplete profile/wallet step, then dashboard.

### Profile and wallet

- Name is required because it is printed on the certificate. Missing name gets an inline error. Other text fields use `LabelInput`; optional fields say “(optional)”. Profile editing from `/profile?from=dashboard` or Settings returns to the signed-in experience.
- Wallet connection requires the provider connection and a nonce signature. The signature links the address; it is not a paid transaction. Show connecting, signing, connected, and error states. A rejected connection or rejected signature explains the failure and permits another attempt. Wrong network opens the switch-network prompt. Missing wallet keeps mint disabled.
- The connected address and Base status appear in the app shell/dashboard. Settings can disconnect the wallet; the current disconnect action is immediate, without confirmation (open improvement #3). The real app must reconcile an already minted certificate if a wallet is later disconnected.

### Part 1 onboarding

- The intro video's watched flag is reached after 80% **actually plays**; seeking forward does not count. Follow actions stay disabled until then. Required X and LinkedIn follows unlock the questions. The prototype marks a follow when its external link is clicked; it cannot verify the external follow (**needs production work**).
- Questions appear in CMS order. Required answers block Next/Submit when empty; optional answers may be blank. Closing the question dialog saves a draft; Resume opens the first unanswered question. Submission marks Part 1 done and unlocks module participation.
- Draft save failures are currently swallowed by the client, and the mock server accepts `videoWatched` from any draft save. Production should validate the watch threshold and show retryable save errors (**needs production work**).

### Sessions, events, and quizzes

- Dashboard session cards are sorted by date, including LinkedIn Lives. Show three initially; **Show more sessions** adds three at a time, and **Show fewer** returns to three. A future module offers Add to calendar; added modules show an Added state. A LinkedIn Live opens its external event link and has no quiz or badge. Its placeholder links/times need CMS updates.
- A module quiz opens after the live session, not while the session is upcoming. The mock API rejects early answers with a 409. The module page still has an open-state mismatch to resolve (improvement #12); production should disable Start quiz until the session opens.
- Each quiz requires all answers correct for its badge. An answer locks once selected; show correctness, explanation or a video chapter hint. Failed attempts show the score, review hints, and remaining attempts. After all attempts are used, offer **Start over** or **Skip this quiz**; skipping requires an explicit confirmation.
- A skipped quiz counts as **done for certificate unlock** but awards **no badge**. The member can return and take it again for the badge. A passed quiz earns one badge and updates dashboard progress. Network/answer errors should leave the attempt recoverable; the dialog displays the save error.

### Part 2, certificate, and mint

- Part 2 unlocks when Part 1 is done and **every module quiz is passed or skipped**. It loads a CMS-shaped list of any number of questions, with optional hints and optional answers, and no character limit. Missing required answers get an inline error and focus. Completion shows a celebratory done state with the earned certificate preview and a mint action.
- The certificate is **locked** until every quiz is resolved. Locked view is a preview with an unlock action; the sidebar item and dashboard certificate row remain locked. Once unlocked, its status is **earned** until minted. The artwork displays the member's name and **only earned badges**, sorted by module week. It centers occupied rows; skipped or failed quizzes leave no empty hexagons. Badge count must use the earned list, not the number of completed quizzes.
- Mint requires an unlocked certificate and connected wallet. The flow is Review → Confirm in wallet → Minting on Base → Minted. Review shows destination address, badge count, network, and gas coverage. Failure gives a retry and a way to leave. The prototype simulates signature and transaction; production must wait for the Base receipt before marking it minted (**needs production work**).
- Once minted, show token/transaction/network/verification details on `/certificate`. The certificate page provides LinkedIn, image download, verification-link, and BaseScan actions. The **dashboard** shows one minted certificate card directly below the greeting, with live certificate art, earned count, token ID, and Base. It has at most two actions: **View certificate** and **View on BaseScan**. The lower ready-to-mint banner is absent.

## Dashboard state matrix

| State | Header and top | Profile/badges | Learning path |
|---|---|---|---|
| New, Part 1 incomplete | Greeting says to introduce yourself; Base chip reflects wallet | Profile card; 0/N badge progress and next badge | **Begin your journey** leads with Start Part 1; featured module action is locked; certificate row locked |
| Part 1 complete, no badges | Greeting directs first session/quiz | Profile and empty badge guidance | Featured module and sessions; Part 1 Done/Part 2 Locked; certificate row locked |
| Some badges | Greeting reports earned count | Only earned badge images; segmented progress shows earned, next, and remaining | Sessions and next quiz; Part 2 locked; certificate row shows resolved quiz count |
| All quizzes resolved, Part 2 open | Greeting says certificate is ready | Earned badge count may be less than total because skips award none | Onboarding Part 2 Open now, ready-to-mint banner, then completed sessions |
| Part 2 done, unminted | Same certificate-ready state | Actual earned badges | Part 2 Done and Mint on Base CTA; no minted top card |
| Minted | Greeting says minted on Base; **certificate card directly below header** | Actual earned badges | Part 2 state, sessions; **no second certificate banner** |

The profile and badges cards always use current account data. The badge progress currently assumes 12 total cohort badges even though seven module fixtures exist; keep the total dynamic in production (open improvement #10). Certificate unlock is based on resolved **module quizzes**, not the badge count and not LinkedIn Live attendance. The ready-to-mint banner's “96 learners” social proof is a prototype placeholder (open improvement #8); do not treat it as live data.

## State and API contract

- Auth: `POST /auth/claim-seat`, `/auth/resend-otp`, `/auth/verify-otp`; `GET /auth/me`.
- Profile/wallet: `GET /profile`, `POST|PUT /profile`, `GET /wallet/status`, `POST /wallet/nonce`, `POST /wallet/connect`, `DELETE /wallet/disconnect`.
- Onboarding: `GET /onboard/status`, `/onboard/part1`, `/onboard/part2`; Part 1 draft and submit; Part 2 submit.
- Learning: `GET /modules`, `/events`, `/badges`, `GET /quiz/[slug]`, quiz answer/restart/skip, module calendar scheduling.
- Certificate: `GET /certificate`, `POST /certificate/mint`, `GET /certificate/verify/[code]`.

Preserve route paths, API names, and response shapes when moving changes to the real app. The source files for behavior are `src/lib/mock/server.ts`, `src/lib/types.ts`, `src/app/**/page.tsx`, and `src/components/**`. `docs/handoff/` contains screen-specific visuals and implementation notes. `docs/IMPROVEMENTS.md` tracks remaining known issues.
