#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 00:17:27 2018

@author: em
"""

from kivy.core.audio import SoundLoader

sound = SoundLoader.load('mytest.ogg')
if sound:
    print("Sound found at %s" % sound.source)
    print("Sound is %.3f seconds" % sound.length)
    sound.play()