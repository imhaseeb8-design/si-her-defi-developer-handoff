"""Prepare a standards-based invitation for an authorized sender; does not send mail."""
import argparse
import json
from email.message import EmailMessage
from email.policy import SMTP
from pathlib import Path
from build import make_ics, escape_ics, fold_ics

ROOT = Path(__file__).resolve().parent

def invitation(event, zone, organizer, attendee):
    for address in (organizer, attendee):
        if any(c in address for c in '\r\n:;') or '@' not in address:
            raise ValueError('Use a valid email address')
    calendar = make_ics(event, zone).decode().replace('METHOD:PUBLISH', 'METHOD:REQUEST')
    extra = [f'ORGANIZER;CN=Si Her DeFi:mailto:{organizer}',
             f'ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:{attendee}',
             'SEQUENCE:0']
    calendar = calendar.replace('END:VEVENT', '\r\n'.join(fold_ics(x) for x in extra) + '\r\nEND:VEVENT')
    msg = EmailMessage(policy=SMTP)
    msg['From'] = organizer
    msg['To'] = attendee
    msg['Subject'] = '[TEST] Si Her DeFi — ' + event['title']
    msg.set_content(f"You’re invited to {event['title']} with {event['speaker']}.\n{event['date']} · 10–11 am CST (UTC−6).\nThis is a test with a placeholder destination: {event['url']}\n")
    msg.add_alternative(calendar, subtype='calendar', charset='utf-8', params={'method':'REQUEST'})
    return msg

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--organizer', required=True, help='Verified, authorized sending address')
    parser.add_argument('--attendee', required=True, help='Direct receiving mailbox, not a forwarding address')
    parser.add_argument('--session', default='token-fundamentals')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    config = json.loads((ROOT/'sessions.json').read_text())
    event = next(e.copy() for e in config['sessions'] if e['id']==args.session)
    event.update(test=True, url=f"https://si-her-defi-calendar-test.imhaseeb8.chatgpt.site/join/{event['id']}/")
    Path(args.output).write_bytes(invitation(event, config['timezone'], args.organizer, args.attendee).as_bytes())
