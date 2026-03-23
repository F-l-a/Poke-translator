from translations_generator import translations_generator_manager
from translations_applicator import translations_applicator_manager
from utils import print_menu, get_user_choice
from cache_manager import manage_cache

def main():
  """
  Main entry point for the Poke-translator application.
  
  Provides a menu-driven interface for:
  - Generating JSON translation files from PokeAPI
  - Applying translations to XML files
  - Managing PokeAPI cache
  """
  while True:
    print_menu(
      ["Generate JSON Translations", "Apply Translations", "Manage PokeAPI Cache"],
      "\n====\nMain Menu"
    )
    main_choice = get_user_choice(["Generate JSON Translations", "Apply Translations", "Manage PokeAPI Cache"])

    if main_choice == 0:
      print("Exiting.")
      break
    elif main_choice == 1:
      print_menu(["pokeapi", "PokemmoClientDump"], "Select translation source:")
      source_choice = get_user_choice(["pokeapi", "PokemmoClientDump"])
      if source_choice == 0:
        continue
      if source_choice == 1:
        source = "pokeapi"
      elif source_choice == 2:
        source = "PokemmoClientDump"
      else:
        print("Invalid selection.")
        continue
      base_path = f"./translations/{source}"
      translations_generator_manager(base_path)
    elif main_choice == 2:
      print_menu(["pokeapi", "PokemmoClientDump - not implemented yet"], "Select translation source:")
      source_choice = get_user_choice(["pokeapi", "PokemmoClientDump"])
      if source_choice == 0:
        continue
      elif source_choice == 1:
        source = "pokeapi"
        base_path = f"./translations/{source}"
        translations_applicator_manager(base_path)
      elif source_choice == 2:
        print("This option is not yet implemented.")
        continue
    elif main_choice == 3:
      manage_cache()

if __name__ == "__main__":
  main()