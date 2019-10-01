"""
Zombie pages and their behaviours.
"""

class View:

    def __init__(self):
        self.events = { 0: self.load }

    def register(self, event_id, event_handler):
        self.events[int(event_id)] = event_handler

    def event(self, number=None, value=None):
        print("View.event %s %s" % (number, repr(value)))
        return self.events[int(number)](value)

    def set(self, selector, element):
        if hasattr(element, 'onclick'): self.events[id(element)] = element.onclick

        if selector.startswith('#'):
            getter = "getElementById(%s)" % repr(selector[1:])
        elif selector.startswith('.'):
            getter = "getElementsByClassName(%s)[0]" % repr(selector[1:])
        else:
            getter = "getElementsByTagName(%s)[0]" % repr(selector)

        return "document.%s.innerHTML = %s" % (getter, repr(element.render(self)))


