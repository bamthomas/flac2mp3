require "flac2mp3"
require "test/unit"

class Flac2mp3Test < Test::Unit::TestCase
	def setup 
		Dir.mkdir("test")
	end

	def teardown
 		`rm -rf test`
	end

	def testRecette
		donnees_wav=["52","49","46","46","24","08","00","00","57","41","56","45","66","6d","74","20","10","00","00","00","01","00","02","00","22","56","00","00","88","58","01","00","04","00","10","00","64","61","74","61","00","08","00","00","00","00","00","00","24","17","1e","f3","3c","13","3c","14","16","f9","18","f9","34","e7","23","a6","3c","f2","24","f2","11","ce","1a","0d"]
		file = File.new("./test/tmp.wav", "wb")
		donnees_wav.each {|hex| file.putc hex.to_i(16)}
		file.close
		`touch test/cover.jpg`
		`flac -V --totally-silent -f -T "ARTIST=artist" -T "TRACKNUMBER=1" -T "ALBUM=album" -T "TITLE=titre" -T "GENRE=Electronic" -T "DATE=2008" ./test/tmp.wav -o ./test/tmp.flac`
		`lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 ./test/tmp.wav ./test/tmp_attendu.mp3 && eyeD3  -a "artist" -n "1" -A "album" -t "titre" --add-image test/cover.jpg:FRONT_COVER: -G "Electronic" -Y "2008" --set-encoding=utf8 ./test/tmp_attendu.mp3`

		flac2mp3("./test/tmp.flac")
	 	
		assert_equal(File::Stat.new("./test/tmp_attendu.mp3").size, File::Stat.new("./test/tmp.mp3").size, "la taille des fichiers doit etre la meme")
		mp3tags_attendus = %x[id3tool ./test/tmp_attendu.mp3].gsub(/Filename:.*\n/,"")
		mp3tags_generes = %x[id3tool ./test/tmp.mp3].gsub(/Filename:.*\n/,"")
		assert_equal(mp3tags_attendus,mp3tags_generes, "les tags mp3 doivent etre les memes")
	end	

	def testTrouveFichiersFlac
		`mkdir -p test/r1 test/r2/r21 test/r3`
		`touch test/r1/f11.flac test/r1/f12.flac test/r2/r21/f21.flac`
		liste_attendue = ["./test/r1/f11.flac", "./test/r1/f12.flac", "./test/r2/r21/f21.flac"].sort()
		assert_equal(liste_attendue,  trouveFlac(".").sort())
		assert_equal(liste_attendue,  trouveFlac("./test/r1", "./test/r2").sort())
	end
end
