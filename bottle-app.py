import bottle
import zombie


class MyForm(zombie.components.Form):

    # need a better way to do styles
    style = zombie.components.Element('style', zombie.components.TextElement("input { border: solid green } input.required { border: solid orange } input.invalid { border: solid red }"))

    name = zombie.components.TextField(required=True)
    email = zombie.components.RegexTextField(regex=r'.*@.*\..*', required=True)
    postcode = zombie.components.TextField(regex=r'\d{4}', required=False)

    def onsubmit(self, value=None):
        return self._onsubmit()


class MyView(zombie.views.View):

    def load(self, value=None):
        self.my_form = MyForm()
        self.my_form._onsubmit = self.clicky
        return self.set('body', self.my_form)

    def clicky(self, value=None):
        print("MyView %s Form %s Name %s" % (self, self.my_form, self.my_form.name))
        text = "Thanks %s <%s> of %s" % (
                self.my_form.name.value(),
                self.my_form.email.value(),
                self.my_form.postcode.value()
        )
        return self.set('body', zombie.components.TextElement(text=text))


bottle.route('/', ['GET', 'POST'], zombie.handlers.bottle_handler(MyView))
bottle.run(host='localhost', port=8080, reloader=True)
