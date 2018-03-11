from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.slider import Slider
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.lang import Builder

import numpy as np


from connectfour import ConnectFour


# TO DO
# Add possibility to choose:
# - who starts
# - level of computer

# Try to refresh screen sooner

# Make popup to:
# - Choose new game settings
# - Inform of game results


Builder.load_string('''
<MyBox>:
    id: box
    orientation: 'vertical'
    padding: [4,4,4,4]
    spacing: 4
    MyGrid:
        id: grid
        size_hint_y: 1

    BoxLayout:
        id: commands
        orientation: 'horizontal'
        spacing: 2
        size_hint_y: None
        height: '48dp'
        Button:
            id: start
            text: 'Start'
            size_hint_y: None
            height: '48dp'
            on_press: root.start_stop_action()
        Label:
            id: message
            text: 'Hello'
''')


class MyGrid(Widget):

    def on_touch_down(self, touch):
        """
        Get click and add/remove point from tab.
        """
        if self.collide_point(*touch.pos):
            # Click in the paint widget
            
            # Find corresponding column
            NCOL = 7            
            col = int((touch.x-self.pos[0])/self.size[0] * NCOL)
                        
            c4 = root.c4
            message = root.ids['message']
            
            # Add coin
            if c4.get_state()==0 and c4.add_coin(col):
                root.refresh()
                
                if c4.get_state()==0:
                    # Computer plays
                    message.text = "Computer computing next move..."
                    print("Computer computing next move...")
                    col = c4.get_next_col()
                    print(f"Computer plays in column {col}")
                    c4.add_coin(col)
                    root.refresh()
                    message.text = f"Computer played in column {col}"
            
            # Check if game is finished
            state = c4.get_state()
            if state != 0:
                if state > 0:
                    if root.computer_first:
                        state = 3 - state
                    if state == 1:
                        message.text = 'You won!'
                    else:
                        message.text = 'You lost!'
                        
                else:
                    message.text = 'Game over, no one won.'
            
            
#            print(f'self.pos[0]: {self.pos[0]}')
#            print(f'touch.x: {touch.x}')
#            print(f'self.size[0]: {self.size[0]}')
#            print(f'(touch.x-self.pos[0])/self.size[0] * NCOL: {(touch.x-self.pos[0])/self.size[0] * NCOL}')
#            print(f'col: {col}')

    def draw_tab(self, tab):
        """
        tab should be a numpy array with values 0,1,2
        """
        
#        tab = np.zeros((6,7), dtype=int)
#        tab[0,2]=1
#        tab[1,2]=2
        
        # RGB colors
        COLORS = {'red': (0.83,0,0),
                  'yellow': (1, 0.8, 0),
                  'blue': (0, 0, 0.6),
                  'white': (1,1,1),
                  'grey': (0.88, 0.88, 0.92)}
        COIN_COLORS={0:'grey', 1:'red', 2:'yellow'}
        
        # Useful to find where to paint coins
        sq_size = (
            1.0 * self.size[0]/tab.shape[1],
            1.0 * self.size[1]/tab.shape[0])
        coin_ratio = 0.8 # space used by a coin inside a square
        
        with self.canvas:
            # Background
            Color(*COLORS['blue'], mode='rgb')
            Rectangle(pos=self.pos, size=self.size)
            
            # Coins
            for row in range(tab.shape[0]):
                for col in range(tab.shape[1]):
                    color = COIN_COLORS[tab[row,col]]
                    Color(*COLORS[color], mode='rgb')
                    Ellipse(pos=(self.pos[0] + sq_size[0] * (col + (1-coin_ratio)/2),
                                 self.pos[1] + sq_size[1] * (row + (1-coin_ratio)/2)),
                            size=(i*coin_ratio for i in sq_size))

    def clear_canvas(self):
        self.canvas.clear()
        

class MyBox(BoxLayout):

    def __init__(self, **kwargs):
        super(MyBox, self).__init__(**kwargs)
        self.c4 = ConnectFour()
        self.refresh()
        
        
        self.cnt = 0
        
#        fps = 1
#        self.event = Clock.schedule_interval(self.refresh, 1.0/fps)
#        self.golife = Golife()
#
#        pattern_names = Golife.PATTERNS.keys()
#        spinner = self.ids['pattern_select']
#        spinner.text = pattern_names[0]
#        spinner.values = pattern_names
#        spinner.bind(text=self.set_pattern)
#        self.set_pattern(spinner, spinner.text)
#
#        self.refresh()
        
  
    def refresh(self, *args):
        """
        Draw current state of grid on canvas
        """
        grid_canvas = self.ids['grid']
        grid_canvas.clear_canvas()
        grid_canvas.draw_tab(tab=self.c4.grid)
                

    def start_stop_action(self):
        """
        Deals with the start/stop button
        """
        self.c4.clear()
        self.computer_first = True
        
        if self.computer_first:
            # If computer plays first
            col = self.c4.get_next_col()
            self.c4.add_coin(col)
            
        self.refresh()
            
        



class ConnectFourApp(App):

    def build(self):
        global root
        root = MyBox()
        return root


if __name__ == '__main__':
    ConnectFourApp().run()


