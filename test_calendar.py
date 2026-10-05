import unittest
import re
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from build import make_ics, provider_links, render, utc_times
from datetime import timedelta
from newsletter import schedule_label


def event(date='2026-10-22'):
    return {'id': 'token-fundamentals', 'title': 'Token Fundamentals', 'speaker': 'Diana Ilieva',
            'date': date, 'start': '10:00', 'end': '11:00', 'url': 'https://example.org/live?session=1&cohort=2'}


class CalendarTests(unittest.TestCase):
    def test_central_daylight_saving_transition(self):
        for date, expected in [('2026-10-22', '20261022T150000Z'), ('2026-11-05', '20261105T160000Z')]:
            e = event(date)
            ics = make_ics(e, 'America/Chicago').decode()
            google = parse_qs(urlsplit(provider_links(e, 'America/Chicago')['google']).query)
            outlook = parse_qs(urlsplit(provider_links(e, 'America/Chicago')['outlook']).query)
            self.assertIn('DTSTART:' + expected, ics)
            self.assertTrue(google['dates'][0].startswith(expected))
            self.assertEqual(outlook['startdt'][0].replace('-', '').replace(':', ''), expected)
            self.assertEqual(google['location'][0], e['url'])

    def test_fixed_utc_minus_six_is_different_in_october(self):
        self.assertIn(b'DTSTART:20261022T160000Z', make_ics(event(), 'Etc/GMT+6'))
        page = render(event(), 'Etc/GMT+6', True)
        self.assertIn('10:00–11:00 AM Mexico City time<br>12:00–1:00 PM ET<br>4:00–5:00 PM UTC', page)
        self.assertIn('data-start="2026-10-22T16:00:00+00:00"', page)
        self.assertNotIn('&lt;br&gt;', page)

    def test_confirmed_modules_keep_noon_eastern_across_clock_change(self):
        config = json.loads((Path(__file__).resolve().parent / 'sessions.json').read_text())
        self.assertEqual(config['timezone'], 'America/New_York')
        for e in config['sessions']:
            if e['action'] != 'calendar':
                continue
            with self.subTest(session=e['id']):
                self.assertEqual((e['start'], e['end']), ('12:00', '13:00'))
                date = e['date']
                start_hour, end_hour = (16, 17) if date < '2026-11-01' else (17, 18)
                expected_start = f'{date}T{start_hour}:00:00Z'
                expected_end = f'{date}T{end_hour}:00:00Z'
                links = provider_links(e, config['timezone'])
                google = parse_qs(urlsplit(links['google']).query)
                compact = lambda value: value.replace('-', '').replace(':', '')
                self.assertEqual(google['dates'][0], compact(expected_start) + '/' + compact(expected_end))
                self.assertEqual(google['stz'][0], 'America/New_York')
                for provider in ('outlook', 'microsoft'):
                    query = parse_qs(urlsplit(links[provider]).query)
                    self.assertEqual(query['startdt'][0], expected_start)
                    self.assertEqual(query['enddt'][0], expected_end)
                    self.assertEqual(query['location'][0], e['url'])
                utc_label = '4:00–5:00 PM UTC' if start_hour == 16 else '5:00–6:00 PM UTC'
                self.assertEqual(schedule_label(e, config['timezone']), '12:00–1:00 PM ET · ' + utc_label)
                page = render(e, config['timezone'], True)
                mexico_label = '10:00–11:00 AM Mexico City time' if start_hour == 16 else '11:00 AM–12:00 PM Mexico City time'
                self.assertIn(mexico_label + '<br>12:00–1:00 PM ET<br>' + utc_label, page)
                self.assertIn('data-start="' + expected_start.replace('Z', '+00:00') + '"', page)
                self.assertIn('data-end="' + expected_end.replace('Z', '+00:00') + '"', page)

    def test_confirmed_linkedin_lives_start_one_hour_later(self):
        config = json.loads((Path(__file__).resolve().parent / 'sessions.json').read_text())
        events = {item['id']: item for item in config['sessions']}
        for ident in ('proof-of-adoption', 'capital-table'):
            item = events[ident]
            self.assertEqual((item['start'], item['end']), ('13:00', '14:00'))
            self.assertEqual(item['speaker'], 'Speakers to be announced')
            self.assertEqual(schedule_label(item, config['timezone']),
                             '1:00–2:00 PM ET · 6:00–7:00 PM UTC')
            start, end = utc_times(item, config['timezone'])
            self.assertEqual(start.isoformat(), item['date'] + 'T18:00:00+00:00')
            self.assertEqual(end.isoformat(), item['date'] + 'T19:00:00+00:00')
            module = dict(item, start='12:00', end='13:00')
            module_start, module_end = utc_times(module, config['timezone'])
            self.assertEqual(start - module_start, timedelta(hours=1))
            self.assertEqual(end - module_end, timedelta(hours=1))

    def test_test_events_are_labeled_and_use_separate_uid(self):
        e = event()
        live = make_ics(e, 'America/Chicago')
        e['test'] = True
        test = make_ics(e, 'America/Chicago')
        self.assertIn(b'SUMMARY:[TEST] Si Her DeFi:', test)
        self.assertNotEqual(re.search(rb'UID:([^\r]+)', live)[1], re.search(rb'UID:([^\r]+)', test)[1])

    def test_utf8_folding_and_text_escaping(self):
        e = event()
        e['title'] = 'Learning, building; together\\more\n' + '🌱' * 60
        raw = make_ics(e, 'America/Chicago')
        self.assertNotIn(b'\n', raw.replace(b'\r\n', b''))
        for line in raw.split(b'\r\n'):
            self.assertLessEqual(len(line), 75)
            line.decode('utf-8')
        unfolded = raw.replace(b'\r\n ', b'').decode()
        self.assertIn('Learning\\, building\\; together\\\\more\\n', unfolded)

    def test_draft_has_no_actionable_calendar_links(self):
        page = render(event(), None, False)
        self.assertEqual(len(re.findall(r'<a\b[^>]*aria-disabled="true"', page)), 3)
        self.assertNotIn('href="token-fundamentals.ics"', page)
        self.assertNotIn('__TITLE__', page)

    def test_ready_page_escapes_query_strings_and_shows_copyable_link(self):
        page = render(event(), 'America/Chicago', True)
        self.assertIn('id="copy-link"', page)
        self.assertIn('id="session-link"', page)
        self.assertNotIn('.ics', page)
        self.assertIn('&amp;', page)
        self.assertNotIn('Preview ·', page)


if __name__ == '__main__':
    unittest.main()
