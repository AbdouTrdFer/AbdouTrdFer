"""Generate the README dashboard from GitHub data using only Python's standard library.

Normal refresh uses GITHUB_TOKEN and GraphQL. --bootstrap reads the public calendar
without credentials; unavailable breakdown fields remain null, never invented.
"""
import argparse
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = 'AbdouTrdFer'

def request(url, token=None, payload=None):
    headers = {'User-Agent': 'AbdouTrdFer-profile', 'Accept': 'application/vnd.github+json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    data = None
    if payload is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=35) as response:
        return response.read().decode()

def api(path, token=None):
    return json.loads(request('https://api.github.com/' + path, token))

class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.counts = {}
        self.tip = None
        self.buffer = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and 'data-date' in attrs:
            self.cells[attrs['id']] = {'date': attrs['data-date'], 'level': int(attrs['data-level'])}
        if tag == 'tool-tip':
            self.tip = attrs.get('for')
            self.buffer = ''

    def handle_data(self, data):
        if self.tip:
            self.buffer += data

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.tip:
            match = re.match(r'(No|[\d,]+) contributions? on ', self.buffer.strip())
            if match:
                self.counts[self.tip] = 0 if match[1] == 'No' else int(match[1].replace(',', ''))
            self.tip = None

def public_calendar(html):
    parser = CalendarParser()
    parser.feed(html)
    if not parser.cells or any(key not in parser.counts for key in parser.cells):
        raise ValueError('GitHub calendar format changed; refusing to generate inaccurate counts.')
    days = sorted([dict(value, count=parser.counts[key]) for key, value in parser.cells.items()], key=lambda d:d['date'])
    # GitHub's public calendar includes leading days to fill its first week.
    # Keep exactly the displayed dates and sum those dates, rather than mixing periods.
    return days

def collect(token=None, bootstrap=False):
    now = datetime.now(timezone.utc)
    if bootstrap:
        days = public_calendar(request(f'https://github.com/users/{USER}/contributions'))
        user = api(f'users/{USER}')
        result = {'total': sum(d['count'] for d in days), 'commits': None, 'prs': None,
                  'reviews': None, 'issues': None, 'other': None, 'days': days,
                  'from': days[0]['date'], 'to': days[-1]['date'],
                  'repos': user['public_repos'], 'followers': user['followers'],
                  'source': 'Public calendar; breakdown awaits authenticated refresh'}
    else:
        if not token:
            raise ValueError('GITHUB_TOKEN is required. Use --bootstrap for a public-only initial snapshot.')
        query = '''query($login:String!) { user(login:$login) {
          followers { totalCount }
          repositories(privacy:PUBLIC, ownerAffiliations:OWNER) { totalCount }
          contributionsCollection {
            startedAt endedAt totalCommitContributions totalPullRequestContributions
            totalPullRequestReviewContributions totalIssueContributions
            contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
          }
        } }'''
        response = json.loads(request('https://api.github.com/graphql', token, {'query':query,'variables':{'login':USER}}))
        if response.get('errors') or not response.get('data',{}).get('user'):
            raise ValueError('GitHub GraphQL did not return a complete user record.')
        user = response['data']['user']
        c = user['contributionsCollection']
        days = [{'date':d['date'],'count':d['contributionCount']} for w in c['contributionCalendar']['weeks'] for d in w['contributionDays']]
        result = {'total':c['contributionCalendar']['totalContributions'],
                  'commits':c['totalCommitContributions'], 'prs':c['totalPullRequestContributions'],
                  'reviews':c['totalPullRequestReviewContributions'], 'issues':c['totalIssueContributions'],
                  'days':days, 'from':c['startedAt'][:10], 'to':c['endedAt'][:10],
                  'repos':user['repositories']['totalCount'], 'followers':user['followers']['totalCount'],
                  'source':'GitHub GraphQL / contributions visible to the workflow token'}
        subtotal = sum(result[k] for k in ['commits','prs','reviews','issues'])
        if subtotal > result['total']:
            raise ValueError('Contribution breakdown exceeds calendar total; preserving previous snapshot.')
        result['other'] = result['total'] - subtotal
    # Push events are a separate, limited feed; never add them to contribution totals.
    cutoff = now - timedelta(days=30)
    events = []
    try:
        for page in range(1,4):
            batch = api(f'users/{USER}/events/public?per_page=100&page={page}', token)
            if not isinstance(batch,list):
                raise ValueError('Invalid public event response')
            events.extend(batch)
            if len(batch) < 100:
                break
        events = list({e['id']:e for e in events}.values())
        result['pushes'] = sum(e['type']=='PushEvent' and datetime.fromisoformat(e['created_at'].replace('Z','+00:00')) >= cutoff for e in events)
        result['events_capped'] = len(events) >= 300
    except Exception as exc:
        print(f'Public push feed unavailable ({type(exc).__name__}); displaying a dash.', file=sys.stderr)
        result['pushes'] = None
        result['events_capped'] = False
    result['updated'] = now.strftime('%Y-%m-%d %H:%M UTC')
    result['username'] = USER
    return result

def number(value):
    return '—' if value is None else f'{value:,}'

# The renderer is independent of data collection and uses no external packages.
from activity_art import render, render_mobile

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--bootstrap',action='store_true')
    parser.add_argument('--render-only',action='store_true')
    args=parser.parse_args()
    path=ROOT/'data/activity.json'
    data=json.loads(path.read_text(encoding='utf-8')) if args.render_only else collect(os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN'),args.bootstrap)
    output=render(data)
    mobile=render_mobile(data)
    # Fetch and render completely before replacing the last successful snapshot.
    path.parent.mkdir(parents=True,exist_ok=True)
    (ROOT/'assets').mkdir(exist_ok=True)
    if not args.render_only:
        path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    (ROOT/'assets/activity.svg').write_text(output,encoding='utf-8')
    (ROOT/'assets/activity-mobile.svg').write_text(mobile,encoding='utf-8')
    followers=number(data.get('followers'))
    badge=f'<svg xmlns="http://www.w3.org/2000/svg" width="130" height="20" role="img"><title>GitHub followers: {followers}</title><path fill="#eef3fb" d="M0 0h95v20H0z"/><path fill="#6287c7" d="M95 0h35v20H95z"/><g fill="#526a8b" font-family="Arial,sans-serif" font-size="10" text-anchor="middle"><text x="47.5" y="14">FOLLOWERS</text><text x="112.5" y="14" fill="#fff">{followers}</text></g></svg>'
    (ROOT/'assets/followers.svg').write_text(badge,encoding='utf-8')
    print(f'Updated dashboard: {data["total"]} contributions, {data["from"]} to {data["to"]}.')

if __name__=='__main__':
    main()
