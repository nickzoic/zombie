import bottle
import zombie


class MyForm(zombie.components.Form):

    style = zombie.components.Element('style', zombie.components.TextElement(".required { border: solid orange } .valid { border: solid green }"))

    name = zombie.components.TextField(required=True)
    email = zombie.components.RegexTextField(regex=r'.*@.*\..*', required=True)
    postcode = zombie.components.TextField()

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
