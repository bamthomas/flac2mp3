#!/usr/bin/ruby

require 'find'
require 'rubygems'

NOMBRE_PROCESSEURS = `cat /proc/cpuinfo | grep processor | wc -l`.to_i
POOL_SIZE=NOMBRE_PROCESSEURS

class Flac2mp3

  def trouve_fichiers(extension, *repertoires_racines)
    fichiers = []
    Find.find(*repertoires_racines) do |path|
      if File.file?(path) && path.end_with?(extension)
        fichiers << path
      end
    end
    fichiers
  end

  def lit_meta_flac(texte)
    metadonnees = Hash[*texte.split(/=|\n/).flatten]
    metadonnees.each {|key, value|
      metadonnees.delete(key)
      metadonnees[key.upcase] = value
    }
  end

  def flac2mp3(fichier_flac, racine_export_mp3)
    raise "l'extension du fichier n'est pas .flac :" + fichier_flac if not fichier_flac =~ /.flac$/
    raise "fichier inexistant :" + fichier_flac if not File.exist? fichier_flac
    chemin_flac = File.dirname(fichier_flac)
    chemin_mp3 = racine_export_mp3 + "/" + chemin_flac
    cree_repertoire_si_nessessaire(chemin_mp3)
    fichier_mp3 = chemin_mp3 + "/" + File.basename(fichier_flac).gsub(/\.flac$/, ".mp3")
    
    metaflac = self.lit_meta_flac `metaflac  --export-tags-to=- "#{fichier_flac}"`
    image= chemin_flac + "/cover.jpg"
    artiste = metaflac["ARTIST"]
    plage = metaflac["TRACKNUMBER"]
    album = metaflac["ALBUM"]
    titre = metaflac["TITLE"]
    genre = metaflac["GENRE"]
    date = metaflac["DATE"]
    if date.include? "-"
      date = date.split('-')[0]
    end
    puts "flac -dcs #{fichier_flac} | lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 - #{fichier_mp3} && eyeD3  -a #{artiste} -n #{plage} -A #{album} -t #{titre} --add-image #{image}:FRONT_COVER: -G #{genre} -Y #{date} --set-encoding=utf8 #{fichier_mp3}"
    %x[flac -dcs "#{fichier_flac}" | lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 - "#{fichier_mp3}" && eyeD3  -a "#{artiste}" -n "#{plage}" -A "#{album}" -t "#{titre}" --add-image "#{image}":FRONT_COVER: -G "#{genre}" -Y "#{date}" --set-encoding=utf8 "#{fichier_mp3}"]

  end

  def cree_repertoire_si_nessessaire(chemin_mp3)
    if (! File.directory?(chemin_mp3))
      `mkdir -p #{chemin_mp3}`
    end
  end

  ################# main
  # threadpool comming from
  # http://blog.vmoroz.com/2011/06/ruby-thread-pool-in-erlang-style.html
  # thx !
  # ####################
	def main(dest, *args)
    raise "target mp3 directory <#{dest}> does not exist" if not File.directory? dest
    
		items_to_process = self.trouve_fichiers(".flac", *args)
    items_left = items_to_process.length
    puts "found #{items_left} flac files and #{POOL_SIZE} encoding units (cores)"
    puts "mp3 destination is <#{dest}>"
		
    message_queue = Queue.new
		start_thread =
  		lambda do
      Thread.new(items_to_process.shift) do |flac|
        puts "Processing #{flac}"
        self.flac2mp3(flac, dest)
        message_queue.push(:done)
      end
    end

    [items_left, POOL_SIZE].min.times do
      start_thread[]
    end

    while items_left > 0
      message_queue.pop
      items_left -= 1
      puts "items left : #{items_left}"
      start_thread[] unless items_left < POOL_SIZE
    end
  end
end

if ARGV.length == 0
  Flac2mp3.new.main "./","./"
else
  destination = ARGV.pop
  if ARGV.length == 0
    Flac2mp3.new.main destination,"./"
  else
    Flac2mp3.new.main destination, *ARGV
  end
end
