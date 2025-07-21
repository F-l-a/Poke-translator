import pokebase as pb
import json
import time
import os
import csv
from utils import print_menu, get_user_choice, get_available_languages

def translations_generator_manager():
  """
  Main manager function for the translations generator.
  
  Handles user interaction for selecting endpoint and target language,
  then generates the corresponding JSON translation file.
  """
  endpoints = [
    "ability", "berry", "item", "location", "move", "nature", "region", "type"
  ]
  
  print_menu(endpoints, "Choose an endpoint to generate JSON from:")
  endpoint_choice = get_user_choice(endpoints)
  if endpoint_choice == 0:
    return

  endpoint = endpoints[endpoint_choice - 1]

  lang_list = get_available_languages()
  print_menu(lang_list, "Choose target language:")
  lang_choice = get_user_choice(lang_list)
  if lang_choice == 0:
    return

  lang_code = lang_list[lang_choice - 1]

  print(f"\nGenerating {endpoint}-{lang_code}.json...")
  data = get_translations(endpoint, lang_code)
  if data:
    save_json(data, endpoint, lang_code)
    print(f"File '{endpoint}-{lang_code}.json' generated successfully!\n")
  else:
    print(f"No translations found for '{endpoint}' in '{lang_code}'. File not generated.\n")

def get_translations(endpoint: str, lang_code: str) -> dict:
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
  if missing_translations:
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
  directory = f"./translations/{lang_code}/missing"
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

def save_json(data: dict, endpoint: str, lang_code: str):
  """
  Saves translation data to a JSON file.
  
  Creates a formatted JSON file with the translation mappings for the specified
  endpoint and language. Files are organized in language-specific directories.
  
  Args:
    data (dict): Translation dictionary {english_name: translated_name}
    endpoint (str): Endpoint name for the filename
    lang_code (str): Language code for organizing files
  """
  directory = f"./translations/{lang_code}"
  filename = f"{directory}/{endpoint}-{lang_code}.json"
  os.makedirs(directory, exist_ok=True)
  with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)