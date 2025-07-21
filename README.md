# Poke-translator
A CLI tool in Python that generates multilingual JSON dictionaries using [PokeAPI](https://pokeapi.co) and applies translations to [SupersStrings](https://github.com/superworldsun/SupersStrings) files via key-value matching.
Italian translations are already present in this repository, but other languages are supported via PokeAPI.
## Usage Guide

1. **Clone the repository:**
   ```bash
   git clone https://github.com/F-l-a/Poke-translator
   cd Poke-translator
   ```

2. **Set up Python environment and install dependencies:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # <- On Windows | On Linux/Mac -> .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Add input files:**
   - Download [SupersStrings](https://github.com/superworldsun/SupersStrings) files (specifically `sws_strings_en.xml`)
   - Place them in the `./input` folder

4. **Run the translator:**
   ```bash
   python main.py
   ```

5. **Output:**
   - Translated files can be found in the `./output/{LANGUAGE}/` folder
   - You may want to change the `lang` and `lang_full` parameters in each file to match your PokeMMO client language

6. **If you want to use the tool another time:**
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


## CLI Debug - [Pokeapi.co](https://pokeapi.co) is simpler

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