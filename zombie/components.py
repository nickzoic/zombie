"""
Composable components used in views

"""

import html
import copy

events = ('onchange', 'onclick')


class Component:
    """Base class for components"""    
 
    _id_counter=0

    def __new__(cls, *args, **kwargs):
        """If the class has declared children, pre-initialize the instance
        with *copies* of the children, so that they can be mutable.  This
        lets you declare forms with fields conveniently in the class 
        definition without having to have a more complicated factory-like
        setup"""
        obj = object.__new__(cls)
        obj._children = []
        Component._id_counter += 1
        obj._attributes = { "id": Component._id_counter }

        for child_name, cls_child in cls.__dict__.items():
            if isinstance(cls_child, Component):
                obj_child = copy.deepcopy(cls_child)
                setattr(obj, child_name, obj_child)
                obj_child._attributes.setdefault('name', child_name)
                obj._children.append(obj_child)

        return obj


class Element(Component):
    """A component which renders as an HTML element, and can contain other
    Components."""

    def __init__(self, tag, *args, **kwargs):
        self._tag = tag
        self._children += list(args)
        self._attributes.update(kwargs)
        self._attributes.update([(e, "return Z(this.id,this.value)") for e in events if hasattr(self, e)])

    def recv(self, event):
        if event.target:
            for target, message in self._children[event.target[0]].recv(event):
                yield ([event.target[0]] + target, message)

    def identities(self):
        yield (self._attributes['id'], self.recv)
        for c in self._children:
            yield from c.identities()

    def render(self):
        return ''.join(
            [ "<%s" % self._tag ] +
            [ ' %s="%s"' % (k, html.escape(str(v), quote=True)) for k, v in self._attributes.items() ] +
            [ '>' ] +
            [ c.render() for c in self._children ] +
            [ "</%s>\n" % self._tag ]
        )


class TextElement(Component):
    """A piece of text in HTML: not an Element itself but contained by Elements"""

    def __init__(self, text):
        self._text = text

    def render(self, view=None):
        return html.escape(self._text, quote=False)

    def recv(self, event):
        pass

    def identities(self):
        yield (self._attributes['id'], self.recv)

class ChangeableElement(Element):

    _value = None

    def onchange(self, value):
        self._value = value


class TextField(ChangeableElement):

    def __init__(self, name=None, value='', *args, **kwargs):
        super().__init__('input', *args, type='text', **kwargs)
        if name: self._attributes['name'] = name
        if value: 
            self._value = value
            self._attributes['value'] = value


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
            self._children = [ TextElement(label) ]
   

class Form(Element):

    def __init__(self, *args, **kwargs):
        super().__init__('form', *args, **kwargs)

        try:
            submit_button = [c for c in self._children[::-1] if isinstance(c, Button)][0]
        except IndexError:
            submit_button = Button('Submit')
            self._children.append(submit_button)
        submit_button.onclick = self.onsubmit

    def onsubmit(self, value=None):
        pass
