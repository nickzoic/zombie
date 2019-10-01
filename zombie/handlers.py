"""
    Bottle handler for Zombie: uses plain old HTTP POST to send messages and
    the response contains messages going back the other way.

    The POST contains a large random session token, plus an event number and
    (optional) event parameter.  The response is a javascript snippet which
    is executed by the loader function.
"""

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
    """Returns a string containing a javascript function 'Z' which is used to
    transmit a message to the server.  'path' and 'session' are the backend
    handler path and session identifier.  The function then evaluates the 
    returned javascript code using 'new Function(...)()', allowing the zombie
    to update the browser state on return."""

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
""" % (repr(path), session)


def loader_html(path, session=""):
    """Wrap the loader_js content into a stub HTML page which is loaded first.
    Once the page is loaded the loader_js function 'Z' is run for the first time,
    and it's this which causes the rest of the page to load."""
    return """
        <!DOCTYPE html><html>
        <head><style></style><script>%s</script></head><body>
        <script>Z()</script><noscript>This site requires Javascript</noscript>
        </body></html>
    """ % loader_js(path, session)


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
            return loader_html(bottle.request.path, session_id)

        elif bottle.request.method == 'POST':
            session_id = bottle.request.params.get('s')
            try:
                view_obj = sessions[session_id]
            except KeyError:
                # pop a browser alert up, and then have the browser reload the page.
                return "alert('Session Expired'); window.location = " + repr(bottle.request.path)
    
            return view_obj.event(
                number = bottle.request.params.get('n', 0),
                value = bottle.request.params.get('v')
            )
        else:
            bottle.response = 405
            return "Method Not Allowed"

    return handler

