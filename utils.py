import pokebase as pb

def print_menu(options: list, title: str):
  """
  Prints a numbered menu with a title.
  
  Args:
    options (list): List of menu options to display
    title (str): Title to display above the menu
  """
  print(f"{title}\n")
  for i, option in enumerate(options, 1):
    print(f"{i}. {option}")
  print("0. Exit")

def get_user_choice(options: list) -> int:
  """
  Prompts the user to select a valid option from the menu.
  
  Continues prompting until a valid choice is entered (0 to len(options)).
  
  Args:
    options (list): List of available options
    
  Returns:
    int: User's choice (0 for exit, 1-N for menu options)
  """
  while True:
    try:
      choice = int(input("\nSelection: "))
      if 0 <= choice <= len(options):
        return choice
    except ValueError:
      pass
    print("Invalid choice. Please try again.")

def get_available_languages() -> list:
  """
  Returns a list of available language codes from PokeAPI.
  
  Fetches all supported languages from the PokeAPI language endpoint.
  
  Returns:
    list: List of language codes (e.g., ['en', 'it', 'fr', 'es'])
  """
  response = pb.APIResourceList("language")  # List of dict with 'name'
  lang_list = [lang['name'] for lang in response]
  return lang_list