try:
    from secrets import token_hex
except ImportError:
    def token_hex(n_digits):
        """Polyfill for Python 3.6's secrets.token_hex"""
        from Crypto.Random.random import rand_bits
        return ("%%0%dx" % n_digits) % rand_bits(8 * n_digits)

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

def bottle_handler(view_class):
    import bottle
    
    def handler():
        if bottle.request.method == 'GET':
            session_id = token_hex(16)
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

