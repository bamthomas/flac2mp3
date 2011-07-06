#!/usr/bin/ruby

require 'find'
require 'set'

def trouveFlac(*repertoires_racines) 
	fichiers_flac = Set.new
	Find.find(*repertoires_racines) do |path| 
		if File.file?(path) && path.end_with?(".flac") 
			fichiers_flac << path
		end
	end
	return fichiers_flac
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
	artiste = metaflac["ARTIST"]
	plage = metaflac["TRACKNUMBER"]
	album = metaflac["ALBUM"]
	titre = metaflac["TITLE"]
	genre = metaflac["GENRE"]
	date = metaflac["DATE"]
	if date.include? "-"
		date = date.split('-')[0]
	end
	puts "flac -dcs #{nom_fichier} | lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 - #{nom_fichier_mp3} && eyeD3  -a #{artiste} -n #{plage} -A #{album} -t #{titre} --add-image=cover.jpg:FRONT_COVER: -G #{genre} -Y #{date} --set-encoding=utf8 #{nom_fichier_mp3}"
	%x[flac -dcs "#{nom_fichier}" | lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 - "#{nom_fichier_mp3}" && eyeD3  -a "#{artiste}" -n "#{plage}" -A "#{album}" -t "#{titre}" --add-image=cover.jpg:FRONT_COVER: -G "#{genre}" -Y "#{date}" --set-encoding=utf8 "#{nom_fichier_mp3}"]

end


threads = []
for file in ARGV
	threads << Thread.new(file) { |myFile|
		flac2mp3(file)
  	}
end

threads.each { |aThread|  aThread.join }

#ARGV.each { |file| flac2mp3(file)}
