#!/bin/bash
REPO_MP3=../../mp3/export

find $@ -name "*.flac" | while read fichier
do 
  DIR=`dirname "$fichier"`
  FILE=`basename "$fichier"`
  DIR_MP3="$REPO_MP3/$DIR"

  FICHIER_MP3=`echo "$REPO_MP3/${fichier}"| sed 's/\.flac/.mp3/'`

  if [ ! -f "$FICHIER_MP3" ] ;
  then 
	echo "transcoding $DIR/$FILE"
  	cd "$DIR" 
  	flac2mp3.rb *.flac
  	cd - > /dev/null
  	mkdir -p  "$DIR_MP3"
  	mv "$DIR"/*.mp3 "$DIR_MP3"
  fi
done
