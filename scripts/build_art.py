"""Original light profile artwork. Motion stays in self-contained SVG/GIF assets."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
INK, MUTED, BLUE, TEAL, PURPLE = '#203451', '#5c7089', '#386ad9', '#177c80', '#8063b9'

def text(x, y, value, size=16, color=INK, weight=400, extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" {extra}>{escape(str(value))}</text>'

def svg(width, height, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
<style>text{{font-family:Arial,Helvetica,sans-serif}}.mono{{font-family:Consolas,monospace}}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
{body}</svg>'''

def write(name, content):
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS/name).write_text(content, encoding='utf-8')

def still(content):
    return content.replace('</style>', '*{animation:none!important}</style>')

def build():
    hero=f'''<defs>
      <linearGradient id="paper" x2="1" y2="1"><stop stop-color="#f2f8ff"/><stop offset=".55" stop-color="#fcfcff"/><stop offset="1" stop-color="#f1faf8"/></linearGradient>
      <linearGradient id="ribbon"><stop stop-color="#b8d9fb"/><stop offset=".52" stop-color="#d3cef5"/><stop offset="1" stop-color="#c6ece4"/></linearGradient>
    </defs>
    <style>@keyframes drift{{50%{{transform:translate(9px,-5px)}}}}@keyframes tide{{50%{{transform:translateY(7px)}}}}.drift{{animation:drift 8s ease-in-out infinite}}.tide{{animation:tide 8s ease-in-out infinite}}</style>
    <rect width="1000" height="320" rx="22" fill="url(#paper)"/>
    <path d="M714 0H1000V123Q931 151 872 95T714 0Z" fill="#e4e7fb"/>
    <path class="tide" d="M0 260Q178 213 360 273T728 271T1000 258V320H0Z" fill="url(#ribbon)" opacity=".65"/>
    <path d="M0 286Q229 255 436 296T1000 279V320H0Z" fill="#fff" opacity=".55"/>
    <circle cx="90" cy="82" r="28" fill="#e4effd"/>
    {text(90,90,'af.',24,BLUE,700,'text-anchor="middle" letter-spacing="-1"')}
    {text(133,77,'HELLO, WORLD',12,MUTED,400,'letter-spacing="2.2" class="mono"')}
    {text(133,99,'A little curiosity. A lot of building.',13,MUTED)}
    {text(60,163,'Abdelali Ferhan',65,INK,700,'letter-spacing="-2.4"')}
    {text(63,206,'Full-stack developer',25,BLUE,600)}
    {text(63,237,'Web experiences  ·  Applied AI  ·  DevOps',16,MUTED)}
    <g class="drift" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <rect x="758" y="91" width="170" height="119" rx="14" fill="#fff" stroke="#cad8ed" stroke-width="1.5" transform="rotate(-7 843 150)"/>
      <path d="M766 117L921 98" stroke="#e5ecf7"/>
      <circle cx="779" cy="105" r="2.5" fill="#b3c6e9" stroke="none"/><circle cx="790" cy="104" r="2.5" fill="#c4b7e5" stroke="none"/><circle cx="801" cy="103" r="2.5" fill="#95cec4" stroke="none"/>
      <path d="M809 147l-16 17 19 12M876 138l19 12-15 18M852 133l-11 49" stroke="{BLUE}" stroke-width="4"/>
      <rect x="883" y="183" width="56" height="46" rx="12" fill="#e6f6f1" stroke="#b8dfd3"/>
      <path d="M898 205l8 7 16-18" stroke="{TEAL}" stroke-width="3"/>
    </g>
    <g stroke="#97afd6" stroke-width="1.5"><path d="M937 64v14M930 71h14M717 210v12M711 216h12"/></g>
    <circle cx="739" cy="85" r="3" fill="#9ac7c1"/><circle cx="966" cy="173" r="3" fill="#b8a6de"/>
    '''
    write('hero.svg',svg(1000,320,hero,'Abdelali Ferhan — Full-stack developer, applied AI and DevOps'))
    write('hero-static.svg',svg(1000,320,still(hero),'Abdelali Ferhan — Full-stack developer, applied AI and DevOps'))
    mobile=f'''<defs><linearGradient id="paper" x2="1" y2="1"><stop stop-color="#eff6ff"/><stop offset="1" stop-color="#f5f3fc"/></linearGradient></defs>
    <rect width="480" height="270" rx="18" fill="url(#paper)"/>
    <path d="M0 226Q130 189 262 230T480 218V270H0Z" fill="#cfe6ec" opacity=".6"/>
    <circle cx="42" cy="42" r="20" fill="#e1ebfc"/>{text(42,49,'af.',18,BLUE,700,'text-anchor="middle"')}
    {text(75,47,'HELLO, WORLD',11,MUTED,400,'letter-spacing="2"')}
    {text(24,104,'Abdelali',46,INK,700,'letter-spacing="-1.5"')}
    {text(24,152,'Ferhan',46,INK,700,'letter-spacing="-1.5"')}
    {text(24,190,'Full-stack developer',22,BLUE,600)}
    {text(24,218,'Web experiences · Applied AI · DevOps',13,MUTED)}
    <path d="M387 104l-16 16 16 16M423 104l16 16-16 16M411 96l-12 47" fill="none" stroke="#7b97d5" stroke-width="3" stroke-linecap="round"/>
    '''
    write('hero-mobile.svg',svg(480,270,mobile,'Abdelali Ferhan — Full-stack developer'))
    for name,label,width,icon in [('portfolio','Portfolio',150,'window'),('linkedin','LinkedIn',145,'in'),('email',"Let’s talk",145,'mail')]:
        fill='#386ad9' if name=='portfolio' else '#f4f7fc'
        color='#fff' if name=='portfolio' else BLUE
        body=f'<rect x=".75" y=".75" width="{width-1.5}" height="38.5" rx="19" fill="{fill}" stroke="{fill if name=="portfolio" else "#dce5f2"}" stroke-width="1.5"/>'
        if icon=='window': body+=f'<rect x="20" y="13" width="16" height="13" rx="2" fill="none" stroke="{color}" stroke-width="1.5"/><path d="M20 17h16" stroke="{color}"/>'
        elif icon=='in': body+=text(21,25,'in',16,color,700)
        else: body+=f'<rect x="19" y="13" width="17" height="13" rx="2" fill="none" stroke="{color}" stroke-width="1.5"/><path d="M20 14l7 6 8-6" fill="none" stroke="{color}" stroke-width="1.5"/>'
        body+=text(47,25,label,14,color,600)+text(width-22,24,'↗',14,color)
        write(f'link-{name}.svg',svg(width,40,body,label))
    intro=f'''<defs><linearGradient id="wash"><stop stop-color="#eef6ff"/><stop offset="1" stop-color="#f0eefb"/></linearGradient></defs>
    <ellipse cx="150" cy="129" rx="133" ry="108" fill="url(#wash)"/>
    <g fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="M29 183l120 48 128-54-123-46Z" fill="#e5ecf7" stroke="#c8d8ee"/>
      <path d="M65 70l132-24 12 105-133 24Z" fill="#fff" stroke="#91aed9" stroke-width="2"/>
      <path d="M69 89l132-24" stroke="#d5e2f2"/>
      <circle cx="80" cy="80" r="2" fill="#a4b9dc"/><circle cx="89" cy="78" r="2" fill="#c3b7dd"/>
      <path d="M91 110l26-5M91 122l48-8M91 134l35-6M91 146l57-10" stroke="#82a8df" stroke-width="3"/>
      <rect x="148" y="100" width="34" height="32" rx="5" fill="#e7f5f1" stroke="#c0e3d7"/>
      <path d="M157 116l6 5 11-14" stroke="{TEAL}" stroke-width="2"/>
      <path d="M138 164l-1 25M116 195l43-8M86 188l63 24 49-20-62-22Z" fill="#f6f8fc" stroke="#b2c8e4"/>
      <path d="M224 190v-36M222 169c-22-1-17-22-17-22s21 0 17 22ZM226 177c19-3 20-22 20-22s-23 2-20 22Z" fill="#b7ddd1" stroke="#82bbaa"/>
      <path d="M211 186h28l-4 24h-19Z" fill="#e5e0f3" stroke="#beb0d7"/>
      <path d="M231 61v14M224 68h14M42 121v10M37 126h10" stroke="#a0b6db"/>
    </g>'''
    write('workbench.svg',svg(300,250,intro,'An original illustration of a light, open developer workbench'))
    for i,(name,title,subtitle,color,pale,kind) in enumerate([
        ('ardmarket','ArdMarket','AI + AGRICULTURE',TEAL,'#ecf8f3','fields'),
        ('scaler','Microservice Scaler','CLOUD + INFRASTRUCTURE',BLUE,'#eef4ff','servers'),
        ('lasorder','LasOrder','WEB + CUSTOMER EXPERIENCE','#b87338','#fff6eb','qr'),
        ('learning','E-learning Platform','WEB + EDUCATION',PURPLE,'#f5f0fc','book')]):
        art=''
        if kind=='fields':
            for y in range(25,86,16): art+=f'<path d="M332 {y+20}Q361 {y-10} 412 {y+3}" fill="none" stroke="{color}" stroke-width="1.8"/>'
        elif kind=='servers':
            for x,y in [(328,45),(373,25),(373,72)]: art+=f'<rect x="{x}" y="{y}" width="36" height="27" rx="5" fill="white" stroke="{color}"/><circle cx="{x+8}" cy="{y+10}" r="2" fill="{color}"/><path d="M{x+16} {y+10}h12M{x+8} {y+19}h20" stroke="{color}"/>'
            art+=f'<path d="M364 58h4V39h5M368 58v27h5" fill="none" stroke="{color}"/>'
        elif kind=='qr':
            for x,y in [(333,28),(378,28),(333,73)]:art+=f'<rect x="{x}" y="{y}" width="27" height="27" rx="4" fill="none" stroke="{color}" stroke-width="2"/><rect x="{x+8}" y="{y+8}" width="11" height="11" rx="2" fill="{color}"/>'
            art+=f'<path d="M378 73h12v12h15v15h-27v-10" fill="none" stroke="{color}" stroke-width="4"/>'
        else:
            art+=f'<path d="M370 41Q348 26 326 37V93Q349 83 370 98Q391 83 413 93V37Q391 26 370 41V98M337 50l21 5M337 63l21 5M382 55l21-5M382 68l21-5" fill="none" stroke="{color}" stroke-width="1.8"/>'
        body=f'<rect x=".5" y=".5" width="439" height="129" rx="14" fill="{pale}" stroke="{pale}"/>'+text(22,35,subtitle,10,color,600,'letter-spacing="1.1"')+text(22,77,title,23,INK,700,'letter-spacing="-.5"')+text(22,105,f'0{i+1}  /  SELECTED PROJECT',9,MUTED,400,'letter-spacing="1"')+art
        write(f'project-{name}.svg',svg(440,130,body,title+' — '+subtitle))
    divider='<defs><linearGradient id="line"><stop stop-color="#d7e9f9"/><stop offset=".5" stop-color="#d8d0ee"/><stop offset="1" stop-color="#c8e9df"/></linearGradient></defs><rect y="11" width="1000" height="2" rx="1" fill="url(#line)"/>'
    write('divider.svg',svg(1000,24,divider,'Section divider'))
    footer=f'''<defs><linearGradient id="wash"><stop stop-color="#e9f4ff"/><stop offset=".55" stop-color="#f3effb"/><stop offset="1" stop-color="#eaf7f2"/></linearGradient></defs>
    <path d="M0 27Q200 0 430 26T1000 17V120H0Z" fill="url(#wash)"/>
    {text(500,70,'Thanks for stopping by.',27,INK,600,'text-anchor="middle" letter-spacing="-.5"')}
    {text(500,98,'Stay curious. Build something useful.',14,MUTED,400,'text-anchor="middle"')}
    '''
    write('footer.svg',svg(1000,120,footer,'Thanks for stopping by. Stay curious. Build something useful.'))
    print('Built original light-profile artwork.')

if __name__=='__main__':
    build()
