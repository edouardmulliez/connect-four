# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 00:37:23 2018

@author: em
"""

import scipy.misc
import numpy as np
from skimage.draw import ellipse

# Image size
width = 1280
height = 960
channels = 4

NCOL = 7
NROW = 6
ratio = 0.65

# Create an empty image
img = np.zeros((height, width, channels), dtype=np.uint8)

# Background color
img[:,:,:] = [10,40,95, 255]

# Draw transparent holes into it
sq_size = (height/NROW, width/NCOL)
for row in range(NROW):
    for col in range(NCOL):
        cy = sq_size[0] * (row + 0.5)
        cx = sq_size[1] * (col + 0.5)
        ry = sq_size[0]/2 * ratio
        rx = sq_size[1]/2 * ratio
        rr, cc = ellipse(int(cy), int(cx), int(ry), int(rx))
        img[rr,cc,3] = 0
        
# Save the image
scipy.misc.imsave("test-transparency.png", img)



