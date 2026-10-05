"""Responsive MJML adaptation of Figma 1177:26; artwork exported from its visual layers."""
import json
from datetime import datetime
from pathlib import Path
from html import escape
from zoneinfo import ZoneInfo

from build import display_range, utc_times

ROOT = Path(__file__).resolve().parent
ORIGIN = 'https://si-her-defi-calendar-test.imhaseeb8.chatgpt.site'

# Explicit color locks keep the intended light design legible in dark-mode clients.
_THEME_RULES = [
    ('body, [aria-roledescription="email"], .outer, .card', 'background:#ffffff!important;background-color:#ffffff!important;color:#141332!important;'),
    ('.upcoming-card, .upcoming-card > table', 'background:#f8f6ff!important;background-color:#f8f6ff!important;'),
    ('.purple-band, .purple-band > table, .purple-band table[bgcolor="#642d9a"]', 'background:#642d9a!important;background-color:#642d9a!important;color:#ffffff!important;'),
    ('.primary-cta table, .primary-cta table td, .primary-cta a', 'background:#642d9a!important;background-color:#642d9a!important;'),
    ('.lavender-cta table, .lavender-cta table td, .lavender-cta a', 'background:#f2e8fa!important;background-color:#f2e8fa!important;color:#612d96!important;'),
    ('.social-cta table, .social-cta table td, .social-cta a', 'background:#f4eef8!important;background-color:#f4eef8!important;color:#000000!important;'),
]
_THEME_RULES += [
    (f'div[style*=";color:{color}"], a[style*=";color:{color}"]', f'color:{color}!important;')
    for color in ('#ffffff', '#e3d4ee', '#0f1030', '#141332', '#39205c', '#505050',
                  '#5a5a6e', '#612d96', '#642d9a', '#666666', '#696477', '#6b319a', '#000000')
]


def dark_mode_css():
    media = '\n'.join(f'{selector}{{{declarations}}}' for selector, declarations in _THEME_RULES)
    outlook = '\n'.join(
        f'{", ".join(f"[data-ogsc] {part}, {part}[data-ogsc]" for part in selector.split(", "))}'
        f'{{{declarations}}}' for selector, declarations in _THEME_RULES
    )
    return f'@media (prefers-color-scheme: dark){{{media}}}\n{outlook}'


def schedule_label(event, zone):
    """Show the configured event in ET and UTC using its date's time zone offset."""
    start_utc, end_utc = utc_times(event, zone)
    eastern = ZoneInfo('America/New_York')

    return display_range(start_utc.astimezone(eastern), end_utc.astimezone(eastern), 'ET') + ' · ' + display_range(start_utc, end_utc, 'UTC')

def build():
    config = json.loads((ROOT/'sessions.json').read_text())
    events = {event['id']: event for event in config['sessions']}
    zone = config['timezone']
    kickoff_schedule = schedule_label(events['collective-capital'], zone)
    ctas = json.loads((ROOT/'cta-links.json').read_text())['links']
    asset = lambda name: ORIGIN + '/assets/' + name + '.png'
    parts = ['''<mjml><mj-head><mj-title>Si Her DeFi — Season 1</mj-title><mj-preview>Let’s DeFi. Save your upcoming sessions.</mj-preview><mj-raw><meta name="color-scheme" content="light dark"><meta name="supported-color-schemes" content="light dark"></mj-raw><mj-attributes><mj-all font-family="Arial, Helvetica, sans-serif"/><mj-text color="#5a5a6e" font-size="14px" line-height="1.52" padding="0"/><mj-button background-color="#f2e8fa" color="#612d96" border-radius="6px" font-size="11px" font-weight="600" inner-padding="9px 12px" align="left" padding="0"/></mj-attributes><mj-style>.card {border-radius:14px;overflow:hidden}.upcoming-card{border-radius:6px}@media(max-width:639px){.primary-cta a{display:block!important;width:100%!important;box-sizing:border-box!important}.kickoff-image table td{width:auto!important}.kickoff-image img{max-width:100%!important;height:auto!important}} @media(max-width:480px){.outer>table>tbody>tr>td{padding-left:20px!important;padding-right:20px!important}.visual img{border-radius:0 0 5px 5px!important}}''' + dark_mode_css() + '''</mj-style></mj-head><mj-body width="640px" background-color="#ffffff">
<mj-section css-class="purple-band" background-color="#642d9a" padding="23px 32px"><mj-group><mj-column width="50%"><mj-image src="'''+asset('logo')+'''" width="140px" align="left" padding="0" alt="SI HER DEFI"/></mj-column><mj-column width="50%"><mj-text align="right" color="#ffffff" font-size="12px" letter-spacing="1px">YOUR WEEK IN DEFI</mj-text></mj-column></mj-group></mj-section>
<mj-section css-class="outer" padding="44px 40px 38px"><mj-column><mj-text color="#505050" font-size="16px" padding-bottom="16px">Season 1 | Si Her DeFi</mj-text><mj-text color="#0f1030" font-size="32px" font-weight="600" line-height="1.12" padding-bottom="8px">Let's DeFi.</mj-text><mj-text font-size="16px" color="#505050" line-height="1.6">Hi {firstName}, we are excited to embark on our DeFi journey together starting on Thursday, October 8th. This fall, we will be in a DeFi immersion with industry leaders guiding us in their areas of expertise.<br/><br/>A few housekeeping things before we dive in:<br/><br/>✅ If you're not able to attend all of the sessions live, it's ok! We will share our certification app invite in our next newsletter, where you can watch the replays and earn your module badges.<br/><br/>✅ We will add a few more sessions in coming newsletters, so please look out for those.<br/><br/>✅ Please add the upcoming modules to your calendar, and look out for new sessions in future Friday newsletters. To join live, use the Ro.am link on each session page or in the calendar event you save. We'll invite you to our new group chat space soon!<br/><br/>Each session button below opens a page with its live link and calendar options.</mj-text></mj-column></mj-section>
<mj-wrapper css-class="outer" padding="0 40px 24px"><mj-section css-class="card" border="1px solid #e5e5e5" padding="0"><mj-column><mj-image src="'''+asset('kickoff')+'''" css-class="kickoff-image" padding="0" alt="Wadooah Wali, Community Fund Leader at Artizen"/><mj-text padding="15px 20px 16px" font-size="15px" color="#666666">Kickoff | Thursday, Oct 8 | '''+kickoff_schedule+'''</mj-text><mj-text padding="0 20px 6px" font-size="24px" color="#0f1030" line-height="1.12" font-weight="600">Si Her Collective Capital</mj-text><mj-text padding="0 20px 16px">Meet Wadooah Wali, Community Fund Leader at Artizen, for the opening conversation on community capital and our Si Her grant fund on Artizen.</mj-text><mj-button href="'''+ctas['collective-capital']['href']+'''" padding="0 20px 16px" width="100%" css-class="primary-cta" background-color="#642d9a" color="#ffffff" font-size="16px" inner-padding="16px 18px" align="center">Add Oct 8 to calendar →</mj-button></mj-column></mj-section></mj-wrapper>''']
    featured = [
        ('web3-womens-day','Special Event | Oct 11','National Web3 Women’s Day','Join co-founder Morgen O’Conner for a 13-hour global celebration of women building the next era of Web3.','womens-day','Register to attend →')]
    for ident,tag,title,copy,img,label in featured:
        parts.append(f'''<mj-wrapper css-class="outer" padding="0 40px 24px"><mj-section css-class="card" border="1px solid #e5e5e5" padding="0"><mj-column width="49%" padding="16px"><mj-text font-size="13px" color="#642d9a" padding-bottom="16px">{tag}</mj-text><mj-text color="#0f1030" font-size="18px" font-weight="600" line-height="1.12" padding-bottom="7px">{title}</mj-text><mj-text padding-bottom="25px">{copy}</mj-text><mj-text><a href="{ctas[ident]['href']}" style="color:#642d9a;font-size:16px">{label}</a></mj-text></mj-column><mj-column width="51%" padding="12px"><mj-image src="{asset(img)}" padding="0" border-radius="8px" alt="{escape(title)}"/></mj-column></mj-section></mj-wrapper>''')
    parts.append('''<mj-section css-class="outer" padding="30px 40px 12px"><mj-column><mj-text color="#666666" font-size="16px" padding-bottom="12px">Upcoming Si Her DeFi Sessions</mj-text><mj-text color="#0f1030" font-size="23px" font-weight="600" line-height="1.12" padding-bottom="6px">Save every confirmed session</mj-text><mj-text font-size="13px">Add each session to your calendar (a couple more coming soon announced in our next newsletters!).</mj-text></mj-column></mj-section>''')
    meta = [
        ('tradfi-tall','Co-Founder, Ecosystem Lead · SI&lt;3&gt;'),('token-tall','Tokenomics Consultant · FinDaS'),('stablecoin-tall','CEO &amp; Co-Founder · Cashi'),('adoption-tall','LinkedIn Live'),('infra-tall','Head of Business Development · SODAX'),('futures-tall','Co-Founder &amp; Partner · IXIAN'),('capital-tall','LinkedIn Live'),('trade-tall','Director of Capital Formation · CryptoMommi')]
    for e,(img,role) in zip(config['sessions'][2:],meta):
        date=datetime.fromisoformat(e['date']); label=date.strftime('%b')+' '+str(date.day)+' · '+schedule_label(e, zone)
        action = (f'<mj-button href="{ctas[e["id"]]["href"]}" css-class="lavender-cta" width="142px">{"Register" if e["action"]=="register" else "Session details"} →</mj-button>'
                  if e['id'] in ctas else '<mj-text font-size="12px" color="#696477">Registration coming soon</mj-text>')
        parts.append(f'''<mj-wrapper css-class="outer" padding="0 40px 24px"><mj-section css-class="card upcoming-card" background-color="#f8f6ff" border="1px solid #e6d9ef" padding="0"><mj-column width="51.6%" padding="13px 14px 13px 10px"><mj-text color="#6b319a" font-size="12px" line-height="14px" padding-bottom="4px">{label}</mj-text><mj-text color="#141332" font-size="17px" font-weight="600" line-height="20px" padding-bottom="4px">{escape(e['title'])}</mj-text><mj-text color="#39205c" font-size="12px" font-weight="600" line-height="15px" padding-bottom="10px">{escape(e['speaker'])}</mj-text><mj-text color="#696477" font-size="11px" line-height="14px" padding-bottom="12px">{role}</mj-text>{action}</mj-column><mj-column css-class="visual" width="48.4%"><mj-image src="{asset(img)}" padding="0" border-radius="0 5px 5px 0" alt="{escape(e['title'])} session artwork"/></mj-column></mj-section></mj-wrapper>''')
    parts.append('''<mj-section padding="10px 0"/><mj-section css-class="purple-band" background-color="#642d9a" padding="30px 40px 16px"><mj-column><mj-text align="center" color="#ffffff" font-size="15px" letter-spacing="6px" line-height="34px">WE BELIEVE IN YOU</mj-text></mj-column></mj-section><mj-section css-class="purple-band" background-color="#642d9a" padding="0 40px 16px">''')
    for name,url,text in [('social-x','https://x.com/si3_ecosystem','@si3_ecosystem'),('social-web','https://www.si3.space/','www.si3.space'),('social-linkedin','https://www.linkedin.com/company/si3-ecosystem/','@si3-ecosystem')]:
        parts.append(f'''<mj-column padding="5px"><mj-button href="{url}" css-class="social-cta" background-color="#f4eef8" color="#000000" font-size="11px" border-radius="12px" inner-padding="10px"><img src="{asset(name)}" width="22" height="22" alt="" style="vertical-align:middle;margin-right:6px"/>{text}</mj-button></mj-column>''')
    parts.append('''</mj-section><mj-section css-class="purple-band" background-color="#642d9a" padding="0 40px 24px"><mj-column><mj-text align="center" color="#e3d4ee" font-size="12px" line-height="18px">You’re receiving this weekly email because you joined the Si Her DeFi cohort. Need help? Reply to this email and our team will support you.<br/><a href="{unsubscribe_link}" style="color:#ffffff">Unsubscribe</a></mj-text></mj-column></mj-section></mj-body></mjml>''')
    (ROOT/'newsletter.mjml').write_text('\n'.join(parts))

if __name__ == '__main__': build()
