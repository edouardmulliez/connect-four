# -*- coding: utf-8 -*-
"""
Class to play at connect 4
"""

# To do: 
# Fix bug on alphabeta function for a specific grid
# - 1. improve function to compute grid value (see has_rolling_count function)
# - 2. Make it possible for the computer to be player 2


import numpy as np
import itertools
import random
import math


NROW=6
NCOL=7


# Problem: I have to prioritize value of victory depending on how many tour it will be obtained.
# Idea: put a big value for a vicotry. Divide value by depth in tree. Or substract -1.


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
          for n in range(3, NROW+NROW-4)]
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

#a = np.array([0,1,1,1,1,0])
#seq = np.array([1,1,0])
#is_seq_in_array(a,seq)


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


# Perhaps to do: simplify fet_unit_value function.
# Idea: instead of checking each patttern separately, count the number of 0/p on a rolling window.

def has_rolling_count(line, counts={0: 1, 1: 3}, window=4):
    """
    Check if we can find window consecutive elements in line that respects the counts
    indicated in dictionary counts.
    For counts={0: 1, 1: 3} for example, we look for 4 consecutive elements: 0 once + 1 thrice
    """
    if len(line) < window:
        return False
    for i in range(len(line)- window + 1):
        if all([sum(line[i:i+window] == k) == v for k,v in counts.items()]):
            return True

    return False


def get_unit_value(line, p):
    """
    Get the value of a given line (row,column or diagonal) for player p.
    We take into account possible alignments of 1, 2, 3 or 4 coins.
    """
    if (line != p).all():
        return 0
    if get_max_alignment(line==p) >= 4:
        # Victory
        return math.inf
    
    for n in range(3,0,-1):
        # Look for sequences with n coins
        for s in sequences[p][n]:
            if is_seq_in_array(line, s):
                return 10**(n-1)
    return 0


def grid_value(grid):
    """
    Evaluate the value of a given grid for the player 1.
    """
    
    value = sum([get_unit_value(grid[u], 1) for u in UNITS])
    value -= sum([get_unit_value(grid[u], 2) for u in UNITS])
    
    return value
    
#    # Really simple: positive value if 1 wins, negative if 1 lose
#    winner = has_winner(grid)
#    values = {0: 0, 1: 1, 2: -1}
#    return values[winner]


from collections import defaultdict

class Tree(defaultdict):
    
    def __init__(self, *args, **kwargs):
        super().__init__(set, *args, **kwargs)
    
    def add(self, parent, value):
        """
        Add a node under parent. The new node key is built using the parent key and value.
        Returns the key of the new node.
        """
        new_id = tuple(list(parent)+[value])
        self[parent].add(new_id)
        return new_id
        
    def pretty_print(self, root=(), level=0):
        space='  '
        print(space*level + str(root))
        for i in sorted(list(self[root])):
            self.pretty_print(root=i, level=level+1)
            

  
def build_tree(grid, tree, root, player, step=4):
    """
    Build a graph of the possible column choices. Max depth is step.
    Impossible states are not added. If a winning or losing situation is 
    encountered, we do not go further in the leaf.
    
    :param grid: grid with necessary coins added in it
    :param root: node of the tree from which we begin
    :param step: max depth where we should continue
    
    Each node id contains the whole path.
    Another implementation where each node id contain only the last column would be possible.    
    """

    if step <= 0:
        return True

    for col in range(NCOL):
        new_grid = grid.copy()
        if add_coin(new_grid, player, col):
            # It is possible to add coin in col. Adding node.
            new_node = tree.add(root, col)
            
            if has_winner(new_grid) == 0:
                # Keep building leaves only if no one has won
                build_tree(new_grid, tree, new_node, 3-player, step-1)
    

#grid = np.zeros((NROW,NCOL), dtype=np.int)
#grid[:,0] = [1,2]*3
#grid[4:6,0] = 0
#grid[3,0] = 1
#grid[0,1:4] = 2
#
#print_grid(grid)
#has_winner(grid)
#
#grid_value(grid)


def get_next_col(grid, step=5):
    """
    Compute the next col where the computer should put the coin. Step is the number of
    moves that should be taken into account.
    """    
    col = alphabeta(grid, 1, -math.inf, math.inf, 0, step)[1]
    return col


def build_grid(grid, node, player):
    """
    Build a new grid by adding the elements of node in grid.
    Returns a new array.
    Player is the first player to add a coin.
    """    
    # to do: deal with player
    assert(player in [1,2])
    grid = grid.copy()
    for col in node:
        add_coin(grid, player, col)
        player = 3 - player
    return grid
    

# Apply minimax algo on Tree. Perhaps we need to apply a multiplier for grid values not on terminal nodes.
# The closer it is to root, the more value (positive or negative) it has.

def minimax(tree, node, level, grid):
    """
    We should begin with level 1 and node=()
    Returns a tuple (node, value)
    """
    
    # If node has children, take max or min depending on parity of level
    if len(tree[node]) > 0:
        
        if level == 1:
            # Randomly select one of the best nodes
            nodes = [(child, minimax(tree, child, level+1, grid)[1]) for child in tree[node]]
            max_value = max([v for k,v in nodes])
            nodes = [k for k,v in nodes if v==max_value]
            return (random.choice(nodes), max_value)
            
        if level % 2 == 1:
#            return max([minimax(tree, child, level+1, grid) for child in tree[node]])
            return max([(child, minimax(tree, child, level+1, grid)[1]) for child in tree[node]],
                        key=lambda x: x[1])
        else:
            return min([(child, minimax(tree, child, level+1, grid)[1]) for child in tree[node]],
                        key=lambda x: x[1])

    # Else, get the value of the grid.
    else:
        # Create grid with correct coins in it
        new_grid = build_grid(grid, node, 1)
        return (node, grid_value(new_grid))


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
        return (grid_value(grid), None)
        
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
    
#    if best_col is None:
#        print("best_col; is None")
#        print("depth: {}".format(depth))
#        print("grid: {}".format(grid))
#        print(f'value v: {v}')
    
    return (v, best_col)



## 1 Understand why this grid produces an error for alphabeta function
##| | | | | | | |
##| | | | | | | |
##| | | |O| | | |
##| | | |O|O| | |
##| | | |X|X| | |
##|X| | |X|O| | |
##---------------
##|0|1|2|3|4|5|6|
#    
#grid = np.zeros((NROW,NCOL), dtype=int)
#grid[0,0] = 1
#grid[0:2,3] = 1
#grid[1,4] = 1
#
#grid[0,4] = 2
#grid[2,4] = 2
#grid[2,3] = 2
#grid[3,3] = 2
#print_grid(grid)
#get_next_col(grid)





## Comparing execution time
#start = timeit.default_timer()
#grid = np.zeros((NROW,NCOL), dtype=int)
#step = 6
#test_alpha = alphabeta(grid, 1, -math.inf, math.inf, 0, step)
#end = timeit.default_timer()
#print(end - start)
#
#
#start = timeit.default_timer()
#grid = np.zeros((NROW,NCOL), dtype=int)
#step = 5
#tree = Tree()
#build_tree(grid, tree, (), 1, step=step)
#test = minimax(tree, (), 1, grid)
#end = timeit.default_timer()
#print(end - start)


def play():
    """
    Ask each player to play in succession, by indicating the chosen column.
    """
    # initialize grid
    grid = np.zeros((NROW,NCOL), dtype=int)
    p = 1
    while (has_winner(grid) == 0 and (grid == 0).any()):
        print_grid(grid)
        
        if p==1:
            # Computer plays 
            print('Computer computing next move...')
            col = get_next_col(grid)
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
    else:
        print('Player {} is the winner!'.format(winner))
