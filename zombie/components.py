"""
Composable components used in views

"""

class Element:

    def __init__(self, tag, text, onclick=None, onchange=None):
        self._tag = tag
        self._text = text
        self._onclick = onclick

    def to_html(self):
        return "<%s%s>%s</%s>" % (
            self._tag,
            ' onclick="Z(%s)"' % id(self) if self._onclick else '',
            self._text,
            self._tag
        )

