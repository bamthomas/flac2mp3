require "flac2mp3"
require "test/unit"

class Flac2mp3Test < Test::Unit::TestCase
  
	def setup
    @flac2mp3 = Flac2mp3.new
		Dir.mkdir("tmp")
	end

	def teardown
 		`rm -rf tmp`
	end

  def test_recette
    cree_fichier_flac("./tmp/tmp.flac")
    `lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 ./tmp/tmp.wav ./tmp/tmp_attendu.mp3 && eyeD3  -a "artist" -n "1" -A "album" -t "titre" --add-image ./tmp/cover.jpg:FRONT_COVER: -G "Electronic" -Y "2008" --set-encoding=utf8 ./tmp/tmp_attendu.mp3`
    
    @flac2mp3.flac2mp3("./tmp/tmp.flac","./")
  
    assert_equal(File::Stat.new("./tmp/tmp_attendu.mp3").size, File::Stat.new("./tmp/tmp.mp3").size, "la taille des fichiers doit etre la meme")
    mp3tags_attendus = %x[id3tool ./tmp/tmp_attendu.mp3].gsub(/Filename:.*\n/,"")
    mp3tags_generes = %x[id3tool ./tmp/tmp.mp3].gsub(/Filename:.*\n/,"")
    assert_equal(mp3tags_attendus,mp3tags_generes, "les tags mp3 doivent etre les memes")
  end
  
  def test_trouve_fichiers_flac
    `mkdir -p tmp/r1 tmp/r2/r21 tmp/r3`
  	`touch tmp/r1/f11.flac tmp/r1/f12.flac tmp/r2/r21/f21.flac`
    liste_attendue = ["./tmp/r1/f11.flac", "./tmp/r1/f12.flac", "./tmp/r2/r21/f21.flac"].sort()
    assert_equal(liste_attendue,  @flac2mp3.trouve_fichiers(".flac", "./").sort())
    assert_equal(liste_attendue,  @flac2mp3.trouve_fichiers(".flac", "./tmp/r1", "./tmp/r2").sort())
  end

	def test_convert_arborescence
		`mkdir -p tmp/r1 tmp/r2/r21 tmp/r3`
		cree_fichier_flac("tmp/r1/f11.flac")
		cree_fichier_flac("tmp/r1/f12.flac")
		cree_fichier_flac("tmp/r2/r21/f21.flac")
    begin
      # il faut etre dans le repertoire racine des flacs
      Dir.chdir("tmp")

      @flac2mp3.trouve_fichiers(".flac", "./").each {|flac| @flac2mp3.flac2mp3(flac, "mp3")}

      assert_equal ["./mp3/r1/f11.mp3", "./mp3/r1/f12.mp3", "./mp3/r2/r21/f21.mp3"].sort, @flac2mp3.trouve_fichiers(".mp3", "./").sort
    ensure Dir.chdir("..")
    end
  end

  def cree_fichier_flac(nom)
    if !File.exist?("./tmp/tmp.wav")
      donnees_wav=["52","49","46","46","24","08","00","00","57","41","56","45","66","6d","74","20","10","00","00","00","01","00","02","00","22","56","00","00","88","58","01","00","04","00","10","00","64","61","74","61","00","08","00","00","00","00","00","00","24","17","1e","f3","3c","13","3c","14","16","f9","18","f9","34","e7","23","a6","3c","f2","24","f2","11","ce","1a","0d"]
      file = File.new("./tmp/tmp.wav", "wb")
      donnees_wav.each {|hex| file.putc hex.to_i(16)}
      file.close
    end
    image = File.dirname(nom) + "/cover.jpg"
    `touch #{image}`
    `flac -V --totally-silent -f -T "ARTIST=artist" -T "TRACKNUMBER=1" -T "ALBUM=album" -T "TITLE=titre" -T "GENRE=Electronic" -T "DATE=2008" ./tmp/tmp.wav -o #{nom}`
  end
end
