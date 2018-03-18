from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.animation import Animation

from connectfour import ConnectFour




### TO DO ###
# - Prevent touch during computation - Not done...

# - Make animation for fall of coins, improve grid aspect, add image for grid
# - Improve game setting popup appearance

# - Put it on Android



Builder.load_string('''
#:import Factory kivy.factory.Factory
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
            text: 'Start a new game'
            on_release: root.open_popup()
        Label:
            id: message
            text: ''

<MyPopup>:
    auto_dismiss: False
    title: 'Game settings'
    BoxLayout:
        orientation: 'vertical'
        
        BoxLayout:
            orientation: 'horizontal'
            Label:
                text: 'Choose difficulty: '
            Spinner:
                id: level_select
        
        BoxLayout:
            orientation: 'horizontal'
            Label:
                size_hint_x: 2.0
                text: 'Do you want to play first?'
            ToggleButton:
                text: 'Yes'
                group: 'who_start'
                state: 'down'
            ToggleButton:
                id: computer_starts
                text: 'No'
                group: 'who_start'
        
        Button:
            id: start
            text: 'Start a new game!'
            on_release: root.start_button()


''')


class MyGrid(Widget):

    
    def draw_tab(self, tab):
        """
        Draw a static image of the connect4, with coins placed according to tab.
        tab should be a numpy array with values 0,1,2
        """        
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
        
        self.clear_canvas()
        
        with self.canvas.after:
#            # Grid image
#            Color(*COLORS['blue'], mode='rgb')
#            Rectangle(pos=self.pos, size=self.size)
            Color(1.0,1.0,1.0, mode='rgb')
            Rectangle(source='test-transparency.png', pos=self.pos, size=self.size)
            
        with self.canvas:
            
            # Coins
            for row in range(tab.shape[0]):
                for col in range(tab.shape[1]):
                    color = COIN_COLORS[tab[row,col]]
                    Color(*COLORS[color], mode='rgb')
                    Ellipse(pos=(self.pos[0] + sq_size[0] * (col + (1-coin_ratio)/2),
                                 self.pos[1] + sq_size[1] * (row + (1-coin_ratio)/2)),
                            size=(i*coin_ratio for i in sq_size))
            
#        self.fall_anim(3,3,2)
            
    def fall_anim(self, row, col, player, NROW=6,NCOL=7):
        """
        Animation of a coin of player whose final position is determined by row and col.
        """
        COLORS = {'red': (0.83,0,0),
                  'yellow': (1, 0.8, 0),
                  'blue': (0, 0, 0.6),
                  'white': (1,1,1),
                  'grey': (0.88, 0.88, 0.92)}
        COIN_COLORS={0:'grey', 1:'red', 2:'yellow'}
        
        # Useful to find where to paint coins
        sq_size = (
            1.0 * self.size[0]/NCOL,
            1.0 * self.size[1]/NROW)
        coin_ratio = 0.8 # space used by a coin inside a square
        
        with self.canvas:
            
            color = COIN_COLORS[player]
            Color(*COLORS[color], mode='rgb')
            e = Ellipse(pos=(self.pos[0] + sq_size[0] * (col + (1-coin_ratio)/2),
                         self.pos[1] + sq_size[1] * (NROW + (1-coin_ratio)/2)),
                    size=(i*coin_ratio for i in sq_size))
        
        anim = Animation(pos=(self.pos[0] + sq_size[0] * (col + (1-coin_ratio)/2),
                              self.pos[1] + sq_size[1] * (row + (1-coin_ratio)/2)),
                         t='in_quad',
                         duration = (NROW-row)/6)
        anim.start(e)
        

    def clear_canvas(self):
        self.canvas.clear()
        self.canvas.after.clear()
        

class MyPopup(Popup):
    
    def __init__(self, levels, current_level, **kwargs):
        """
        Create the popup with a spinner with chosen levels
        """
        super(Popup, self).__init__(**kwargs)
                
        # Add diggiculty level to spinner
        spinner = self.ids['level_select']
        spinner.text = current_level
        spinner.values = levels
        
    def start_button(self):
        level = self.ids['level_select'].text
        computer_first = self.ids['computer_starts'].state == 'down'
        root.start_game(level, computer_first)
        self.dismiss()
        

class MyBox(BoxLayout):

    def __init__(self, **kwargs):
        super(MyBox, self).__init__(**kwargs)
        self.c4 = ConnectFour()

        self.block_touch = False
        
        # Bind touch on grid
        grid = self.ids['grid']
        grid.bind(on_touch_down=self.on_grid_touch)
        
        Clock.schedule_once(lambda dt: self.open_popup(), 0)
        

    def on_grid_touch(self, grid, touch):
        '''
        Deal with touch on grid.
        '''
                
        if grid.collide_point(*touch.pos) and not self.block_touch:
            # Click in the paint widget
            
            # Block touch
            self.block_touch = True
            # Find corresponding column
            NCOL = 7            
            col = int((touch.x-grid.pos[0])/grid.size[0] * NCOL)
                        
            c4 = self.c4
            message = self.ids['message']
            
            # Add coin
            if c4.get_state()==0 and c4.add_coin(col):
                self.refresh()
                self.check_game_end()
                
                if c4.get_state()==0:
                    # Computer plays
                    message.text = "Computer computing next move..."
                    Clock.schedule_once(lambda dt: self.computer_plays(), 0)
                    return True
            
            self.block_touch = False
    
    def unblock_touch(self):
        self.block_touch = False

    def check_game_end(self):
        """
        Check if game is finished. If finished, update label accordingly.
        """
        # Check if game is finished
        message = self.ids['message']
        state = self.c4.get_state()
        if state != 0:
            if state > 0:
                if self.computer_first:
                    state = 3 - state
                if state == 1:
                    message.text = 'You won!'
                else:
                    message.text = 'You lost!'
                    
            else:
                message.text = 'Game over, no one won.'
    
    
    def computer_plays(self):
        """
        Compute next move for computer. Update canvas and label accordingly.
        """
        c4 = self.c4
        message = self.ids['message']
        col = c4.get_next_col()
        c4.add_coin(col)
        self.refresh()
        message.text = f"Computer played in column {col}"
        self.check_game_end()
        
        # unblock touch
        Clock.schedule_once(lambda dt: self.unblock_touch(),0)
    
  
    def refresh(self, *args):
        """
        Draw current state of grid on canvas
        """
        grid_canvas = self.ids['grid']
        grid_canvas.clear_canvas()
        grid_canvas.draw_tab(tab=self.c4.grid)
        
        
    def start_game(self, level, computer_first):
        self.ids['message'].text = ''        
        self.c4.clear()
        self.c4.update_level(level)        
        self.computer_first = computer_first        
        self.refresh()
        
        if self.computer_first:
            # computer plays first
            Clock.schedule_once(lambda dt: self.computer_plays(), 0)
            

            
    def open_popup(self, *args):
        """
        Opens a popup to choose next game settings
        """
        levels = [k for k,v in self.c4.LEVELS]
        current_level = self.c4.level_name
                
        self.popup = MyPopup(levels, current_level)
        self.popup.open()


class ConnectFourApp(App):

    def build(self):
        global root
        root = MyBox()
        return root


if __name__ == '__main__':
    ConnectFourApp().run()


