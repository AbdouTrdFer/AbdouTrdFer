"""Generate the README dashboard from GitHub data using only Python's standard library.

Normal refresh uses GITHUB_TOKEN and GraphQL. --bootstrap reads the public calendar
without credentials; unavailable breakdown fields remain null, never invented.
"""
import argparse
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import re
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = 'AbdouTrdFer'
COLORS = ['#bdff83', '#95d8d2', '#c6b9f2', '#f2c891', '#82948c']

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

def render(data):
    bg, panel, line, ink, muted = '#0b1514','#101f1c','#263c35','#eef5ee','#a3b8ac'
    def t(x,y,value,size=14,color=ink,weight=400,extra=''):
        return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" {extra}>{escape(str(value))}</text>'
    body=f'<rect width="1000" height="670" rx="18" fill="{bg}"/><rect x=".5" y=".5" width="999" height="669" rx="18" fill="none" stroke="{line}"/>'
    body+=t(30,37,'THE BUILD LOG',12,COLORS[0],400,'class="mono" letter-spacing="2"')+t(970,37,'GITHUB / ACTIVITY',11,muted,400,'class="mono" text-anchor="end"')
    body+=t(30,84,'Small steps. Visible progress.',30,ink,700)+t(30,112,f'{data["from"]} → {data["to"]}',13,muted,400,'class="mono"')
    for i,(value,label,note) in enumerate([(data['total'],'TOTAL CONTRIBUTIONS','Displayed reporting period'),(data.get('pushes'),'RECENT PUBLIC PUSHES','30 days · limited event feed'),(data.get('repos'),'PUBLIC REPOSITORIES','Current public repository count'),(data.get('followers'),'FOLLOWERS','Current GitHub followers')]):
        x=30+i*241
        body+=f'<rect x="{x}" y="136" width="217" height="112" rx="10" fill="{panel}"/>'+t(x+16,162,label,10,muted,400,'class="mono" letter-spacing=".5"')+t(x+16,203,number(value)+('+' if i==1 and data.get('events_capped') else ''),35,COLORS[0] if i==0 else ink,700)+t(x+16,229,note,10,muted)
    body+=t(30,285,'CONTRIBUTION MIX',11,muted,400,'class="mono" letter-spacing="1.3"')
    cx,cy,r=147,390,73
    body+=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{line}" stroke-width="17"/>'
    circumference=2*math.pi*r
    offset=0
    keys=['commits','prs','reviews','issues','other']
    available=all(data.get(k) is not None for k in keys)
    if available and data['total']:
        for key,color in zip(keys,COLORS):
            length=data[key]/data['total']*circumference
            if length>0:
                body+=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="17" stroke-dasharray="{length:.4f} {circumference-length:.4f}" stroke-dashoffset="{-offset:.4f}" transform="rotate(-90 {cx} {cy})"/>'
            offset+=length
    body+=t(cx,391,number(data['total']),33,ink,700,'text-anchor="middle"')+t(cx,414,'CONTRIBUTIONS',9,muted,400,'text-anchor="middle" class="mono"')
    for i,(key,label,color) in enumerate(zip(keys,['Commits','Pull requests','Reviews','Issues','Other / restricted'],COLORS)):
        y=327+i*32
        body+=f'<circle cx="270" cy="{y-4}" r="4" fill="{color}"/>'+t(284,y,label,14,muted)+t(472,y,number(data.get(key)),16,ink,700,'text-anchor="end"')
    body+=f'<line x1="502" y1="286" x2="502" y2="467" stroke="{line}"/>'
    days=data['days']
    active=sum(d['count']>0 for d in days)
    best=max((d['count'] for d in days),default=0)
    body+=t(537,311,'CONSISTENCY OVER NOISE.',12,COLORS[0],400,'class="mono" letter-spacing="1"')+t(537,352,f'{active} active days',29,ink,700)+t(537,381,f'{best} contributions on the busiest day',14,muted)
    body+=t(537,426,'Every iteration is part of the process.',14,muted)
    body+=t(537,452,'Daily snapshot · real GitHub activity',12,muted)
    body+=t(30,500,'CONTRIBUTION CALENDAR',11,muted,400,'class="mono" letter-spacing="1.3"')
    start=date.fromisoformat(days[0]['date'])
    start-=timedelta(days=(start.weekday()+1)%7)
    max_count=max(best,1)
    shades=[panel,'#294b36','#477a49','#7ab85e',COLORS[0]]
    weeks=max(((date.fromisoformat(d['date'])-start).days//7 for d in days),default=52)+1
    step=min(17.5,935/weeks)
    for d in days:
        current=date.fromisoformat(d['date'])
        delta=(current-start).days
        level=0 if d['count']==0 else min(4,1+int(3*(d['count']/max_count)**.5))
        x=30+(delta//7)*step
        y=516+(delta%7)*13
        body+=f'<rect x="{x:.1f}" y="{y}" width="{step-3:.1f}" height="10" rx="2" fill="{shades[level]}"><title>{d["date"]}: {d["count"]} contributions</title></rect>'
    body+=t(30,630,'UPDATED '+data['updated'],10,muted,400,'class="mono"')
    note='Breakdown available after first workflow run' if not available else 'Pushes are separate from contribution totals'
    body+=t(970,630,note,10,muted,400,'text-anchor="end"')
    body+=t(30,650,'Public calendar snapshot' if not available else 'GitHub API snapshot',10,muted)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="670" viewBox="0 0 1000 670" role="img" aria-labelledby="title desc"><title id="title">GitHub activity for {USER}</title><desc id="desc">{escape(data["source"])}. {escape(note)}.</desc><style>text{{font-family:Arial,Helvetica,sans-serif}}.mono{{font-family:Consolas,monospace}}</style>{body}</svg>'

def render_mobile(data):
    """Reflow the same real snapshot; do not shrink desktop labels on phones."""
    bg,panel,line,ink,muted='#0b1514','#101f1c','#263c35','#eef5ee','#a3b8ac'
    def t(x,y,value,size=14,color=ink,weight=400,extra=''):
        return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" {extra}>{escape(str(value))}</text>'
    body=f'<rect width="480" height="850" rx="16" fill="{bg}"/>'
    body+=t(24,36,'THE BUILD LOG',12,COLORS[0])+t(24,75,'Small steps.',30,ink,700)+t(24,110,'Visible progress.',30,ink,700)
    body+=t(24,140,f'{data["from"]} → {data["to"]}',13,muted)
    for i,(key,label,note) in enumerate([('total','CONTRIBUTIONS','Displayed period'),('pushes','PUBLIC PUSHES','30 days · limited feed'),('repos','PUBLIC REPOS','Current count'),('followers','FOLLOWERS','Current count')]):
        x=24+(i%2)*222
        y=162+(i//2)*112
        body+=f'<rect x="{x}" y="{y}" width="210" height="100" rx="9" fill="{panel}"/>'+t(x+14,y+24,label,12,muted)+t(x+14,y+62,number(data.get(key))+('+' if key=='pushes' and data.get('events_capped') else ''),32,COLORS[0] if key=='total' else ink,700)+t(x+14,y+84,note,11,muted)
    body+=t(24,410,'CONTRIBUTION MIX',12,muted)
    cx,cy,r=119,514,68
    body+=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{line}" stroke-width="16"/>'
    keys=['commits','prs','reviews','issues','other']
    available=all(data.get(k) is not None for k in keys)
    offset=0
    circ=2*math.pi*r
    if available and data['total']:
        for key,color in zip(keys,COLORS):
            length=data[key]/data['total']*circ
            if length:
                body+=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="16" stroke-dasharray="{length:.4f} {circ-length:.4f}" stroke-dashoffset="{-offset:.4f}" transform="rotate(-90 {cx} {cy})"/>'
            offset+=length
    body+=t(cx,514,number(data['total']),31,ink,700,'text-anchor="middle"')+t(cx,538,'CONTRIBUTIONS',10,muted,400,'text-anchor="middle"')
    for i,(key,label,color) in enumerate(zip(keys,['Commits','Pull requests','Reviews','Issues','Other / restricted'],COLORS)):
        y=453+i*30
        body+=f'<circle cx="226" cy="{y-4}" r="4" fill="{color}"/>'+t(239,y,label,14,muted)+t(451,y,number(data.get(key)),16,ink,700,'text-anchor="end"')
    active=sum(d['count']>0 for d in data['days'])
    body+=t(24,626,f'{active} active days in the reporting period',17,ink,700)
    body+=t(24,655,'CALENDAR / MOST RECENT 26 WEEKS',12,muted)
    end=date.fromisoformat(data['days'][-1]['date'])
    start=end-timedelta(days=(end.weekday()+1)%7+25*7)
    best=max(max(d['count'] for d in data['days']),1)
    shades=[panel,'#294b36','#477a49','#7ab85e',COLORS[0]]
    for d in data['days']:
        delta=(date.fromisoformat(d['date'])-start).days
        if delta<0:
            continue
        level=0 if d['count']==0 else min(4,1+int(3*(d['count']/best)**.5))
        body+=f'<rect x="{24+(delta//7)*16.6:.1f}" y="{675+(delta%7)*12}" width="13" height="9" rx="2" fill="{shades[level]}"><title>{d["date"]}: {d["count"]}</title></rect>'
    body+=t(24,786,'Updated '+data['updated'],12,muted)
    body+=t(24,814,'Breakdown appears after the first workflow run.' if not available else 'Pushes are separate from contribution totals.',11,muted)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="850" viewBox="0 0 480 850" role="img"><title>GitHub activity for {USER}, mobile layout</title><style>text{{font-family:Arial,Helvetica,sans-serif}}</style>{body}</svg>'

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
    badge=f'<svg xmlns="http://www.w3.org/2000/svg" width="130" height="20" role="img"><title>GitHub followers: {followers}</title><path fill="#172722" d="M0 0h95v20H0z"/><path fill="#157a68" d="M95 0h35v20H95z"/><g fill="#fff" font-family="Arial,sans-serif" font-size="10" text-anchor="middle"><text x="47.5" y="14">FOLLOWERS</text><text x="112.5" y="14">{followers}</text></g></svg>'
    (ROOT/'assets/followers.svg').write_text(badge,encoding='utf-8')
    print(f'Updated dashboard: {data["total"]} contributions, {data["from"]} to {data["to"]}.')

if __name__=='__main__':
    main()
