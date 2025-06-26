import re

# given a string with \_, return a list of matching pokemons
def pokemon_matcher(string):
    hint = string.replace("\_", ".")  # Replace _ with . for regex matching

    """
    # Iterate over the currently 1025 pokemons using the poke API
    # Filter them by regex matching
    response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=10000")
    data = response.json()
    """

    matching_pokemons = []

    # Read the pokemon names file
    with open("./data/pokemon_names.txt", "r") as file:
        pokemon_list = file.read().splitlines()

        for pokemon in pokemon_list:
            if re.fullmatch(hint, pokemon.lower()):
                matching_pokemons.append(pokemon)

        file.close()

    return matching_pokemons