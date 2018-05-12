"""
Zombie pages and their behaviours.
"""

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


