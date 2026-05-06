"""
Composable components used in views

"""

import html
import copy

# XXX have to somehow differentiate between local events (which just do javascripty
# things on the frontend) and remote events which call the Z() function


events = ('onchange', 'onclick')


class Component:
    """Base class for components"""    
  
    parent = None
    children = []

    _id_counter = 0

    def __new__(cls, *args, **kwargs):
        """If the class has declared children, pre-initialize the instance
        with *copies* of the children, so that they can be mutable.  This
        lets you declare forms with fields conveniently in the class 
        definition without having to have a more complicated factory-like
        setup"""
        obj = object.__new__(cls)
        print("Creating %s %s" % (cls.__name__, obj))
        obj._children = []
        Component._id_counter += 1
        obj._attributes = { "id": Component._id_counter }

        for child_name, cls_child in cls.__dict__.items():
            if isinstance(cls_child, Component):
                obj_child = copy.deepcopy(cls_child)
                obj_child.parent = obj
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


class ScriptElement(Component):
    def __init__(self, code):
        self._code = code

    def render(self, view):
        self._name = view.add_function


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

class ActiveElement(Element):
    """A component which can be rendered as HTML and can receive events."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Component._id_counter += 1
        self._attributes['id'] = str(Component._id_counter)
        

class ChangeableElement(ActiveElement):

    _value = None
    inputs = []

    def __init__(self, *args, **kwargs):
        self.required = False
        if 'required' in kwargs:
            if kwargs['required']: self.required = True 
            del kwargs['required']
        super().__init__(*args, **kwargs)
        if self.required:
            self.attributes['oninput'] = 'this.classList.toggle("required", !this.value)'
            self.attributes['onfocus'] = 'this.classList.toggle("required", !this.value)'

    def onchange(self, value):
        self._value = value

    def value(self):
        return self._value


class TextField(ChangeableElement):

    def __init__(self, name=None, value='', *args, **kwargs):
        super().__init__('input', *args, type='text', **kwargs)
        if name: self._attributes['name'] = name
        if value: 
            self._value = value
            self._attributes['value'] = value


class RegexTextField(TextField):

    def __init__(self, name=None, regex=None, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        if regex:
            self._regex = regex
            if self.required:

                self.attributes['oninput'] += ';this.classList.toggle("invalid", this.value.length > 0 && !this.value.match(%s))' % repr(regex)
                self.attributes['onfocus'] += ';this.classList.toggle("invalid", this.value.length > 0 && !this.value.match(%s))' % repr(regex)
            else:
                self.attributes['oninput'] = 'this.classList.toggle("invalid", !this.value.match(%s))' % repr(regex)
                self.attributes['onfocus'] = 'this.classList.toggle("invalid", !this.value.match(%s))' % repr(regex)


class SlugField(TextField):
    
    def onchange(self, value):
        new_value = re.sub("[^A-Za-z0-9]+", "")
        super().onchange(self, new_value)


class ClickableElement(ActiveElement):

    def onclick(self):
        pass


class Button(ClickableElement):

    def __init__(self, label=None, *args, **kwargs):
        super().__init__('button', *args, **kwargs)
        if label is not None:
            self._children = [ TextElement(label) ]
   

class Form(ActiveElement):

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
