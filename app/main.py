__version__ = '1.0.0'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.animation import Animation

from connectfour import ConnectFour
from get_image_size import get_image_size # get image size with minimal dependencies

Builder.load_string('''
#:import Factory kivy.factory.Factory
<MyBox>:
    id: box
    orientation: 'vertical'
    padding: [4,4,4,4]
    spacing: 4
    AnchorLayout:
        id: grid_container
        anchor_x: 'center'
        anchor_y: 'center'
        MyGrid:
            id: grid
            size_hint_x: 0.7
    BoxLayout:
        id: commands
        orientation: 'horizontal'
        spacing: 2
        size_hint_y: None
        height: '48dp'
        Button:
            text: 'Start a new game'
            on_release: root.open_popup()
            size_hint_x: 0.3
        Label:
            id: message
            text: ''
            size_hint_x: 0.7

<MyPopup>:
    auto_dismiss: False
    title: 'Game settings'
    size_hint: (0.7,0.5)
    BoxLayout:
        orientation: 'vertical'
        
        BoxLayout:
            orientation: 'horizontal'
            Label:
                size_hint_x: 2.0
                text: 'Choose difficulty: '
            Spinner:
                id: level_select
        
        BoxLayout:
            orientation: 'horizontal'
            Label:
                size_hint_x: 2.0
                text: 'Do you want to play first?'
            ToggleButton:
                size_hint_x: 0.5
                text: 'Yes'
                group: 'who_start'
                state: 'down'
            ToggleButton:
                size_hint_x: 0.5
                id: computer_starts
                text: 'No'
                group: 'who_start'
        
        Button:
            id: start
            text: 'Start a new game!'
            on_release: root.start_button()

<EndPopup>:
    auto_dismiss: False
    title: ''
    size_hint: (0.4,0.3)
    BoxLayout:
        orientation: 'vertical'
        Label:
            id: message
        Button:
            id: start
            text: 'Start a new game!'
            on_release: root.start_button()
''')


GRID_IMAGE_PATH = 'grid.png'
image_size = get_image_size(GRID_IMAGE_PATH)
IMAGE_RATIO = image_size[0] / image_size[1]

class MyGrid(Widget):

    
    def draw_tab(self, tab):
        """
        Draw a static image of the connect4, with coins placed according to tab.
        tab should be a numpy array with values 0,1,2
        """        
        # RGB colors
        COLORS = {
                # 'red': (0.83,0,0),
                'red': (0.66,0.07,0.07),
                  'yellow': (1, 0.8, 0),
                  'blue': (0, 0, 0.6),
                  'white': (1,1,1),
                  'grey': (0.88, 0.88, 0.92),
                  'black': (0.0, 0.0, 0.0)}
        COIN_COLORS={0:'black', 1:'red', 2:'yellow'}
        
        # Useful to find where to paint coins
        sq_size = (
            1.0 * self.size[0]/tab.shape[1],
            1.0 * self.size[1]/tab.shape[0])
        coin_ratio = 0.8 # space used by a coin inside a square
        
        self.clear_canvas()

        with self.canvas.after:
            # Grid image 
            Color(1.0,1.0,1.0, mode='rgb')
            Rectangle(source=GRID_IMAGE_PATH, pos=self.pos, size=self.size)
            

        with self.canvas:
            # Coins
            for row in range(tab.shape[0]):
                for col in range(tab.shape[1]):
                    color = COIN_COLORS[tab[row,col]]
                    Color(*COLORS[color], mode='rgb')
                    Ellipse(pos=(self.pos[0] + sq_size[0] * (col + (1-coin_ratio)/2),
                                 self.pos[1] + sq_size[1] * (row + (1-coin_ratio)/2)),
                            size=(i*coin_ratio for i in sq_size))
            
            
    def fall_anim(self, row, col, player,  NROW=6,NCOL=7):
        """
        Animation of a coin of player whose final position is determined by row and col.
        """
        COLORS = {
                # 'red': (0.83,0,0),
                'red': (0.71,0.03,0.03),
                  'yellow': (0.85, 0.65, 0.07),
                  'blue': (0, 0, 0.6),
                  'white': (1,1,1),
                  'grey': (0.88, 0.88, 0.92),
                  'black': (0.0, 0.0, 0.0)}
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
                         duration = (NROW-row)/10)
                
        return (anim, e)
        

    def clear_canvas(self):
        self.canvas.clear()
        self.canvas.after.clear()
        

class MyPopup(Popup):
    """
    Create the popup to choose game settings (difficulty and who starts)
    """
    
    def __init__(self, levels, current_level, **kwargs):
        super(Popup, self).__init__(**kwargs)
        
        # Add difficulty level to spinner
        spinner = self.ids['level_select']
        spinner.text = current_level
        spinner.values = levels
                
    def start_button(self):
        level = self.ids['level_select'].text
        computer_first = self.ids['computer_starts'].state == 'down'
        root.start_game(level, computer_first)
        self.dismiss()
     
class EndPopup(Popup):
    '''
    Create popup to inform of game results.
    '''

    def __init__(self, winner, **kwargs):
        assert(winner in ['computer','player','equality'])
        super(Popup, self).__init__(**kwargs)
        d = {'computer': 'You lost!',
             'player': 'You are the winner!',
             'equality': 'Equality ... '}
        self.ids['message'].text = d[winner]
        

    def start_button(self, *args):
        self.dismiss()
        root.open_popup()
        
class MyBox(BoxLayout):

    def __init__(self, **kwargs):
        super(MyBox, self).__init__(**kwargs)
        self.c4 = ConnectFour()
        
        self.block_touch = False
        
        # Bind touch on grid
        grid = self.ids['grid']
        grid.bind(on_touch_down=self.on_grid_touch)
        grid.bind(size=self.refresh)

        # Adapt size of the grid, so that the aspect ratio of the image is kept
        self.ids['grid_container'].bind(size=self.resize_grid)
        
        Clock.schedule_once(lambda dt: self.open_popup(), 0)
        

    def resize_grid(self, grid_container, *args):
        # Adapt size of the grid, so that the aspect ratio of the image is kept
        container_size_x, container_size_y = self.ids['grid_container'].size
        container_ratio = container_size_x / container_size_y
        grid = self.ids['grid']
        if container_ratio > IMAGE_RATIO:
            # container is larger than the image
            grid.size_hint_x = IMAGE_RATIO / container_ratio
            grid.size_hint_y = 1
        else:
            grid.size_hint_x = 1
            grid.size_hint_y = container_ratio / IMAGE_RATIO


    def on_grid_touch(self, grid, touch):
        '''
        Deal with touch on grid.
        '''
                
        if grid.collide_point(*touch.pos) and not self.block_touch:
            # Click in the paint widget
            
            # Block touch (until computer finished playing next move)
            self.block_touch = True
            # Find corresponding column
            NCOL = 7            
            col = int((touch.x-grid.pos[0])/grid.size[0] * NCOL)
                        
            c4 = self.c4
            message = self.ids['message']
            
            # It's the player turn to play and a coin can be added in the selected column
            if c4.get_state()==0 and c4.add_coin(col):
                # Animation to make the coin fall
                anim, e = grid.fall_anim(*c4.last_pos, 3-c4.player)

                self.check_game_end()
                
                if c4.get_state()==0:
                    # Computer plays
                    message.text = "Computer computing next move..."
                    # Without the inner schedule_once, the animation is blocked 
                    # before completion
                    anim.bind(on_complete=lambda x,y: 
                        Clock.schedule_once(lambda dt: self.computer_plays(), 0))
                                                        
                anim.start(e)
                return True
            
            self.block_touch = False
    
    def unblock_touch(self):
        self.block_touch = False

    def check_game_end(self):
        """
        Check if game is finished. If finished, update label accordingly.
        """
        # Check if game is finished
        state = self.c4.get_state()
        if state != 0:
            if state > 0:
                if self.computer_first:
                    state = 3 - state
                if state == 1:
                    winner = 'player'
                else:
                    winner = 'computer'                    
            else:
                winner = 'equality'

            self.open_end_popup(winner)

    
    
    def computer_plays(self):
        """
        Compute next move for computer. Update canvas and label accordingly.
        """
        c4 = self.c4
        message = self.ids['message']
        col = c4.get_next_col()
        c4.add_coin(col)
        
        # Coin fall animation
        anim, e = self.ids['grid'].fall_anim(*c4.last_pos, 3-c4.player)
        # unblock touch once animation is finished
        anim.bind(on_complete=lambda x,y: 
                        Clock.schedule_once(lambda dt: self.unblock_touch(), 0))   
        anim.start(e)
            
        message.text = "Computer played in column {}".format(col)
        self.check_game_end()
            
  
    def refresh(self, *args):
        """
        Draw current state of grid on canvas
        """
        grid_canvas = self.ids['grid']
        grid_canvas.clear_canvas()
        grid_canvas.draw_tab(tab=self.c4.grid)        
        
    def start_game(self, level, computer_first):


        print(f'Starting a new game, computer first: {computer_first}')


        self.ids['message'].text = ''        
        self.c4.clear()
        self.c4.update_level(level)        
        self.computer_first = computer_first        
        self.refresh()
        
        if self.computer_first:
            # computer plays first
            Clock.schedule_once(lambda dt: self.computer_plays(), 0)
        else:
            # Unblock touch on grid so that player can play
            self.unblock_touch()
            
    def clear(self):
        """
        Remove coins, message from main window.
        """
        self.ids['message'].text = ''        
        self.c4.clear()
        self.refresh()
        
            
    def open_popup(self, *args):
        """
        Opens a popup to choose next game settings
        """
        # Clear grid and message
        self.clear()
        
        levels = [k for k,v in self.c4.LEVELS]
        current_level = self.c4.level_name
        self.popup = MyPopup(levels, current_level)
        self.popup.open()
        
    def open_end_popup(self, winner):
        popup = EndPopup(winner)
        popup.open()
        


class ConnectFourApp(App):

    def build(self):
        global root
        root = MyBox()
        return root


if __name__ == '__main__':
    ConnectFourApp().run()


