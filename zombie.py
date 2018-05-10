
loader_js = """
  function Z (r) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function () {
      (new Function('Z', xhr.responseText))(Z);
    };
    xhr.open("POST", %s);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send('e='+ (r || 0));
  }
  Z();
"""

loader_html = "<!DOCTYPE html><html><head><script>%s</script></head><body></body></html>"


class Element:

    def __init__(self, tag, text, onclick=None):
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


class View:

    def __init__(self):
        self.events = { 0 : self.load }

    def bottle_handler(self):
        import bottle
        if bottle.request.method == 'GET':
            return loader_html % (loader_js % repr(bottle.request.path))
        elif bottle.request.method == 'POST':
            en = int(bottle.request.params.get('e', 0))
            return self.events.get(en)()

    def set(self, selector, element):
        if element._onclick: self.events[id(element)] = element._onclick

        if selector.startswith('#'):
            getter = "getElementById(%s)" % repr(selector[1:])
        elif selector.startswith('.'):
            getter = "getElementsByClassName(%s)[0]" % repr(selector[1:])
        else:
            getter = "getElementsByTagName(%s)[0]" % repr(selector)

        return "document.%s.innerHTML = %s" % (getter, repr(element.to_html()))


