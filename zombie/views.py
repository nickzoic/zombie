"""
Zombie pages and their behaviours.
"""

class View:

    def __init__(self):
        self.events = [ self.load ]

    def add_event(self, name, callback):
        self.events.append(callback)
        return "return Z(%s,this.value)" % (len(self.events) - 1)

    def event(self, number=None, value=None):
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


