try:
    import secrets
    def get_token():
        """Get a 80-bit random token as a hex string"""
        return secrets.token_hex(20)
except ImportError:
    def get_token():
        """Get a 80-bit random token as a hex string"""
        from Crypto.Random.random import rand_bits
        return "%020x" % rand_bits(80)


def loader_js(path, session=""):
    return """
  function Z (n, v) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function () {
      if (xhr.responseText) (new Function('Z', xhr.responseText))(Z);
    };
    xhr.open("POST", %s);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send('s=%s&n=' + (n || 0) + '&v=' + encodeURIComponent(v || ''));
    return false;
  }
  Z();
""" % (repr(path), session)

loader_html = "<!DOCTYPE html><html><head><style></style><script>%s</script></head><body></body></html>"

# XXX need a session eviction policy ... probably just some kind of timeout
# XXX this is very simple and doesn't allow for multiple BFF servers: a mechanism
#     to pin a session to a BFF server would be nice.

sessions = {}

def bottle_handler(view_class):
    import bottle

    def handler():
        if bottle.request.method == 'GET':
            session_id = get_token()
            sessions[session_id] = view_class()
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

    return handler

