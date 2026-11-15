"""Light, readable SVG layouts for an existing GitHub activity snapshot."""
from datetime import date, timedelta
from html import escape
import math

INK, MUTED, LINE, PALE = '#203451', '#5c7089', '#dde6f2', '#f5f8fd'
COLORS = ['#6287d5', '#49a9a1', '#a18bc7', '#dba16e', '#c6d1e0']
KEYS = ['commits','prs','reviews','issues','other']
LABELS = ['Commits','Pull requests','Reviews','Issues','Other / restricted']

def number(value):
    return '—' if value is None else f'{value:,}'

def t(x,y,value,size=14,color=INK,weight=400,extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" {extra}>{escape(str(value))}</text>'

def rect(x,y,w,h,fill='#fff',radius=12,stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'

def svg(w,h,body,data):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">GitHub activity for {escape(data["username"])}</title><desc id="desc">{escape(data["source"])}. Updated {escape(data["updated"])}.</desc><style>text{{font-family:Arial,Helvetica,sans-serif}}</style>{body}</svg>'

def ring(data,cx,cy,r):
    body=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#ecf1f8" stroke-width="17"/>'
    circumference=2*math.pi*r
    offset=0
    if all(data.get(k) is not None for k in KEYS) and data['total']:
        for key,color in zip(KEYS,COLORS):
            length=data[key]/data['total']*circumference
            if length>0:
                body+=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="17" stroke-dasharray="{length:.4f} {circumference-length:.4f}" stroke-dashoffset="{-offset:.4f}" transform="rotate(-90 {cx} {cy})"/>'
            offset+=length
    return body+t(cx,cy+2,number(data['total']),36,INK,700,'text-anchor="middle"')+t(cx,cy+25,'contributions',13,MUTED,400,'text-anchor="middle"')

def legend(data,x,y,width):
    body=''
    for i,(key,label,color) in enumerate(zip(KEYS,LABELS,COLORS)):
        row=y+i*31
        body+=f'<circle cx="{x}" cy="{row-5}" r="4.5" fill="{color}"/>'+t(x+15,row,label,14,MUTED)+t(x+width,row,number(data.get(key)),16,INK,600,'text-anchor="end"')
    return body

def calendar(data,x,y,width,mobile=False):
    days=data['days']
    if not days:
        return ''
    start=date.fromisoformat(days[0]['date'])
    start-=timedelta(days=(start.weekday()+1)%7)
    if mobile:
        end=date.fromisoformat(days[-1]['date'])
        start=end-timedelta(days=(end.weekday()+1)%7+25*7)
    weeks=max(((date.fromisoformat(d['date'])-start).days//7 for d in days),default=52)+1
    step=width/weeks
    best=max(max(d['count'] for d in days),1)
    shades=['#edf2f9','#d1e3f3','#9ac5e2','#62a6cd','#3c82b6']
    body=''
    last_month=None
    for d in days:
        current=date.fromisoformat(d['date'])
        delta=(current-start).days
        if delta<0:
            continue
        level=0 if d['count']==0 else min(4,1+int(3*(d['count']/best)**.5))
        px=x+(delta//7)*step
        py=y+(delta%7)*12
        body+=f'<rect x="{px:.1f}" y="{py}" width="{step-3:.1f}" height="9" rx="2" fill="{shades[level]}"><title>{d["date"]}: {d["count"]} contributions</title></rect>'
        if current.day<=7 and current.month!=last_month and (delta//7)<weeks-2:
            body+=t(round(px,1),y-9,current.strftime('%b'),10,MUTED)
            last_month=current.month
    return body

def render(data):
    body=rect(.75,.75,998.5,602.5,'#fff',18,LINE)
    body+=t(30,43,'A little progress, every day.',26,INK,600,'letter-spacing="-.6"')
    body+=t(970,41,f'{data["from"]} — {data["to"]}',13,MUTED,400,'text-anchor="end"')
    cards=[('total','Contributions','Reporting period','#f0f5ff'),('pushes','Public pushes','Last 30 days · limited feed','#eef8f5'),('repos','Public repositories','Current count','#f5f1fb'),('followers','Followers','Current count','#fff7ee')]
    for i,(key,label,note,fill) in enumerate(cards):
        x=30+i*241
        body+=rect(x,72,217,113,fill)
        body+=t(x+17,99,label,14,MUTED)+t(x+17,143,number(data.get(key))+('+' if key=='pushes' and data.get('events_capped') else ''),38,INK,700,'letter-spacing="-1"')+t(x+17,167,note,11,MUTED)
    body+=t(30,222,'How I contribute',17,INK,600)
    body+=ring(data,145,323,72)+legend(data,263,263,203)
    body+=f'<path d="M505 227V408" stroke="{LINE}"/>'
    active=sum(d['count']>0 for d in data['days'])
    best=max((d['count'] for d in data['days']),default=0)
    body+=rect(540,230,430,179,PALE)
    body+=t(563,262,'One project. One improvement. One step.',16,MUTED)
    body+=t(563,311,str(active),39,INK,700)+t(640,309,'active days',18,MUTED)
    body+=t(563,344,f'{best} contributions on the busiest day',14,MUTED)
    body+=t(563,383,'Built over time, one iteration at a time.',13,MUTED)
    body+=t(30,446,'The contribution trail',17,INK,600)
    body+=t(827,445,'Less',10,MUTED)
    for i,color in enumerate(['#edf2f9','#d1e3f3','#9ac5e2','#62a6cd','#3c82b6']):
        body+=rect(854+i*17,435,12,10,color,2)
    body+=t(944,445,'More',10,MUTED)
    body+=calendar(data,30,480,940)
    body+=t(30,585,'Updated '+data['updated'],11,MUTED)
    note='Breakdown awaits authenticated refresh' if any(data.get(k) is None for k in KEYS) else 'Daily snapshot · GitHub API'
    body+=t(970,585,note,11,MUTED,400,'text-anchor="end"')
    return svg(1000,604,body,data)

def render_mobile(data):
    body=rect(.75,.75,478.5,848.5,'#fff',16,LINE)
    body+=t(24,40,'A little progress,',28,INK,600)+t(24,75,'every day.',28,INK,600)
    body+=t(24,105,f'{data["from"]} — {data["to"]}',13,MUTED)
    cards=[('total','Contributions','Reporting period','#f0f5ff'),('pushes','Public pushes','30 days · limited feed','#eef8f5'),('repos','Public repositories','Current count','#f5f1fb'),('followers','Followers','Current count','#fff7ee')]
    for i,(key,label,note,fill) in enumerate(cards):
        x=24+(i%2)*222
        y=128+(i//2)*113
        body+=rect(x,y,210,101,fill)+t(x+14,y+24,label,14,MUTED)+t(x+14,y+64,number(data.get(key))+('+' if key=='pushes' and data.get('events_capped') else ''),35,INK,700)+t(x+14,y+86,note,11,MUTED)
    body+=t(24,396,'How I contribute',19,INK,600)
    body+=ring(data,118,501,68)+legend(data,223,443,226)
    active=sum(d['count']>0 for d in data['days'])
    body+=rect(24,603,432,52,PALE)+t(40,636,f'{active} active days in the reporting period',17,INK,600)
    body+=t(24,687,'The contribution trail',17,INK,600)+t(24,709,'Most recent 26 weeks',12,MUTED)
    body+=calendar(data,24,738,432,mobile=True)
    body+=t(24,835,'Updated '+data['updated'],11,MUTED)
    return svg(480,850,body,data)
