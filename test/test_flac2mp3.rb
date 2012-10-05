require "flac2mp3"
require "test/unit"

class TestFlac2mp3 < Test::Unit::TestCase
  def setup
    @flac2mp3 = Flac2mp3.new
  end

	def test_lit_metaflac_une_ligne
		assert_equal( {"TITRE"=>"titre"} ,@flac2mp3.lit_meta_flac("TITRE=titre"))
	end

	def test_lit_meta_flac_deux_lignes
		assert_equal( {"TITRE"=>"titre","ALBUM"=>"album"} ,@flac2mp3.lit_meta_flac("TITRE=titre\nALBUM=album"))
	end

	def test_lit_meta_flac_deux_lignes_avec_majuscule_minuscule
		assert_equal( {"TITRE"=>"titre","ALBUM"=>"album"} ,@flac2mp3.lit_meta_flac("TiTrE=titre\nalbum=album"))
  end

  def test_lit_meta_flac_deux_lignes_avec_retour_chariot
    assert_equal( {"DESCRIPTION" => "Interprètes : Hot Chip, interprète", "TITRE"=>"titre"},
                   @flac2mp3.lit_meta_flac("DESCRIPTION=Interprètes : Hot Chip, interprète\nLabel : Domino Recording Co - Domino\nTITRE=titre"))
  end

  def test_flac2mp3_texte_avec_point_exclamation
    assert_equal( {"TITRE"=>"titre","ALBUM"=>"album"} ,@flac2mp3.lit_meta_flac("TiTrE=titre!\nalbum=album!"))
  end

  def test_flac2mp3_fichier_ne_terminant_pas_par_flac
    assert_raise(RuntimeError) {@flac2mp3.flac2mp3("fichier.blah", "inutile")}
  end

	def test_flac2mp3_fichier_inexistant
		assert_raise(RuntimeError) {@flac2mp3.flac2mp3("fichier_inexistant.flac", "inutile")}
	end
end
