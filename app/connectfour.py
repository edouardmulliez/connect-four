# -*- coding: utf-8 -*-
"""
Class to play at connect 4
"""

import numpy as np
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


def get_next_col(grid, player, step=6):
    """
    Compute the next col where player (1 or 2) should put the coin. Step is the number of
    moves that will be taken into account.
    """    
    col = alphabeta(grid, player, -math.inf, math.inf, 0, step)[1]
    return col



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





class ConnectFour:
    """
    Class to play connect4.
    Contains grid state and current player.
    """
    
#    LEVELS = list(zip(['Easy','Medium','Hard','Very Hard'], [3,4,5,6]))
    LEVELS = list(zip(['Easy','Medium','Hard'], [3,4,5]))
    
    def __init__(self):
        self.grid = np.zeros((NROW,NCOL), dtype=int)
        self.player = 1 # next player to play
        self.update_level('Medium')
        self.last_pos = None # Position of the last coin put.

        
    def update_level(self, level_name):
        """
        Change step number depending on level_name. step is the number of moves 
        evaluated by the computer to choose its next move.
        """
        assert(level_name in [k for k,v in ConnectFour.LEVELS])
        self.level_name = level_name
        for k, v in ConnectFour.LEVELS:
            if k==self.level_name:
                self.step = v
            

    def add_coin(self, col):
        """
        Add coin in column col for current player.
        If operation possible, change current player and return True.
        Else return False
        """
        valid = add_coin(self.grid, self.player, col)
        if valid:
            self.player = 3 - self.player
            # update last_pos
            row = (self.grid[:,col] != 0).nonzero()[0][-1]
            self.last_pos = (row, col)
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


