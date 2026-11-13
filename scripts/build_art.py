"""Original, editable vector artwork. No network, templates, or external assets."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
BG, PANEL, LINE, INK, MUTED, MINT = '#0b1514', '#101f1c', '#263c35', '#eef5ee', '#a3b8ac', '#bdff83'

def text(x, y, value, size=16, color=INK, weight=400, extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" {extra}>{escape(str(value))}</text>'

def svg(width, height, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
<style>text{{font-family:Arial,Helvetica,sans-serif}} .mono{{font-family:Consolas,monospace}} @media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
{body}</svg>'''

def write(name, content):
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / name).write_text(content, encoding='utf-8')

def build():
    hero = f'''<defs>
      <pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse"><path d="M 36 0 L 0 0 0 36" fill="none" stroke="{LINE}" stroke-width=".5"/></pattern>
      <radialGradient id="glow"><stop stop-color="#29472d"/><stop offset="1" stop-color="{BG}"/></radialGradient>
      <linearGradient id="cube" x2="1" y2="1"><stop stop-color="#c9ff98"/><stop offset="1" stop-color="#67b98e"/></linearGradient>
    </defs>
    <style>@keyframes orbit{{to{{transform:rotate(360deg)}}}}@keyframes breathe{{50%{{opacity:.3}}}}.orbit{{transform-origin:792px 207px;animation:orbit 24s linear infinite}}.reverse{{animation-direction:reverse;animation-duration:12s}}.pulse{{animation:breathe 4s ease-in-out infinite}}</style>
    <rect width="1000" height="430" rx="20" fill="{BG}"/>
    <circle cx="792" cy="207" r="207" fill="url(#glow)"/>
    <path d="M608 20H980V410H608Z" fill="url(#grid)" opacity=".6"/>
    <rect x=".5" y=".5" width="999" height="429" rx="20" fill="none" stroke="{LINE}"/>
    <rect x="38" y="31" width="34" height="34" rx="10" fill="{MINT}"/>
    {text(45,54,'af',20,BG,700)}{text(85,53,'ABDELALI FERHAN',13,INK,700,'letter-spacing="2"')}
    <circle cx="758" cy="49" r="4" fill="{MINT}" class="pulse"/>
    {text(772,53,'OPEN TO COLLABORATE',11,MUTED,400,'class="mono" letter-spacing="1"')}
    {text(38,113,'FULL-STACK SOFTWARE ENGINEER',12,MINT,400,'class="mono" letter-spacing="1.6"')}
    {text(35,180,'Thoughtful',60,INK,700,'letter-spacing="-2"')}
    {text(35,246,'interfaces.',60,INK,700,'letter-spacing="-2"')}
    {text(35,312,'Intelligent systems.',48,MINT,700,'letter-spacing="-1.8"')}
    {text(38,350,'From the first interaction to the services behind it.',16,MUTED)}
    <line x1="38" y1="378" x2="962" y2="378" stroke="{LINE}"/>
    {text(38,405,'WEB APPLICATIONS  /  AI  /  DEVOPS',11,MUTED,400,'class="mono" letter-spacing="1.4"')}
    {text(962,405,'@AbdouTrdFer',12,MINT,400,'class="mono" text-anchor="end"')}
    <circle cx="792" cy="207" r="131" fill="none" stroke="{LINE}"/>
    <circle cx="792" cy="207" r="97" fill="none" stroke="#3e5c46" stroke-dasharray="3 8"/>
    <g class="orbit"><ellipse cx="792" cy="207" rx="151" ry="58" fill="none" stroke="#92be87" stroke-width="1.5" transform="rotate(-33 792 207)"/><circle cx="919" cy="125" r="7" fill="{MINT}"/></g>
    <g class="orbit reverse"><ellipse cx="792" cy="207" rx="151" ry="58" fill="none" stroke="#588879" transform="rotate(38 792 207)"/><circle cx="671" cy="113" r="5" fill="#8acdcc"/></g>
    <path d="M792 142L853 177V247L792 282L731 247V177Z" fill="{PANEL}" stroke="{MINT}" stroke-width="1.5"/>
    <path d="M792 142L853 177L792 213L731 177Z" fill="url(#cube)"/>
    <path d="M792 213V282M731 177L792 213L853 177" fill="none" stroke="{MINT}" stroke-width="1.5"/>
    {text(748,236,'a',29,MINT,700)}{text(809,236,'f',29,MINT,700)}
    <rect x="687" y="324" width="210" height="26" rx="13" fill="{PANEL}" stroke="{LINE}"/>
    {text(792,341,'CURIOUS BY DEFAULT',10,MUTED,400,'text-anchor="middle" class="mono" letter-spacing="2"')}
    '''
    write('hero.svg',svg(1000,430,hero,'Abdelali Ferhan — Thoughtful interfaces. Intelligent systems.'))
    write('hero-static.svg',svg(1000,430,hero.replace('.orbit{','.orbit{animation:none!important;').replace('.pulse{','.pulse{animation:none!important;'),'Abdelali Ferhan — Full-stack software engineer'))
    process = f'<rect width="1000" height="152" rx="16" fill="{BG}"/><rect x=".5" y=".5" width="999" height="151" rx="16" fill="none" stroke="{LINE}"/>'
    process += '<style>@keyframes travel{to{stroke-dashoffset:-800}}.signal{animation:travel 8s linear infinite}</style>'
    process += f'<path d="M90 54H910" stroke="{LINE}" stroke-width="2"/><path class="signal" d="M90 54H910" stroke="{MINT}" stroke-width="2" stroke-dasharray="30 170"/>'
    for i,(label,sub) in enumerate([('Understand','Start with the problem'),('Design','Make the experience clear'),('Build','Connect the moving parts'),('Improve','Learn from what ships')]):
        x=128+i*248
        process+=f'<circle cx="{x}" cy="54" r="18" fill="{PANEL}" stroke="{MINT}"/>'+text(x,59,f'0{i+1}',12,MINT,400,'text-anchor="middle" class="mono"')+text(x,99,label,19,INK,700,'text-anchor="middle"')+text(x,125,sub,12,MUTED,400,'text-anchor="middle"')
    write('process.svg',svg(1000,152,process,'Understand, design, build, improve'))
    write('process-static.svg',svg(1000,152,process.replace('.signal{','.signal{animation:none!important;'),'Understand, design, build, improve'))
    for name,label,width in [('portfolio','VIEW PORTFOLIO  ↗',190),('linkedin','LINKEDIN  ↗',145),('email',"LET’S TALK  ↗",150)]:
        body=f'<rect x=".5" y=".5" width="{width-1}" height="35" rx="8" fill="{MINT if name=="portfolio" else PANEL}" stroke="{LINE}"/>'+text(width/2,23,label,11,BG if name=='portfolio' else INK,700,'text-anchor="middle" letter-spacing="1"')
        write(f'link-{name}.svg',svg(width,36,body,label))
    for i,(name,title,subtitle,color,kind) in enumerate([
        ('ardmarket','ArdMarket','AI MEETS AGRICULTURE',MINT,'fields'),
        ('scaler','Microservice Scaler','INFRASTRUCTURE THAT ADAPTS','#95d8d2','servers'),
        ('lasorder','LasOrder','FROM SCAN TO SERVICE','#f2c891','qr'),
        ('learning','E-learning Platform','A CLEARER PATH TO LEARNING','#c6b9f2','book')]):
        art=''
        if kind=='fields':
            for y in range(30,111,20): art+=f'<path d="M310 {y+36}Q345 {y-20} 425 {y+5}" fill="none" stroke="{color}" stroke-width="2"/>'
        elif kind=='servers':
            for x,y in [(310,40),(367,26),(367,81)]: art+=f'<rect x="{x}" y="{y}" width="44" height="34" rx="5" fill="none" stroke="{color}"/><circle cx="{x+10}" cy="{y+12}" r="3" fill="{color}"/><path d="M{x+19} {y+12}h16M{x+9} {y+24}h26" stroke="{color}"/>'
            art+=f'<path d="M354 57h6v-14h7M360 57v41h7" fill="none" stroke="{color}"/>'
        elif kind=='qr':
            for x,y in [(315,28),(368,28),(315,81)]:art+=f'<rect x="{x}" y="{y}" width="32" height="32" rx="4" fill="none" stroke="{color}" stroke-width="3"/><rect x="{x+9}" y="{y+9}" width="14" height="14" rx="2" fill="{color}"/>'
            art+=f'<path d="M368 81h14v14h18v18h-32v-12" fill="none" stroke="{color}" stroke-width="5"/>'
        else:
            art+=f'<path d="M357 43Q330 25 306 38V103Q332 90 357 108Q382 90 408 103V38Q381 25 357 43V108M318 54l25 5M318 68l25 5M371 59l25-5M371 73l25-5" fill="none" stroke="{color}" stroke-width="2"/>'
        body=f'<rect width="440" height="170" rx="12" fill="{BG}"/><path d="M290 0V170" stroke="{LINE}"/>'+text(22,29,f'0{i+1} / SELECTED WORK',10,color,400,'class="mono" letter-spacing="1"')+text(22,91,title,23,INK,700)+text(22,121,subtitle,9,MUTED,400,'class="mono" letter-spacing=".6"')+art
        write(f'project-{name}.svg',svg(440,170,body,title+' — '+subtitle))
    footer=f'<rect width="1000" height="90" rx="14" fill="{BG}"/><path d="M30 45H275M725 45H970" stroke="{LINE}"/>'+text(500,40,'KEEP LEARNING. KEEP BUILDING.',13,MINT,400,'text-anchor="middle" class="mono" letter-spacing="2"')+text(500,63,'Abdelali Ferhan / @AbdouTrdFer',11,MUTED,400,'text-anchor="middle"')
    write('footer.svg',svg(1000,90,footer,'Keep learning. Keep building.'))
    print('Built original SVG artwork.')

if __name__ == '__main__':
    build()
