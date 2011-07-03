require "flac2mp3"
require "test/unit"

class Flac2mp3Test < Test::Unit::TestCase
	def testRecette
		donnees_wav=["52","49","46","46","24","08","00","00","57","41","56","45","66","6d","74","20","10","00","00","00","01","00","02","00","22","56","00","00","88","58","01","00","04","00","10","00","64","61","74","61","00","08","00","00","00","00","00","00","24","17","1e","f3","3c","13","3c","14","16","f9","18","f9","34","e7","23","a6","3c","f2","24","f2","11","ce","1a","0d"]
		file = File.new("./tmp.wav", "wb")
		donnees_wav.each {|hex| file.putc hex.to_i(16)}
		file.close
		%x[flac -V --totally-silent -f -T "ARTIST=artist" -T "TRACKNUMBER=1" -T "ALBUM=album" -T "TITLE=titre" -T "GENRE=Electronic" -T "DATE=2008" ./tmp.wav]
		%x[lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 --ignore-tag-errors --ta "artist" --tn "1" --tl "album" --tt "titre" --tg "Electronic" --ty "2008" ./tmp.wav ./tmp_attendu.mp3]
		flac2mp3("tmp.flac")
	 	
		assert_equal(File::Stat.new("./tmp_attendu.mp3").size, File::Stat.new("./tmp.mp3").size, "la taille des fichiers doit etre la meme")
		mp3tags_attendus = %x[id3tool ./tmp_attendu.mp3].gsub(/Filename:.*\n/,"")
		mp3tags_generes = %x[id3tool ./tmp.mp3].gsub(/Filename:.*\n/,"")
		assert_equal(mp3tags_attendus,mp3tags_generes, "les tags mp3 doivent etre les memes")

		File.delete("./tmp.wav","./tmp.flac","./tmp_attendu.mp3","./tmp.mp3")
	end	
	def testLitMetaFlac_uneLigne
		assert_equal( {"TITRE"=>"titre"} ,litMetaFlac("TITRE=titre"))
	end
	def testLitMetaFlac_deuxLignes
		assert_equal( {"TITRE"=>"titre","ALBUM"=>"album"} ,litMetaFlac("TITRE=titre\nALBUM=album"))
	end
	def testFlac2mp3_fichierNeTerminantPasParFlac
		assert_raise(RuntimeError) {flac2mp3("fichier.blah")}
	end
	def testFlac2mp3_fichierInexistant
		assert_raise(RuntimeError) {flac2mp3("fichier_inexistant.flac")}
	end
end
