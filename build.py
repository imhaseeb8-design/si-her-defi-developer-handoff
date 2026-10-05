"""Build static calendar pages and ICS files from verified session details."""
import argparse
import html
import json
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
UTC = timezone.utc


def utc_times(event, zone):
    tz = ZoneInfo(zone)
    start = datetime.fromisoformat(f"{event['date']}T{event['start']}").replace(tzinfo=tz)
    end = datetime.fromisoformat(f"{event['date']}T{event['end']}").replace(tzinfo=tz)
    if end <= start:
        raise ValueError(f"{event['id']}: end must be after start")
    return start.astimezone(UTC), end.astimezone(UTC)


def display_range(start, end, label):
    clock = lambda value: f'{value.hour % 12 or 12}:{value.minute:02d}'
    start_suffix = f' {start:%p}' if start.strftime('%p') != end.strftime('%p') else ''
    return f'{clock(start)}{start_suffix}–{clock(end)} {end:%p} {label}'


def https_url(value):
    parsed = urlsplit(value)
    return parsed.scheme == 'https' and bool(parsed.hostname) and not parsed.username and not parsed.password


def details(event):
    prefix = 'TEST EVENT — placeholder destination. Use the date and time shown on the session page.\n\n' if event.get('test') else ''
    return prefix + f"{event['title']}\n{event['speaker']}\n\nJoin the live session:\n{event['url']}"


def event_title(event):
    return ('[TEST] ' if event.get('test') else '') + f"Si Her DeFi: {event['title']}"


def provider_links(event, zone):
    start, end = utc_times(event, zone)
    google = 'https://calendar.google.com/calendar/r/eventedit?' + urlencode({
        'action': 'TEMPLATE', 'text': event_title(event),
        'dates': f"{start:%Y%m%dT%H%M%SZ}/{end:%Y%m%dT%H%M%SZ}",
        'details': details(event), 'location': event['url'], 'stz': zone, 'etz': zone,
    })
    query = urlencode({
        'subject': event_title(event), 'startdt': start.isoformat().replace('+00:00', 'Z'),
        'enddt': end.isoformat().replace('+00:00', 'Z'), 'body': details(event),
        'location': event['url'], 'allday': 'false', 'path': '/calendar/action/compose', 'rru': 'addevent',
    })
    return {'google': google, 'outlook': 'https://outlook.live.com/calendar/0/deeplink/compose?' + query,
            'microsoft': 'https://outlook.office.com/calendar/0/deeplink/compose?' + query}


def escape_ics(text):
    return str(text).replace('\\', '\\\\').replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')


def fold_ics(line):
    # RFC 5545: fold at 75 octets without splitting UTF-8 code points.
    chunks, current = [], ''
    for char in line:
        if len((current + char).encode('utf-8')) > 75:
            chunks.append(current)
            current = ' '
        current += char
    chunks.append(current)
    return '\r\n'.join(chunks)


def make_ics(event, zone):
    start, end = utc_times(event, zone)
    uid = uuid.uuid5(uuid.NAMESPACE_URL, 'si-her-defi:' + ('test:' if event.get('test') else 'live:') + event['id'])
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//SI3//Si Her DeFi//EN', 'CALSCALE:GREGORIAN',
             'METHOD:PUBLISH', 'BEGIN:VEVENT', f'UID:urn:uuid:{uid}',
             f'DTSTAMP:{datetime.now(UTC):%Y%m%dT%H%M%SZ}',
             f'DTSTART:{start:%Y%m%dT%H%M%SZ}', f'DTEND:{end:%Y%m%dT%H%M%SZ}',
             'SUMMARY:' + escape_ics(event_title(event)),
             'DESCRIPTION:' + escape_ics(details(event)), 'LOCATION:' + escape_ics(event['url']),
             'URL:' + event['url'], 'STATUS:CONFIRMED', 'TRANSP:OPAQUE', 'END:VEVENT', 'END:VCALENDAR']
    return ('\r\n'.join(fold_ics(line) for line in lines) + '\r\n').encode('utf-8')


def render(event, zone, ready=False):
    template = (ROOT / 'page.html').read_text()
    date = datetime.fromisoformat(event['date'])
    date_label = f"{date:%A}, {date:%B} {date.day}"
    if ready:
        start, end = utc_times(event, zone)
        mexico = ZoneInfo('America/Mexico_City')
        eastern = ZoneInfo('America/New_York')
        time_label = '<br>'.join((display_range(start.astimezone(mexico), end.astimezone(mexico), 'Mexico City time'),
                                display_range(start.astimezone(eastern), end.astimezone(eastern), 'ET'),
                                display_range(start, end, 'UTC')))
        urls = provider_links(event, zone)
        link = lambda url: 'href="' + html.escape(url, quote=True) + '" target="_blank" rel="noopener noreferrer"'
        buttons = {name.upper(): link(url) for name, url in urls.items()}
        safe_url = html.escape(event['url'], quote=True)
        join = f'<div class="join"><p class="join-label">Session link</p><div class="join-row"><a id="session-link" href="{safe_url}" target="_blank" rel="noopener noreferrer">{html.escape(event["url"])}</a><button id="copy-link" type="button" data-url="{safe_url}">Copy</button></div></div>'
        manual = '<p class="manual">Using Proton or Apple Calendar? Create an event for the date and time above, then paste the session link into its location. This page does not send calendar invitations.</p>'
        draft = '<p class="draft">Test event · Placeholder join link. Use the date and time shown above.</p>' if event.get('test') else ''
    else:
        time_label = 'Time and timezone awaiting confirmation'
        buttons = {name: 'aria-disabled="true"' for name in ['GOOGLE', 'OUTLOOK', 'MICROSOFT']}
        join = ''
        manual = ''
        draft = '<p class="draft">Preview · Calendar links will be activated once the session details are confirmed.</p>'
    replacements = {'TITLE': html.escape(event['title']), 'SPEAKER': html.escape(event['speaker']),
                    'DATE': html.escape(date_label + f', {date.year}'), 'TIME': time_label, 'START_ISO': start.isoformat() if ready else '', 'END_ISO': end.isoformat() if ready else '', 'DRAFT': draft, 'JOIN': join, 'MANUAL': manual, **buttons}
    for key, value in replacements.items():
        template = template.replace(f'__{key}__', value)
    return template


def build(base_url=None, test=False):
    config = json.loads((ROOT / 'sessions.json').read_text())
    zone = config.get('timezone')
    if zone:
        ZoneInfo(zone)
    if base_url and not https_url(base_url):
        raise ValueError('The hosted base URL must be HTTPS')
    if test:
        if not base_url:
            raise ValueError('Test mode requires a hosted base URL')
        zone = config.get('timezone') or 'Etc/GMT+6'
        for event in config['sessions']:
            event.update(test=True, confirmed=True, url=f"{base_url.rstrip('/')}/join/{event['id']}/")
            event['start'] = event['start'] or '10:00'
            event['end'] = event['end'] or '11:00'
    dist = ROOT / 'dist'
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir()
    ctas, pending = {}, []
    events = config['sessions']
    ids = [event['id'] for event in events]
    if len(ids) != len(set(ids)):
        raise ValueError('Session IDs must be unique')
    for event in events:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', event['id']):
            raise ValueError('Invalid session ID')
        if event['url'] and not https_url(event['url']):
            raise ValueError(f"{event['id']}: session URL must be HTTPS")
        if test:
            destination = dist / 'join' / event['id']
            destination.mkdir(parents=True)
            destination.joinpath('index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Test destination · Si Her DeFi</title><style>body{margin:0;min-height:100svh;display:grid;place-items:center;font:16px/1.6 Arial,sans-serif;background:#f8f6fb;color:#141332}main{max-width:420px;padding:32px}h1{line-height:1.2;color:#642d9a}</style><main><p>SI HER DEFI · TEST DESTINATION</p><h1>' + html.escape(event['title']) + '</h1><p>Your event link works.</p><p>This is a placeholder for testing. The live session will happen at the confirmed Ro.am URL.</p></main></html>')
        ready = bool(event['confirmed'] and event['url'])
        if event['action'] == 'register':
            if ready:
                ctas[event['id']] = {'label': 'Register', 'href': event['url']}
            else:
                pending.append(event['id'])
            continue
        ready = bool(ready and zone and event['start'] and event['end'])
        folder = dist / 'calendar' / event['id']
        folder.mkdir(parents=True)
        (folder / 'index.html').write_text(render(event, zone, ready))
        if ready:
            if base_url:
                ctas[event['id']] = {'label': 'Session details and calendar', 'href': f"{base_url.rstrip('/')}/calendar/{event['id']}/"}
        else:
            pending.append(event['id'])
    sample = next(event for event in events if event['id'] == 'token-fundamentals')
    shutil.copytree(ROOT / 'assets', dist / 'assets', dirs_exist_ok=True)
    (dist / 'index.html').write_text(render(sample, zone, bool(sample['confirmed'] and sample['url'])))
    (ROOT / 'cta-links.json').write_text(json.dumps({'links': ctas, 'pending': pending}, indent=2) + '\n')
    snippets = [f'<!-- {key} -->\n<mj-button href="{html.escape(value["href"], quote=True)}">{value["label"]}</mj-button>' for key, value in ctas.items()]
    (ROOT / 'email-ctas.mjml').write_text('<!-- Insert these snippets into your existing MJML columns. -->\n' + '\n\n'.join(snippets) + '\n')
    if test:
        email = (ROOT / 'test-email-template.mjml').read_text().replace('__CALENDAR_URL__', html.escape(ctas['token-fundamentals']['href'], quote=True))
        (ROOT / 'test-email.mjml').write_text(email)
    print(json.dumps({'calendar_pages': sum(e['action'] == 'calendar' for e in events), 'pending': pending, 'output': str(dist)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', help='Verified hosted HTTPS origin for final email CTA links')
    parser.add_argument('--test', action='store_true', help='Use clearly labeled test events and hosted placeholder destinations')
    args = parser.parse_args()
    build(args.base_url, args.test)
