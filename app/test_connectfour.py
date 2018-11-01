#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  8 18:31:15 2018

@author: em
"""

import unittest

from connectfour import ConnectFour, NROW, NCOL

class TestConnectFour(unittest.TestCase):


    def setUp(self):
        self.c4 = ConnectFour()

    def test_add_coin(self):
        # change of player
        previous_player = self.c4.player
        self.c4.add_coin(2)
        self.assertNotEqual(previous_player, self.c4.player,
                            'add_coin should change self.player')

        # We can exactly add NROW coins in a given column        
        for i in range(NROW):
            self.assertTrue(self.c4.add_coin(3))        
        self.assertFalse(self.c4.add_coin(3),
                         'We cannot add more than NROW coins in a given col')
        
        # Checking grid modifications
        self.c4.clear()
        player1 = self.c4.player
        for i in range(NROW):
            self.c4.add_coin(4)
        self.assertEqual(self.c4.grid[0,4], player1)
        self.assertEqual(self.c4.grid[2,4], player1)
        self.assertEqual(self.c4.grid[1,4], 3-player1)
        
        
    def test_get_state(self):
        # No one has won
        for i in range(NROW):
            self.c4.add_coin(3)
        self.assertEqual(self.c4.get_state(), 0, 'No one has won')
        
        # A player has won
        self.c4.clear()
        self.c4.grid[0:4,1] = 1
        self.assertEqual(self.c4.get_state(), 1, 'player 1 has won')

        self.c4.clear()
        self.c4.grid[0,1:5] = 2
        self.assertEqual(self.c4.get_state(), 2, 'player 2 has won')
        
        self.c4.clear()
        for i in range(4):
            self.c4.grid[i+1,i] = 1
        self.assertEqual(self.c4.get_state(), 1, 'player 1 has won')
        
        self.c4.clear()
        for i in range(4):
            self.c4.grid[i+1,i] = 1
        self.assertEqual(self.c4.get_state(), 1, 'player 1 has won')
        
        self.c4.clear()
        for i in range(4):
            self.c4.grid[4-i,i] = 1
        self.assertEqual(self.c4.get_state(), 1, 'player 1 has won')


if __name__ == '__main__':
    unittest.main()