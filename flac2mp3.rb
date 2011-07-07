#!/usr/bin/ruby

require 'find'
require 'rubygems'

def trouveFichiers(extension, *repertoires_racines) 
	fichiers = []
	Find.find(*repertoires_racines) do |path| 
		if File.file?(path) && path.end_with?(extension) 
			fichiers << path
		end
	end
	fichiers
end

def litMetaFlac(texte)
	metadonnees = Hash[*texte.split(/=|\n/).flatten]
	metadonnees.each {|key, value|
		metadonnees.delete(key)
		metadonnees[key.upcase] = value
	}
end
 
def flac2mp3(nom_fichier) 
	raise "l'extension du fichier n'est pas .flac :" + nom_fichier if not nom_fichier =~ /.flac$/
	raise "fichier inexistant :" + nom_fichier if not File.exist? nom_fichier
	metaflac = litMetaFlac %x[metaflac  --export-tags-to=- "#{nom_fichier}"]
	nom_fichier_mp3 = nom_fichier.gsub(/\.flac$/, ".mp3")	
	image=File.dirname(nom_fichier) + "/cover.jpg"
	artiste = metaflac["ARTIST"]
	plage = metaflac["TRACKNUMBER"]
	album = metaflac["ALBUM"]
	titre = metaflac["TITLE"]
	genre = metaflac["GENRE"]
	date = metaflac["DATE"]
	if date.include? "-"
		date = date.split('-')[0]
	end
	puts "flac -dcs #{nom_fichier} | lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 - #{nom_fichier_mp3} && eyeD3  -a #{artiste} -n #{plage} -A #{album} -t #{titre} --add-image #{image}:FRONT_COVER: -G #{genre} -Y #{date} --set-encoding=utf8 #{nom_fichier_mp3}"
	%x[flac -dcs "#{nom_fichier}" | lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 - "#{nom_fichier_mp3}" && eyeD3  -a "#{artiste}" -n "#{plage}" -A "#{album}" -t "#{titre}" --add-image "#{image}":FRONT_COVER: -G "#{genre}" -Y "#{date}" --set-encoding=utf8 "#{nom_fichier_mp3}"]

end

################# main
# threadpool comming from 
# http://blog.vmoroz.com/2011/06/ruby-thread-pool-in-erlang-style.html
# thx !
# ####################

nombre_processeurs = `cat /proc/cpuinfo | grep processor | wc -l`.to_i

items_to_process = trouveFichiers(".flac", *ARGV)

message_queue = Queue.new
start_thread = 
  lambda do
    Thread.new(items_to_process.shift) do |flac|
      puts "Processing #{flac}"
      flac2mp3(flac)
      message_queue.push(:done)
    end
  end

items_left = items_to_process.length

POOL_SIZE=nombre_processeurs
[items_left, POOL_SIZE].min.times do
  start_thread[]
end

while items_left > 0 
  message_queue.pop
  items_left -= 1
  start_thread[] unless items_left < POOL_SIZE
end
