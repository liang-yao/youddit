#!/bin/bash

identify -format "%f %w %h \n" *.jpg

convert hq.jpg -modulate 100,0 -blur 0x4 -resize 1200 output2.png
convert hqdefault.jpg -modulate 100,0 -blur 0x12 -resize 1200 output1.png



# handle for 4:3 traditional thumbnails
#convert hqdefault.jpg -resize 1000 -blur 0x12 output.png


