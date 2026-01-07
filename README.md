[![Auto Release Translation](https://github.com/F-l-a/Poke-translator/actions/workflows/auto-release.yml/badge.svg)](https://github.com/F-l-a/Poke-translator/actions/workflows/auto-release.yml)
# Poke-translator
A CLI tool in Python that generates multilingual JSON dictionaries using [PokeAPI](https://pokeapi.co) and applies translations to [SupersStrings](https://github.com/superworldsun/SupersStrings) files via key-value matching.
Italian translations are already present in this repository, but other languages are supported via PokeAPI.

## Usage Guide

1. **Clone the repository with submodules:**
   ```bash
   git clone --recursive https://github.com/F-l-a/Poke-translator
   cd Poke-translator
   ```
   
   **Note:** The `--recursive` flag is important to automatically download the SupersStrings dependency.
   
   If you already cloned without `--recursive`, you can initialize the submodule with:
   ```bash
   git submodule update --init --recursive
   ```

2. **Set up Python environment and install dependencies:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # <- On Windows | On Linux/Mac -> .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Input files are automatically available:**
   - The [SupersStrings](https://github.com/superworldsun/SupersStrings) files are automatically downloaded as a Git submodule
   - The tool will use files from `./input/SupersStrings/SupersStoryStrings/` automatically

4. **Run the translator:**
   ```bash
   python main.py
   ```

   https://github.com/user-attachments/assets/5f3ede9a-5db9-454f-a476-014e22669bcb
   #### ProTip
   - You can delete the PokeAPI local cache after the generation of JSON files. This speeds up the generation of the next file because the database gets slow easily when generating many entries. You can find the path to the cache by selecting option `3` from the main menu.
   #### Notes
   - `sws_strings_en.xml`: Misc + Buttons + NPCs + Items + Natures -> Translate all
   - `sws_en_Unova_0.xml`: Gyms/E4 (End Battle) (Unova) + Pokedex -> Translate Pokedex
   - `sws_en_Unova_1.xml`: HMs (Unova) + NPCs + Gyms/E4 (Unova)
   - `sws_en_Sinnoh.xml`: HMs (Sinnoh) + NPCs + Gyms/E4 (Sinnoh)
   - `sws_en_Kanto.xml`: HMs (Kanto) + NPCs + Gyms/E4 (Kanto)
   - `sws_en_Johto.xml`: HMs (Johto) + NPCs + Gyms/E4 (Johto)
   - `sws_en_Hoenn.xml`: HMs (Hoenn) + NPCs + Gyms/E4 (Hoenn)

6. **Output:**
   - Translated files can be found in the `./output/{LANGUAGE}/` folder
   - You may want to change the `lang` and `lang_full` parameters in each `.xml` file to match your PokeMMO client language. The default is English

7. **If you want to use the tool another time:**
   ```bash
   .venv\Scripts\activate  # <- On Windows | On Linux/Mac -> .venv/bin/activate
   python main.py
   ```

## Useful [PokeAPI](https://pokeapi.co) Endpoints

- [x] ability:"https://pokeapi.co/api/v2/ability/"
- [x] berry:"https://pokeapi.co/api/v2/berry/"
- [x] item:"https://pokeapi.co/api/v2/item/"
- [some relevant translations for the italian language are missing] location:"https://pokeapi.co/api/v2/location/"
- [x] move:"https://pokeapi.co/api/v2/move/"
- [x] nature:"https://pokeapi.co/api/v2/nature/"
- [x] region:"https://pokeapi.co/api/v2/region/"
- [x] language:"https://pokeapi.co/api/v2/language/"


## CLI Debug - [Pokeapi.co](https://pokeapi.co) is simpler, use the web interface

### Try API endpoints from CLI
```python
import pokebase as pb
res = pb.APIResource('pokemon', 'pikachu')
```

### Discover available attributes and methods:
```python
dir(res)  # Shows all attributes and methods
vars(res)  # Shows instance attributes
help(res)  # Complete documentation
```

### Usage examples:
```python
res.name  # Pokémon name
res.id  # Pokémon ID  
res.types  # Pokémon types
res.abilities  # Pokémon abilities
res.stats  # Pokémon stats
```

### To explore a specific attribute:
```python
type(res.types)  # Data type
len(res.types)   # Length if it's a list
res.types[0]     # First element if it's a list
```

### To see all available endpoints:
```python
from pokebase.common import ENDPOINTS
print(ENDPOINTS)
```

***
## TODO (it)
- Colors in add_translations
- Fireworks
- Event elements (Christmas ones are broken)
