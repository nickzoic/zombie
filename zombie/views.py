"""
Zombie pages and their behaviours.
"""

class View:

    def __init__(self):
        self.events = { 0: self.load }

    def load(self):
        pass

    def event(self, number=0, value=None):
        return self.events[int(number)](value)

    def set(self, selector, element):
        self.events.update(element.identities())
        #if hasattr(element, 'onclick'): self.events[id(element)] = element.onclick

        if selector.startswith('#'):
            getter = "getElementById(%s)" % repr(selector[1:])
        elif selector.startswith('.'):
            getter = "getElementsByClassName(%s)[0]" % repr(selector[1:])
        else:
            getter = "getElementsByTagName(%s)[0]" % repr(selector)

        return "document.%s.innerHTML = %s" % (getter, repr(element.render()))


