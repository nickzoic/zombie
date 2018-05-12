import bottle
import zombie

class MyForm(zombie.components.Form):

    def __init__(self, onsubmit):
        super().__init__()
        self.children = [
            zombie.components.TextField('name'),
            zombie.components.TextField('email'),
            zombie.components.TextField('postcode')
        ]
        self.postinit()
        self._onsubmit = onsubmit

    def onsubmit(self, value=None):
        return self._onsubmit()


class MyView(zombie.views.View):

    def load(self, value=None):
        my_form = MyForm(self.clicky)
        return self.set('body', my_form)

    def clicky(self, value=None):
        return self.set('body', zombie.components.TextElement(text='thanks'))


bottle.route('/', ['GET', 'POST'], zombie.handlers.bottle_handler(MyView))
bottle.run(host='localhost', port=8080, reloader=True)
