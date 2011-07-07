require "flac2mp3"
require "test/unit"

class Flac2mp3Test < Test::Unit::TestCase
  def setup
    @flac2mp3 = Flac2mp3.new
  end

	def testLitMetaFlac_uneLigne
		assert_equal( {"TITRE"=>"titre"} ,@flac2mp3.litMetaFlac("TITRE=titre"))
	end

	def testLitMetaFlac_deuxLignes
		assert_equal( {"TITRE"=>"titre","ALBUM"=>"album"} ,@flac2mp3.litMetaFlac("TITRE=titre\nALBUM=album"))
	end

	def testLitMetaFlac_deuxLignesAvecMajusculeMinuscule
		assert_equal( {"TITRE"=>"titre","ALBUM"=>"album"} ,@flac2mp3.litMetaFlac("TiTrE=titre\nalbum=album"))
	end

	def testFlac2mp3_fichierNeTerminantPasParFlac
		assert_raise(RuntimeError) {@flac2mp3.flac2mp3("fichier.blah", "inutile")}
	end

	def testFlac2mp3_fichierInexistant
		assert_raise(RuntimeError) {@flac2mp3.flac2mp3("fichier_inexistant.flac", "inutile")}
	end
end
