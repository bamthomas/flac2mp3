require "flac2mp3"
require "test/unit"

class Flac2mp3Test < Test::Unit::TestCase
	def testLitMetaFlac_uneLigne
		assert_equal( {"TITRE"=>"titre"} ,litMetaFlac("TITRE=titre"))
	end

	def testLitMetaFlac_deuxLignes
		assert_equal( {"TITRE"=>"titre","ALBUM"=>"album"} ,litMetaFlac("TITRE=titre\nALBUM=album"))
	end

	def testLitMetaFlac_deuxLignesAvecMajusculeMinuscule
		assert_equal( {"TITRE"=>"titre","ALBUM"=>"album"} ,litMetaFlac("TiTrE=titre\nalbum=album"))
	end

	def testFlac2mp3_fichierNeTerminantPasParFlac
		assert_raise(RuntimeError) {flac2mp3("fichier.blah")}
	end

	def testFlac2mp3_fichierInexistant
		assert_raise(RuntimeError) {flac2mp3("fichier_inexistant.flac")}
	end
end
