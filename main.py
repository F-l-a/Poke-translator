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
      translations_generator_manager()
    elif main_choice == 2:
      translations_applicator_manager()
    elif main_choice == 3:
      manage_cache()

if __name__ == "__main__":
  main()