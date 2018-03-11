# -*- coding: utf-8 -*-
"""
Class to play at connect 4
"""

# To do: 
# Build UI
# 


import numpy as np
import itertools
import math


NROW=6
NCOL=7


## Create boolean arrays to easily select rows, columns, diagonals from the grid.
def from_idx_to_mask(idx):
    """
    Transform list of indices into a boolean array, that can be used to subset 
    elements of an array.
    """
    mask = np.zeros((NROW,NCOL), dtype=np.bool)
    for row, col in idx:
        mask[row,col] = True
    return mask

ROWS = [[(row, col) for col in range(NCOL)] for row in range(NROW)]
COLS = [[(row, col) for row in range(NROW)] for col in range(NCOL)]
DIAG = [[(i, n-i) for i in range(n+1) if i < NROW and n-i < NCOL]
          for n in range(3, NROW+NROW-3)]
DIAG += [[(i, i+n) for i in range(NROW) if 0 <= i+n < NCOL]
          for n in range(-(NROW-4), NCOL-3)]
UNITS = ROWS + COLS + DIAG
UNITS = [from_idx_to_mask(u) for u in UNITS]

     
def print_grid(grid):
    char = {0: ' ', 1: 'X', 2: 'O'}        
    for row in range(NROW-1, -1, -1):
        print('|'+'|'.join([char[i] for i in grid[row,:]])+'|')            
    print('-'* 15)
    print('|'+'|'.join(str(i) for i in range(NCOL))+'|')
        

def add_coin(grid, player, col):
    """
    Add a coin in the grid in column col. Return False if coin cannot be added in grid.
    Modifies grid inplace.
    :param player: either 1 or 2
    :param col: int between 0 and NCOL-1
    """
    assert(player in [1,2])
    assert(col in range(NCOL))
            
    if (grid[NROW-1,col] != 0):
        return False
    # Find 1st empty row in col.
    row = np.nonzero(grid[:, col] == 0)[0][0]
    grid[row, col] = player
    return True

def remove_coin(grid, col):
    """
    Remove last coin in col. Returns false if no coin can be removed.
    Modifies grid inplace.
    :param col: int between 0 and NCOL-1
    """
    assert(col in range(NCOL))
    
    if (grid[0, col] == 0):
        return False    
    # Find last non zero element in col
    row = (grid[:,col] != 0).nonzero()[0][-1]
    grid[row,col] = 0    
    return True


def get_max_alignment(l):
    """
    Get the maximum number of consecutive True values in list or array l.
    """
    cnt = 0
    max_cnt = 0
    for i in l:
        if i:
            cnt += 1
            if cnt > max_cnt:
                max_cnt = cnt
        else:
            cnt = 0            
    return max_cnt

def is_seq_in_array(a, seq):
    """
    Returns True if sequence seq is in array a. 
    a and seq are 1D np.array
    """
    N, p = a.size, seq.size
    for i in range(N+1-p):
        if (a[i:i+p] == seq).all():
            return True
    return False


def has_winner(grid):
    """
    If a player has won, return its id.
    Else return 0.
    """
    for p in [1,2]:
        a = (grid == p)
        for u in UNITS:
            if get_max_alignment(a[u]) >= 4:
                return p
    return 0
        

# Patterns to find in grid
seq_3 = set(itertools.permutations([1,1,1,0], 4))
seq_2 = set(itertools.permutations([1,1,0,0], 4))
seq_1 = set(itertools.permutations([1,0,0,0], 4))
sequences = {1: {1: seq_1, 2: seq_2, 3: seq_3},
             2: {}}
# Convert to array
for k, v in sequences[1].items():
    sequences[1][k] = [np.array(s) for s in v]
    sequences[2][k] = [2*a for a in sequences[1][k]]
# sequences[p][n] contains a list of array, each array representing a pattern 
# to find n coins in a row for player p.


WINDOW_MASK = np.ones(4,dtype=int)
VICTORY_VALUE = 10**6
def get_unit_value(line, p):
    """
    Get the value of a given line (row,column or diagonal) for player p.
    We take into account possible alignments of 1, 2, 3 or 4 coins.
    """
    # Compute window count on line
    zero_cnt = np.convolve(line==0, WINDOW_MASK, mode='valid')
    p_cnt = np.convolve(line==p, WINDOW_MASK, mode='valid') # Count for player
    o_cnt = 4 - zero_cnt - p_cnt # count for opponent
    
    if max(p_cnt) >= 4:
        return VICTORY_VALUE
    if max(o_cnt) >= 4:
        return -VICTORY_VALUE
    
    p_pt, o_pt = 0, 0 # Points for player and opponent
    
    for n in range(3,0,-1):
        # Look for sequences with n coins
        if np.any(np.logical_and(p_cnt==n, zero_cnt==4-n)):
            p_pt = 10**(n-1)
            break
    for n in range(3,0,-1):
        # Look for sequences with n coins
        if np.any(np.logical_and(o_cnt==n, zero_cnt==4-n)):
            o_pt = 10**(n-1)
            break
    return p_pt-o_pt
    
def grid_value(grid, player):
    """
    Evaluate the value of a given grid for player.
    """
    return sum([get_unit_value(grid[u], player) for u in UNITS])
    

#def get_unit_value(line, p):
#    """
#    Get the value of a given line (row,column or diagonal) for player p.
#    We take into account possible alignments of 1, 2, 3 or 4 coins.
#    """
#    if (line != p).all():
#        return 0
#    if get_max_alignment(line==p) >= 4:
#        # Victory
#        return VICTORY_VALUE
#    
#    for n in range(3,0,-1):
#        # Look for sequences with n coins
#        for s in sequences[p][n]:
#            if is_seq_in_array(line, s):
#                return 10**(n-1)
#    return 0
#
#
#
#def grid_value(grid):
#    """
#    Evaluate the value of a given grid for the player 1.
#    """
#    
#    value = sum([get_unit_value(grid[u], 1) for u in UNITS])
#    value -= sum([get_unit_value(grid[u], 2) for u in UNITS])
#    
#    return value
    


def get_next_col(grid, player, step=6):
    """
    Compute the next col where player (1 or 2) should put the coin. Step is the number of
    moves that will be taken into account.
    """    
    col = alphabeta(grid, player, -math.inf, math.inf, 0, step)[1]
    return col


#def build_grid(grid, node, player):
#    """
#    Build a new grid by adding the elements of node in grid.
#    Returns a new array.
#    Player is the first player to add a coin.
#    """    
#    # to do: deal with player
#    assert(player in [1,2])
#    grid = grid.copy()
#    for col in node:
#        add_coin(grid, player, col)
#        player = 3 - player
#    return grid
#    
#
## Apply minimax algo on Tree. Perhaps we need to apply a multiplier for grid values not on terminal nodes.
## The closer it is to root, the more value (positive or negative) it has.
#
#def minimax(tree, node, level, grid):
#    """
#    We should begin with level 1 and node=()
#    Returns a tuple (node, value)
#    """
#    
#    # If node has children, take max or min depending on parity of level
#    if len(tree[node]) > 0:
#        
#        if level == 1:
#            # Randomly select one of the best nodes
#            nodes = [(child, minimax(tree, child, level+1, grid)[1]) for child in tree[node]]
#            max_value = max([v for k,v in nodes])
#            nodes = [k for k,v in nodes if v==max_value]
#            return (random.choice(nodes), max_value)
#            
#        if level % 2 == 1:
##            return max([minimax(tree, child, level+1, grid) for child in tree[node]])
#            return max([(child, minimax(tree, child, level+1, grid)[1]) for child in tree[node]],
#                        key=lambda x: x[1])
#        else:
#            return min([(child, minimax(tree, child, level+1, grid)[1]) for child in tree[node]],
#                        key=lambda x: x[1])
#
#    # Else, get the value of the grid.
#    else:
#        # Create grid with correct coins in it
#        new_grid = build_grid(grid, node, 1)
#        return (node, grid_value(new_grid))


## alphabeta function not simplified

def alphabeta(grid, player, alpha, beta, depth, max_depth):
    """
    alphabeta is a more efficient application of minimax algo
    The idea is to explore only the necessary branches of the minimax algo.
    :param grid: current state of the grid
    :param player: next player to play (used to know which type of coin is added next)
    :param depth: current depth in the tree. Depth of tree root is 0.
    :param max_depth: maximum depth in the tree (depth of the final leaves)
    
    alpha, beta are parameters to determine which branch should be cut off.
    
    Returns a tuple (value, col)
    """
    
    custom_cols = [3,2,4,1,5,0,6]
        
    if (depth == max_depth) or has_winner(grid):
        # Final leaf
        initial_player = player if depth%2==0 else 3-player
        return (grid_value(grid, initial_player)/(depth/max_depth), None)
        
    best_col = None
    
    if depth % 2 == 1:
        # Min node
        v = math.inf
        for col in custom_cols: #         for col in range(NCOL):
            # update grid
            if add_coin(grid, player, col):
                ab = alphabeta(grid, 3-player, alpha, beta, depth+1, max_depth)[0]
                if ab <= v:
                    v = ab
                    best_col = col
                # put grid back to inital value
                remove_coin(grid, col)
                if alpha >= v:
                    return (v, best_col)
                beta = min(beta,v)
    else:
        # Max node
        v = -math.inf
        for col in custom_cols: #         for col in range(NCOL):
            # update grid
            if add_coin(grid, player, col):
                ab = alphabeta(grid, 3-player, alpha, beta, depth+1, max_depth)[0]
                if ab >= v:
                    v = ab
                    best_col = col
                # put grid back to inital value
                remove_coin(grid, col)
                if v >= beta:
                    return (v, best_col)
                alpha = min(alpha,v)
        
    return (v, best_col)


LEVELS = dict(zip([1,2,3,4], [3,4,5,6]))


class ConnectFour:
    """
    Class to play connect4.
    Contains grid state and current player.
    """
    
    
    def __init__(self):
        self.grid = np.zeros((NROW,NCOL), dtype=int)
        self.player = 1 # next player to play
        self.step = 4 # Number of steps considered by computer. 
        
    def add_coin(self, col):
        """
        Add coin in column col for current player.
        If operation possible, change current player and return True.
        Else return False
        """
        valid = add_coin(self.grid, self.player, col)
        if valid:
            self.player = 3 - self.player
        return valid
        
    def get_next_col(self):
        """
        Compute the next column where to put the coin for current player.
        """
        return get_next_col(self.grid, self.player, self.step)
        
    def get_state(self):
        """
        Return current state of the game:
            * 1,2: player 1 or 2 has won
            * -1: grid is full
            * 0: grid not full and noone has won
        """
        winner = has_winner(self.grid)
        if winner > 0:
            return winner
        if (self.grid != 0).all():
            return -1
        return 0
    
    def clear(self):
        self.grid[:] = 0
        self.player = 1


def play():
    """
    Ask each player to play in succession, by indicating the chosen column.
    """
    # initialize grid
    grid = np.zeros((NROW,NCOL), dtype=int)
    p = 1
    
    
    # Choose first player
    first=''
    while first not in ['y','n']:
        first = input('Do you want to play first? (y/n): ')
    computer = 2 if first=='y' else 1
    
    # Choose level
    level_names = LEVELS.keys()
    level = -1
    while level not in level_names:
        level = input('Choose a level of difficulty (between 1 and 4): ')
        try:
            level = int(level)
            assert(level in level_names)
        except ValueError:
            print("Please enter an integer between 1 and 4!")
            continue
    step = LEVELS[level]
    
    while (has_winner(grid) == 0 and (grid == 0).any()):
        print_grid(grid)
        
        if p==computer:
            # Computer plays 
            print('Computer computing next move...')
            col = get_next_col(grid, p, step=step)
        else:
            prompt = 'Player {}, choose a column between 0 and {}: '.format(p, NCOL-1)
            col = input(prompt)
            
            try:
                col = int(col)
            except ValueError:
                print("Please enter an integer!")
                continue
        
        if add_coin(grid, p, col):
            # Possible column, change player
            p = 3 - p 
        else:
            # Impossible column, try again
            print("You can't choose column {}".format(col))
    
    print_grid(grid)
    winner = has_winner(grid)
    if winner == 0:
        print('Equality!')
    elif winner==computer:
        print('Computer wins!')
    else:
        print('You are the winner!')
