import bottle
import zombie


#class MyForm(zombie.Form):
#    name = zombie.TextField()
#    email = zombie.EmailField()
#    postcode = zombie.PostcodeField()

class MyView(zombie.View):

    def load(self, value=None):
        return self.set('body', zombie.Element('button', text="click me", onclick=self.clicky))

    def clicky(self, value=None):
        return self.set('body', zombie.Element('h1', text='thanks'))

bottle.route('/', ['GET', 'POST'], MyView().bottle_handler)
bottle.run(host='localhost', port=8080, reloader=True)
