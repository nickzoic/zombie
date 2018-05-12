"""
Composable components used in views

"""

events = ('onchange', 'onclick')


class Component:
    """Base class for components"""    
    pass


class Element(Component):
    """A component which renders as an HTML element"""

    children = []
    attributes = {}

    def __init__(self, tag, *args, **kwargs):
        self._tag = tag
        self.children = list(args)
        self.attributes = kwargs
    
    def render(self, view):

        return ''.join(
            [ "<%s" % self._tag ] +
            [ " %s=%s" % (k, repr(v)) for k, v in self.attributes.items() ] +
            [ ' %s=%s' % (e, repr(view.add_event(e, getattr(self,e)))) for e in events if hasattr(self,e) ] +
            [ '>' ] +
            [ c.render(view) for c in self.children ] +
            [ "</%s>" % self._tag ]
        )


class TextElement(Component):

    def __init__(self, text):
        self._text = text

    def render(self, view=None):
        return self._text  # XXX html escape this


class ChangeableElement(Element):

    _value = None

    def onchange(self, value):
        self._value = value


class TextField(ChangeableElement):

    def __init__(self, name=None, value='', *args, **kwargs):
        super().__init__('input', *args, type='text', **kwargs)
        if name: self.attributes['name'] = name
        if value: 
            self._value = value
            self.attributes['value'] = value


class ClickableElement(Element):

    def onclick(self):
        pass


class Button(ClickableElement):

    def __init__(self, label=None, *args, **kwargs):
        super().__init__('button', *args, **kwargs)
        if label is not None:
            self.children = [ TextElement(label) ]
   

class Form(Element):

    def __init__(self, *args, **kwargs):
        super().__init__('form', *args, **kwargs)

    def postinit(self):
        try:
            submit_button = [c for c in self.children[::-1] if isinstance(c, Button)][0]
        except IndexError:
            submit_button = Button('Submit')
            self.children.append(submit_button)
        submit_button.onclick = self.onsubmit

    def onsubmit(self, value=None):
        pass
