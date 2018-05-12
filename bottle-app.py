import bottle
import zombie

#class MyForm(zombie.Form):
#    name = zombie.TextField()
#    email = zombie.EmailField()
#    postcode = zombie.PostcodeField()

class MyView(zombie.views.View):

    def load(self, value=None):
        return self.set('body', zombie.components.Element('button', text="click me", onclick=self.clicky))

    def clicky(self, value=None):
        return self.set('body', zombie.components.Element('h1', text='thanks'))

bottle.route('/', ['GET', 'POST'], zombie.handlers.bottle_handler(MyView))
bottle.run(host='localhost', port=8080, reloader=True)
