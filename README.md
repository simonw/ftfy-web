# ftfy-web

A simple web wrapper around [Rob Speer](https://twitter.com/r_speer)'s [FTFY Python library](https://github.com/LuminosoInsight/python-ftfy). Paste in some broken unicode text and it will tell you how to fix it!

Try it out at https://ftfy.now.sh/

The tool outputs Python code to fix the input text, for example:

    s = 'Iggy Pop (nÃƒÂ© Jim Osterberg)'
    s = s.encode('sloppy-windows-1252')
    s = s.decode('utf-8')
    s = s.encode('latin-1')
    s = s.decode('utf-8')

In some cases it will output additional functions, for example:

    s = "Direzione Pd, ok â\x80\x9csenza modifiche\x94 all'Italicum."
    s = s.encode('latin-1')
    s = s.decode('windows-1252')
    s = fix_partial_utf8_punct_in_1252(s)

The implementation of those functions can be found [in the python-ftfy/fixes.py module](https://github.com/LuminosoInsight/python-ftfy/blob/bdc6f2211195e70ce38b52fefa522a007b04406e/ftfy/fixes.py#L581).
