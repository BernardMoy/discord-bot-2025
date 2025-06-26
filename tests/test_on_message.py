from pokemon_matcher import pokemon_matcher
def test_pokemon_matcher():
    hint = r'dri\_\_\_\_n'
    matching_results = pokemon_matcher(hint)
    assert matching_results == ['drifloon']