import shelve
import os
from pokebase import cache
from utils import print_menu, get_user_choice

def display_cache():
  """
  Displays the contents of the PokeAPI cache.
  
  Shows all cached keys and allows the user to inspect specific entries.
  Handles cases where cache file doesn't exist or is empty.
  """
  print(f"\nReading cache: {cache.API_CACHE}\n")

  if not os.path.exists(cache.API_CACHE + ".dat"):
    print("No cache file found.")
    return

  try:
    with shelve.open(cache.API_CACHE) as db:
      keys = list(db.keys())
      if not keys:
        print("Cache is empty.")
        return

      print("Keys found in cache:\n")
      for i, key in enumerate(keys, 1):
        print(f"{i}. {key}")

      print("\n0. Back to menu")
      choice = input("\nIf you want to see the content of a key, enter the corresponding number: ")

      if choice.isdigit() and 1 <= int(choice) <= len(keys):
        selected_key = keys[int(choice) - 1]
        print(f"\nContent of '{selected_key}':\n")
        print(db[selected_key])
  except Exception as e:
    print(f"Error reading cache: {e}")

def get_cache_path():
  """
  Returns the cache file path.
  
  Returns:
    str: Path to the PokeAPI cache file
  """
  return cache.API_CACHE

def manage_cache():
  """
  Main cache management function.
  
  Provides a menu-driven interface for cache operations including
  viewing cache contents and displaying cache file location.
  """
  print_menu(
    ["Display Cache", "Display Cache Path"],
    "Cache Management"
  )
  cache_choice = get_user_choice(["Display Cache", "Display Cache Path"])

  if cache_choice == 1:
    display_cache()
  elif cache_choice == 2:
    print(f"\nCache path: {get_cache_path()}\n")