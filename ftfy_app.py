from sanic import Sanic
from sanic import response
from html import escape
import json
from urllib.parse import urlencode
from ftfy.fixes import fix_encoding_and_explain

EXAMPLES = [
    "He's Justinâ\x9d¤",
    'Le Schtroumpf Docteur conseille g√¢teaux et baies schtroumpfantes pour un '
    'r√©gime √©quilibr√©.',
    'âœ” No problems',
    'РґРѕСЂРѕРіРµ Р\x98Р·-РїРѕРґ #С„СѓС‚Р±РѕР»',
    '\x84Handwerk bringt dich überall hin\x93: Von der YOU bis nach Monaco',
    'Hi guys í ½í¸\x8d',
    'hihi RT username: â\x98ºí ½í¸\x98',
    'Beta Haber: HÄ±rsÄ±zÄ± BÃ¼yÃ¼ Korkuttu',
    'Р С—РЎР‚Р С‘РЎРЏРЎвЂљР Р…Р С•РЎРѓРЎвЂљР С‘. РІСњВ¤',
    'Kayanya laptopku error deh, soalnya tiap mau ngetik deket-deket kamu font yg '
    'keluar selalu Times New Ã¢â‚¬Å“ RomanceÃ¢â‚¬Â\x9d.',
    'Iggy Pop (nÃƒÂ© Jim Osterberg)',
    "Direzione Pd, ok â\x80\x9csenza modifiche\x94 all'Italicum.",
    "selamat berpuasa sob (Ã\xa0Â¸â€¡'ÃŒâ‚¬Ã¢Å’Â£'ÃŒÂ\x81)Ã\xa0Â¸â€¡",
    'The Mona Lisa doesnÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢t have eyebrows.',
    '#╨┐╤Ç╨░╨▓╨╕╨╗╤î╨╜╨╛╨╡╨┐╨╕╤é╨░╨╜╨╕╨╡',
    "LiĂ¨ge Avenue de l'HĂ´pital",
    'It was namedÂ â€žscarsÂ´ stonesâ€ś after the rock-climbers who got hurt '
    'while climbing on it.',
    'vedere Ă®nceĹŁoĹźatÄ\x83',
    'NapĂ\xadĹˇte nĂˇm !',
    'It was namedÂ\xa0â\x80\x9escarsÂ´ stonesâ\x80\x9c after the rock-climbers '
    'who got hurt while climbing on it.',
    'Arsenal v Wolfsburg: pre-season friendly â\x80â\x80\x9c live!',
    'Ã¢â€\x9dâ€™(Ã¢Å’Â£Ã‹â€ºÃ¢Å’Â£)Ã¢â€\x9dÅ½',
    'Ã¢â€�â€™(Ã¢Å’Â£Ã‹â€ºÃ¢Å’Â£)Ã¢â€�Å½',
    'I just figured out how to tweet emojis! â\x9a½í\xa0½í¸\x80í\xa0½í¸\x81í\xa0'
    '½í¸\x82í\xa0½í¸\x86í\xa0½í¸\x8eí\xa0½í¸\x8eí\xa0½í¸\x8eí\xa0½í¸\x8e'
]


INDEX = '''
<html>
<head>
    <title>ftfy - fix unicode that's broken in various ways</title>
<style>
body {{font-family: Helvetica}}
textarea {{width: 50%; height: 5em}}
</style>
</head>
<body>
<h1>ftfy - fix unicode that's broken in various ways</h1>
<p>Paste in some unicode text that appears to be broken and this tool will use the <a href="https://github.com/LuminosoInsight/python-ftfy">ftfy Python library</a> to try and fix it.</p>
<form action="/">
    <p>
        <textarea name="s" rows="3" cols="30">{s}</textarea>
    </p>
    <p>
        <input type="submit" value="Figure out encoding errors">
    </p>
</form>
<pre>{steps}</pre>
{output}
<h3>Examples</h3>
{examples}
<p style="font-size: 0.7em">Web app <a href="https://github.com/simonw/ftfy-web">source code on GitHub</a></p>
</html>
'''

examples = ['<ul>']
for example in EXAMPLES:
    steps = fix_encoding_and_explain(example)[1]
    if steps:
        examples.append('<li><a href="?{}">{}</a></li>'.format(
            urlencode({'s': example}), escape(example)
        ))
examples.append('</ul>')


app = Sanic(__name__)


def steps_to_python(s, steps):
    python = ['s = {}'.format(repr(s))]
    lines = []
    has_sloppy = False
    extra_imports = set()
    for method, encoding, _ in steps:
        if method == 'transcode':
            extra_imports.add(encoding)
            line = 's = {}(s)'.format(encoding)
        else:
            if encoding.startswith('sloppy'):
                has_sloppy = True
            line = 's = s.{}({})'.format(method, repr(encoding))
        lines.append(line)
    python = []
    if has_sloppy:
        python.append('import ftfy.bad_codecs  # enables sloppy- codecs')
    for extra in extra_imports:
        python.append('from ftfy.fixes import {}'.format(extra))
    python.append('s = {}'.format(repr(s)))
    return '\n'.join(python + lines + ['print(s)'])


@app.route('/')
async def handle_request(request):
    s = request.args.getlist('s')
    if s:
        s = s[0].strip()
        fixed, steps = fix_encoding_and_explain(s)
        return response.html(INDEX.format(
            output='<textarea>{}</textarea>'.format(escape(fixed)),
            steps=escape(steps_to_python(s, steps)),
            s=escape(s),
            examples='\n'.join(examples),
        ))
    else:
        return response.html(INDEX.format(
            output='',
            s='',
            steps='',
            examples='\n'.join(examples),
        ))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8006)
