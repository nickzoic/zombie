import secrets

# XXX use a less terrible way of building the POST parameters

def loader_js(path, session=""):
    return """
  function Z (n, v) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function () {
      (new Function('Z', xhr.responseText))(Z);
    };
    xhr.open("POST", %s);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send('s=%s&n='+ (n || 0) + '&v=' + (v || ''));
  }
  Z();
""" % (repr(path), session)

loader_html = "<!DOCTYPE html><html><head><script>%s</script></head><body></body></html>"

# XXX need a session eviction policy ... probably just some kind of timeout

sessions = {}

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


class View:

    # XXX this should probably be a separate zombie.bottle.handler 
    # XXX this is very simple and doesn't allow for multiple BFF servers: a mechanism
    #     to pin a session to a BFF server would be nice.

    @classmethod
    def bottle_handler(cls):
        import bottle
        global sessions
        if bottle.request.method == 'GET':
            session_id = secrets.token_hex(16)
            sessions[session_id] = cls()
            return loader_html % (loader_js(bottle.request.path, session_id))
        elif bottle.request.method == 'POST':
            session_id = bottle.request.params.get('s')
            try:
                view_obj = sessions[session_id]
            except KeyError:
                return "alert('Session Expired'); window.url = " + repr(bottle.request.path)

            return view_obj.event(
                number = bottle.request.params.get('n', 0),
                value = bottle.request.params.get('v')
            )
        else:
            bottle.response = 405
            return "Method Not Allowed"

    def __init__(self):
        self.events = { 0 : self.load }

    def event(self, number=None, value=None):
        return self.events[int(number)](value)

    def set(self, selector, element):
        if element._onclick: self.events[id(element)] = element._onclick

        if selector.startswith('#'):
            getter = "getElementById(%s)" % repr(selector[1:])
        elif selector.startswith('.'):
            getter = "getElementsByClassName(%s)[0]" % repr(selector[1:])
        else:
            getter = "getElementsByTagName(%s)[0]" % repr(selector)

        return "document.%s.innerHTML = %s" % (getter, repr(element.to_html()))


