from kivy.app import App
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.animation import Animation


Builder.load_string('''
<MyImage>:
    source: 'test-transparency.png'

''')


class MyImage(Image):
    
    def on_touch_down(self, touch):
        self.draw_rectangle()
    
    def draw_rectangle(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.3,0.5,0.1, mode='rgb')
            r = Rectangle(pos=(0,self.pos[1]+self.size[1]), size=(int(i/7) for i in self.size))
            Color(1.0,1.0,1.0, mode='rgb')
            Rectangle(source='test-transparency.png', pos=self.pos, size=self.size)
            
            anim = Animation(pos=(0,0), t='in_quad')
            anim.start(r)
#            r.pos = (r.pos[0]+240, 0)

class ConnectFourApp(App):

    def build(self):
        return MyImage()


if __name__ == '__main__':
    ConnectFourApp().run()


