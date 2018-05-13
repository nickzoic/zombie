"""
Composable components used in views

"""

import html

events = ('onchange', 'onclick')


class Component:
    """Base class for components"""    
   
    children = []

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.children = cls.children[:]
        for n, c in cls.__dict__.items():
            if isinstance(c, Component):
                c.attributes['name'] = n
                obj.children.append(c)
        return obj


class Element(Component):
    """A component which renders as an HTML element"""

    attributes = {}

    def __init__(self, tag, *args, **kwargs):
        self._tag = tag
        self.children += list(args)
        self.attributes = kwargs
    
    def render(self, view):
        # XXX calling add_event hidden away in there isn't cool.
        return ''.join(
            [ "<%s" % self._tag ] +
            [ ' %s="%s"' % (k, html.escape(v, quote=True))
                for k, v in self.attributes.items() ] +
            [ ' %s="%s"' % (e, html.escape((view.add_event(e, getattr(self,e))), quote=True))
                for e in events if hasattr(self,e) ] +
            [ '>' ] +
            [ c.render(view) for c in self.children ] +
            [ "</%s>\n" % self._tag ]
        )


class TextElement(Component):

    def __init__(self, text):
        self._text = text

    def render(self, view=None):
        return html.escape(self._text, quote=False)


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


class SlugField(TextField):
    
    def onchange(self, value):
        new_value = re.sub("[^A-Za-z0-9]+", "")
        super().onchange(self, new_value)


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

        try:
            submit_button = [c for c in self.children[::-1] if isinstance(c, Button)][0]
        except IndexError:
            submit_button = Button('Submit')
            self.children.append(submit_button)
        submit_button.onclick = self.onsubmit

    def onsubmit(self, value=None):
        pass
