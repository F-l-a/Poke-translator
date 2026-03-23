import pokebase as pb
import json
import time
import os
import csv
from utils import print_menu, get_user_choice, get_available_languages

def get_client_dump_languages() -> list:
  """
  Returns a list of available languages based on folder names in the
  PokemmoClientDumps directory, excluding 'en'.
  """
  input_dir = "./input/PokemmoClientDumps"
  en_dir_path = os.path.join(input_dir, 'en')

  try:
    if not os.path.isdir(en_dir_path):
      print(f"Error: English 'en' directory not found at '{en_dir_path}'")
      return []
    
    langs = [name for name in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, name)) and name != 'en']
    return sorted(langs)
  except FileNotFoundError:
    print(f"Error: Directory not found at '{input_dir}'")
    return []

def translations_generator_manager(base_path: str):
  """
  Main manager function for the translations generator.
  
  Handles user interaction for selecting endpoint and target language,
  then generates the corresponding JSON translation file.
  """
  if 'PokemmoClientDump' in base_path:
    endpoints = ["pokemon-species", "move", "ability", "region", "egg-group"]
    lang_list = get_client_dump_languages()
  else:
    endpoints = [
      "ability", "berry", "item", "location", "move", "nature", "region", "type", "egg-group", "pokemon-species"
    ]
    lang_list = get_available_languages()
  
  menu_endpoints = ["Generate All"] + endpoints
  print_menu(menu_endpoints, "Choose an endpoint to generate JSON from:")
  endpoint_choice = get_user_choice(menu_endpoints)
  if endpoint_choice == 0:
    return

  print_menu(lang_list, "Choose target language:")
  lang_choice = get_user_choice(lang_list)
  if lang_choice == 0:
    return

  lang_code = lang_list[lang_choice - 1]

  endpoints_to_process = []
  selected_option = menu_endpoints[endpoint_choice - 1]
  if selected_option == "Generate All":
    endpoints_to_process = endpoints
  else:
    endpoints_to_process.append(selected_option)

  for endpoint in endpoints_to_process:
    print(f"\nGenerating {endpoint}-{lang_code}.json...")
    data = get_translations(endpoint, lang_code, base_path)
    if data:
      save_json(data, endpoint, lang_code, base_path)
      print(f"File '{endpoint}-{lang_code}.json' generated successfully!\n")
    else:
      print(f"No translations found for '{endpoint}' in '{lang_code}'. File not generated.\n")

def get_translations(endpoint: str, lang_code: str, base_path: str) -> dict:
  """
  Retrieves translations from English to the specified language for a PokeAPI endpoint.
  
  Fetches all resources from the given endpoint and extracts their names in both
  English and the target language. Also generates a CSV file with missing translations
  for potential manual completion.

  Args:
    endpoint (str): Endpoint name (e.g., 'item', 'move', 'ability')
    lang_code (str): Target language code (e.g., 'it', 'fr', 'es')

  Returns:
    dict: Dictionary mapping {english_name: translated_name}
  """

  if 'PokemmoClientDump' in base_path:
    # --- Configuration-driven extraction for Client Dumps ---
    
    def _extract_id_name_map(data, config):
      """Helper to extract a map of {id: name} from dump data based on config."""
      item_map = {}
      item_path = config.get("item_path")
      id_path = config["id_path"]
      name_path = config["name_path"]

      for top_level_item in data:
        items_to_process = []
        if item_path:
          nested_items = top_level_item.get(item_path, [])
          if isinstance(nested_items, list):
            items_to_process = nested_items
        else:
          items_to_process = [top_level_item]
        
        for item in items_to_process:
          item_id = item.get(id_path)
          item_name = item.get(name_path, "").strip()
          if item_id is not None and item_name:
            item_map[item_id] = item_name
      return item_map

    try:
      with open('./input/PokemmoClientDumps/client_dump_config.json', 'r', encoding='utf-8') as f:
        configs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
      print(f"Error reading or parsing config file: {e}")
      return {}

    endpoint_config = next((c for c in configs if c['endpoint'] == endpoint), None)

    if not endpoint_config:
      print(f"No configuration found for endpoint '{endpoint}'")
      return {}
      
    file_name = endpoint_config["file"]
    en_file_path = f"./input/PokemmoClientDumps/en/{file_name}"
    lang_file_path = f"./input/PokemmoClientDumps/{lang_code}/{file_name}"

    try:
      with open(en_file_path, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
      with open(lang_file_path, 'r', encoding='utf-8') as f:
        lang_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
      print(f"Error reading JSON files: {e}")
      return {}

    results = {}
    extractor_type = endpoint_config.get("extractor_type", "id_name_map")

    if extractor_type == "id_name_map":
      en_map = _extract_id_name_map(en_data, endpoint_config)
      lang_map = _extract_id_name_map(lang_data, endpoint_config)
      for item_id, en_name in en_map.items():
        lang_name = lang_map.get(item_id)
        if lang_name:
          results[en_name] = lang_name
        else:
          print(f"Warning: No translation found for ID {item_id} ('{en_name}')")
    
    elif extractor_type == "string_list_pairs":
      item_path = endpoint_config["item_path"]
      if len(en_data) != len(lang_data):
        print("Error: The number of top-level items do not match.")
        return {}
      
      for en_top_item, lang_top_item in zip(en_data, lang_data):
        if en_top_item.get("id") != lang_top_item.get("id"):
          print(f"Warning: Top-level ID mismatch, skipping item {en_top_item.get('id')}")
          continue
        
        en_list = en_top_item.get(item_path, [])
        lang_list = lang_top_item.get(item_path, [])

        if len(en_list) == len(lang_list):
          for en_str, lang_str in zip(en_list, lang_list):
            if en_str and lang_str:
              # Apply title case formatting specifically for egg-group
              if endpoint == "egg-group":
                en_str = en_str.title()
                lang_str = lang_str.title()
              
              if en_str not in results:
                results[en_str] = lang_str
        elif en_list or lang_list:
          print(f"Warning: List length mismatch for '{item_path}' in item ID {en_top_item.get('id')}")

    return results
  
  # Get all resources for this endpoint (APIResourceList handles pagination automatically)
  resource_list = pb.APIResourceList(endpoint)
  total = resource_list.count
  current = 0
  results = {}
  missing_translations = []

  print(f"Found {total} resources for endpoint '{endpoint}'. Starting processing...")

  # Get target language ID once for efficiency
  try:
    lang_resource = pb.APIResource('language', lang_code)
    lang_id = lang_resource.id
  except Exception as e:
    print(f"Error retrieving language ID for '{lang_code}': {e}")
    lang_id = None

  # Iterate through all resources
  for resource in resource_list:
    current += 1
    resource_name = resource.get("name")
    
    try:
      # Get specific resource details
      resource_data = pb.APIResource(endpoint, resource_name)
      
      # Find official English name
      english_name = next(
        (n.name for n in resource_data.names if n.language.name == "en"), 
        resource_name
      )
      
      # Find translated name in target language
      translated_name = next(
        (n.name for n in resource_data.names if n.language.name == lang_code), 
        None
      )

      if translated_name:
        results[english_name] = translated_name
        status = f"[EN] {english_name} = [{lang_code.upper()}] {translated_name}"
      else:
        status = f"[EN] {english_name} = [NO TRANSLATION]"
        # Add to missing translations list
        if lang_id is not None:
          missing_translations.append([resource_data.id, lang_id, english_name, ''])

      percent = (current / total) * 100
      print(f"[{current:04}/{total} - {percent:.1f}%] - {endpoint}/{resource_name} - {status}")
      
      # Reduced pause for better performance
      if current % 10 == 0:  # Pause every 10 requests instead of every request
        time.sleep(0.1)
      
    except Exception as e:
      print(f"[{current:04}/{total}] - Error processing {resource_name}: {e}")
      continue

  # Save missing translations to CSV
  if missing_translations and 'pokeapi' in base_path:
    save_missing_translations_csv(missing_translations, endpoint, lang_code)
    print(f"Saved {len(missing_translations)} missing translations in {endpoint}_names.csv")

  print(f"Processing completed. Found {len(results)} translations for '{lang_code}'.")
  return results

def save_missing_translations_csv(missing_translations: list, endpoint: str, lang_code: str):
  """
  Saves missing translations to a CSV file for manual completion.
  
  Creates a CSV file with missing translations that can be manually filled
  and potentially imported back into the translation system or PokeAPI.
  
  Args:
    missing_translations (list): List of rows [resource_id, language_id, english_name, '']
    endpoint (str): Endpoint name for the filename
    lang_code (str): Language code for organizing files
  """
  directory = f"./translations/pokeapi/{lang_code}/missing"
  filename = f"{directory}/{endpoint}_names.csv"
  os.makedirs(directory, exist_ok=True)
  
  # Check if file exists to add header only if necessary
  file_exists = os.path.isfile(filename)
  
  with open(filename, "a", encoding="utf-8", newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write header only if file is new
    if not file_exists:
      writer.writerow(['resource_id', 'language_id', 'english_name', 'translation'])
    
    # Write all missing translations
    writer.writerows(missing_translations)

def save_json(data: dict, endpoint: str, lang_code: str, base_path: str):
  """
  Saves translation data to a JSON file.
  
  Creates a formatted JSON file with the translation mappings for the specified
  endpoint and language. Files are organized in language-specific directories.
  
  Args:
    data (dict): Translation dictionary {english_name: translated_name}
    endpoint (str): Endpoint name for the filename
    lang_code (str): Language code for organizing files
  """
  directory = f"{base_path}/{lang_code}"
  filename = f"{directory}/{endpoint}-{lang_code}.json"
  os.makedirs(directory, exist_ok=True)
  with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)