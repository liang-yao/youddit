#!/bin/bash

rm thumbList

ls *.jpg > thumbList

while read LINE
do
      echo "$LINE"
      convert $LINE -modulate 100,0 bw$LINE

done < thumbList

