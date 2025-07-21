import os
import json
import re
from pathlib import Path
from utils import print_menu, get_user_choice

def get_available_translation_languages():
  """
  Returns a list of available languages based on /translations folders
  that actually contain JSON translation files.
  
  Scans the translations directory for language folders and verifies
  they contain translation JSON files (excluding special_cases files).
  
  Returns:
    list: Sorted list of available language codes
  """
  translations_dir = "translations"
  languages = []
  
  if os.path.exists(translations_dir):
    for item in os.listdir(translations_dir):
      item_path = os.path.join(translations_dir, item)
      if os.path.isdir(item_path):
        # Check if folder contains at least one translation JSON file
        has_translations = False
        try:
          for file in os.listdir(item_path):
            if file.endswith('.json') and not file.startswith('special_cases'):
              has_translations = True
              break
        except (OSError, PermissionError):
          continue
        
        if has_translations:
          languages.append(item)
  
  return sorted(languages)

def translations_applicator_manager():
  """
  Main menu for the translation applicator.
  
  Handles user interaction for selecting target language and
  initiating the translation process for all input files.
  """
  languages = get_available_translation_languages()
  
  if not languages:
    print("No languages available in /translations folder")
    return
  
  print_menu(languages, "Choose target language:")
  lang_choice = get_user_choice(languages)
  
  if lang_choice == 0:
    return
  
  lang_code = languages[lang_choice - 1]
  apply_translations(lang_code)

def apply_translations(lang_code):
  """
  Applies translations for the specified language to files specified in info.xml.
  
  Reads the info.xml file to get the list of files to translate, processes them,
  and creates the same directory structure in the output folder.
  
  Args:
    lang_code (str): Target language code (e.g., 'it', 'fr', 'es')
  """
  # Ask for mod version
  print(f"\nTranslating to: {lang_code.upper()}")
  mod_version = input("Enter mod version (e.g., 1.0.0): ").strip()
  
  if not mod_version:
    print("Error: Mod version is required")
    return
  
  print(f"Using mod version: {mod_version}")
  
  # Paths
  input_dir = "input"
  info_xml_path = os.path.join(input_dir, "info.xml")
  translations_dir = f"translations/{lang_code}"
  output_dir = f"output/{lang_code.upper()}"
  special_cases_file = f"translations/{lang_code}/special_cases-{lang_code}.json"
  
  # Check if input directory and info.xml exist
  if not os.path.exists(input_dir):
    print(f"Error: Input folder '{input_dir}' not found")
    return
    
  if not os.path.exists(info_xml_path):
    print(f"Error: info.xml not found in '{input_dir}'")
    return
  
  # Parse info.xml to extract file paths
  input_files = []
  try:
    import xml.etree.ElementTree as ET
    tree = ET.parse(info_xml_path)
    root = tree.getroot()
    
    # Find all <string path="..."/> elements
    for string_element in root.find('strings').findall('string'):
      relative_path = string_element.get('path')
      if relative_path:
        # Convert relative path to absolute input path
        absolute_path = os.path.join(input_dir, relative_path)
        if os.path.exists(absolute_path):
          input_files.append(absolute_path)
          print(f"  Found file: {relative_path}")
        else:
          print(f"  Warning: File not found: {relative_path}")
    
    print(f"Extracted {len(input_files)} files from info.xml")
    
  except Exception as e:
    print(f"Error parsing info.xml: {e}")
    return
  
  if not input_files:
    print("No valid files found in info.xml")
    return
  
  # Create output directory structure
  Path(output_dir).mkdir(parents=True, exist_ok=True)
  
  # Copy and update info.xml to output directory
  output_info_path = os.path.join(output_dir, "info.xml")
  try:
    # Read original info.xml content
    with open(info_xml_path, 'r', encoding='utf-8') as f:
      info_content = f.read()
    
    # Keep original paths without modification
    updated_content = info_content
    
    # Update XML attributes using regex patterns
    import re
    
    # Update name attribute: add " ITA(ClientENG)"
    updated_content = re.sub(
      r'(<resource\s+name="[^"]*)"',
      r'\1 ITA(ClientENG)"',
      updated_content
    )
    
    # Update version attribute: add "-mod_{mod_version}"
    updated_content = re.sub(
      r'(<resource\s+[^>]*version=")([^"]*)"',
      rf'\1\2-mod_{mod_version}"',
      updated_content
    )
    
    # Update author attribute: add " (edited by FlaProGmr)"
    updated_content = re.sub(
      r'(<resource\s+[^>]*author=")([^"]*)"',
      r'\1\2 (edited by FlaProGmr)"',
      updated_content
    )
    
    # Update description attribute: add edited version info
    updated_content = re.sub(
      r'(<resource\s+[^>]*description=")([^"]*)"',
      r'\1\2 (edited version from: https://github.com/F-l-a/SupersStrings-MultiLanguage)"',
      updated_content
    )
    
    # Save updated info.xml to output
    with open(output_info_path, 'w', encoding='utf-8') as f:
      f.write(updated_content)
    
    print(f"Updated info.xml saved to: {output_info_path}")
    
  except Exception as e:
    print(f"Error updating info.xml: {e}")
    return
  
  # Copy icon.png if it exists in input directory
  icon_input_path = os.path.join(input_dir, "icon.png")
  if os.path.exists(icon_input_path):
    icon_output_path = os.path.join(output_dir, "icon.png")
    try:
      import shutil
      shutil.copy2(icon_input_path, icon_output_path)
      print(f"Copied icon.png to: {icon_output_path}")
    except Exception as e:
      print(f"Error copying icon.png: {e}")
  else:
    print(f"Warning: icon.png not found in {input_dir}")
  
  # Process each input file
  processed_files = []  # Keep track of files that were actually processed
  
  for input_file in input_files:
    # Calculate relative path from input directory
    relative_path = os.path.relpath(input_file, input_dir)
    
    # Ask user what to do with this file
    print(f"\nFile: {relative_path}")
    while True:
      choice = input("Translate this file? (Y)es / (N)o copy without translation / (S)kip: ").strip().upper()
      if choice in ['Y', 'YES', 'N', 'NO', 'S', 'SKIP']:
        break
      print("Invalid choice. Please enter Y, N, or S.")
    
    if choice in ['S', 'SKIP']:
      print(f"Skipping file: {relative_path}")
      continue  # Skip this file completely
    
    # Create corresponding output path with same directory structure
    output_file_path = os.path.join(output_dir, relative_path)
    output_file_dir = os.path.dirname(output_file_path)
    
    # Create output subdirectory if it doesn't exist
    if output_file_dir:
      Path(output_file_dir).mkdir(parents=True, exist_ok=True)
    
    if choice in ['N', 'NO']:
      # Copy file without translation
      try:
        # Keep original filename without modification
        import shutil
        shutil.copy2(input_file, output_file_path)
        print(f"Copied without translation: {input_file} -> {output_file_path}")
        processed_files.append(relative_path)
      except Exception as e:
        print(f"Error copying file {input_file}: {e}")
    else:
      # Translate the file (Y/YES)
      process_single_file(input_file, lang_code, translations_dir, output_file_path, special_cases_file, len(processed_files) + 1, len(input_files))
      processed_files.append(relative_path)
  
  # Update info.xml to remove references to skipped files
  if len(processed_files) < len(input_files):
    try:
      # Reread the updated info.xml to modify it further
      with open(output_info_path, 'r', encoding='utf-8') as f:
        final_info_content = f.read()
      
      # Remove string entries for files that were skipped
      import xml.etree.ElementTree as ET
      from xml.dom import minidom
      
      # Parse the XML
      root = ET.fromstring(final_info_content)
      strings_element = root.find('strings')
      
      # Get list of processed files with original naming
      processed_relative_paths = processed_files
      
      # Remove string elements for files that weren't processed
      for string_element in strings_element.findall('string'):
        path = string_element.get('path')
        if path not in processed_relative_paths:
          strings_element.remove(string_element)
          print(f"Removed from info.xml: {path}")
      
      # Save the updated info.xml with proper formatting
      rough_string = ET.tostring(root, 'utf-8')
      reparsed = minidom.parseString(rough_string)
      pretty = reparsed.toprettyxml(indent="    ")
      
      # Remove empty lines and fix encoding declaration
      lines = [line for line in pretty.split('\n') if line.strip()]
      final_content = '\n'.join(lines)
      
      with open(output_info_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
      
      print(f"Updated info.xml - removed {len(input_files) - len(processed_files)} skipped file references")
      
    except Exception as e:
      print(f"Error updating info.xml for skipped files: {e}")
  
  print(f"\nProcessing completed!")
  print(f"Total files processed: {len(processed_files)}/{len(input_files)}")
  print(f"Files skipped: {len(input_files) - len(processed_files)}")

def process_single_file(input_file, lang_code, translations_dir, output_file, special_cases_file, current_file=1, total_files=1):
  """
  Processes a single XML file with translations.
  
  Loads the file content, applies translations using JSON dictionaries
  and special cases, then saves the translated version to the specified output path.
  
  Args:
    input_file (str): Path to input XML file
    lang_code (str): Target language code
    translations_dir (str): Directory containing translation JSON files
    output_file (str): Full path for the output file
    special_cases_file (str): Path to special cases JSON file
    current_file (int): Current file number (1-based)
    total_files (int): Total number of files being processed
  """
  print(f"\n{'='*50}")
  print(f"Processing file: {input_file}")
  print(f"{'='*50}")
  
  # Keep original filename without modification
  # output_file is already set correctly by the caller
  try:
    with open(input_file, 'r', encoding='utf-8') as f:
      xml_content = f.read()
    
    print(f"XML file loaded as text ({len(xml_content)} characters)")
    
  except IOError as e:
    print(f"Error reading file: {e}")
    return
  
  # Load special cases
  special_cases = {}
  global_add_translations = {}
  global_no_translation_ids = set()
  global_override_translations = {}  # Store override translations globally
  global_transform_translations = {}  # Store transform translations globally
  add_block_data = {}  # Initialize add_block_data
  
  if os.path.exists(special_cases_file):
    try:
      with open(special_cases_file, 'r', encoding='utf-8') as f:
        special_cases_data = json.load(f)
        
        # Handles global add_translation
        if "add_translation" in special_cases_data:
          global_add_translations = special_cases_data["add_translation"].get("translations", {})
          print(f"Loaded {len(global_add_translations)} additional global translations")
          del special_cases_data["add_translation"]
        
        # Save add_block to apply after translations
        add_block_data = {}
        if "add_block" in special_cases_data:
          add_block_data = special_cases_data["add_block"]
          print(f"Detected {len(add_block_data)} files for add_block (application deferred)")
          del special_cases_data["add_block"]
        
        # Handles global override_translation
        if "override_translation" in special_cases_data:
          override_translation_ids = special_cases_data["override_translation"].get("ids", [])
          
          # Process override translations
          for id_entry in override_translation_ids:
            # Handle structure with objects
            id_item = id_entry.get("id", "")
            translation = id_entry.get("translation", "")
            reason = id_entry.get("reason", "")
            
            if "-" in id_item and id_item.replace("-", "").replace(".", "").isdigit():
              # It's a range: "101-105" or "1000-1050"
              try:
                start, end = id_item.split("-")
                start_id = int(start)
                end_id = int(end)
                
                # Add all IDs in the range with the same translation
                for id_num in range(start_id, end_id + 1):
                  global_override_translations[str(id_num)] = {
                    "translation": translation,
                    "reason": reason
                  }
                
                reason_info = f" ({reason})" if reason else ""
                print(f"Expanded override_translation range {id_item} into {end_id - start_id + 1} IDs{reason_info}")
              except ValueError:
                print(f"Error parsing override_translation range: {id_item}")
            else:
              # Single ID
              global_override_translations[id_item] = {
                "translation": translation,
                "reason": reason
              }
              reason_info = f" ({reason})" if reason else ""
              print(f"Added override_translation ID: {id_item}{reason_info}")
          
          print(f"Loaded {len(global_override_translations)} IDs for global override_translation")
          del special_cases_data["override_translation"]
        
        # Handles global transform_translation
        if "transform_translation" in special_cases_data:
          transform_translation_ids = special_cases_data["transform_translation"].get("ids", [])
          
          # Process transform translations
          for id_entry in transform_translation_ids:
            # Handle structure with objects
            id_item = id_entry.get("id", "")
            patterns = id_entry.get("patterns", [])
            reason = id_entry.get("reason", "")
            
            if "-" in id_item and id_item.replace("-", "").replace(".", "").isdigit():
              # It's a range: "101-105" or "1000-1050"
              try:
                start, end = id_item.split("-")
                start_id = int(start)
                end_id = int(end)
                
                # Add all IDs in the range with the same patterns
                for id_num in range(start_id, end_id + 1):
                  global_transform_translations[str(id_num)] = {
                    "patterns": patterns,
                    "reason": reason
                  }
                
                reason_info = f" ({reason})" if reason else ""
                print(f"Expanded transform_translation range {id_item} into {end_id - start_id + 1} IDs{reason_info}")
              except ValueError:
                print(f"Error parsing transform_translation range: {id_item}")
            else:
              # Single ID
              global_transform_translations[id_item] = {
                "patterns": patterns,
                "reason": reason
              }
              reason_info = f" ({reason})" if reason else ""
              print(f"Added transform_translation ID: {id_item}{reason_info}")
          
          print(f"Loaded {len(global_transform_translations)} IDs for global transform_translation")
          del special_cases_data["transform_translation"]
        # Handles global no_translation
        if "no_translation" in special_cases_data:
          no_translation_ids = special_cases_data["no_translation"].get("ids", [])
          
          # Expand ranges in no_translation IDs
          for id_entry in no_translation_ids:
            # Handle structure with objects
            id_item = id_entry.get("id", "")
            comment = id_entry.get("comment", "")
            
            if "-" in id_item and id_item.replace("-", "").replace(".", "").isdigit():
              # It's a range: "101-105" or "1000-1050"
              try:
                start, end = id_item.split("-")
                start_id = int(start)
                end_id = int(end)
                
                # Add all IDs in the range
                for id_num in range(start_id, end_id + 1):
                  global_no_translation_ids.add(str(id_num))
                
                comment_info = f" ({comment})" if comment else ""
                print(f"Expanded no_translation range {id_item} into {end_id - start_id + 1} IDs{comment_info}")
              except ValueError:
                print(f"Error parsing no_translation range: {id_item}")
            else:
              # Single ID
              global_no_translation_ids.add(id_item)
              comment_info = f" ({comment})" if comment else ""
              print(f"Added no_translation ID: {id_item}{comment_info}")
          
          print(f"Loaded {len(global_no_translation_ids)} IDs for global no_translation")
          del special_cases_data["no_translation"]
        
        # Expand ranges in IDs
        for key, value in special_cases_data.items():
          if "-" in key and key.replace("-", "").replace(".", "").isdigit():
            # It's a range: "101-105" or "1000-1050"
            try:
              start, end = key.split("-")
              start_id = int(start)
              end_id = int(end)
              
              # Add all IDs in the range
              for id_num in range(start_id, end_id + 1):
                special_cases[str(id_num)] = value
              
              print(f"Expanded range {key} into {end_id - start_id + 1} IDs")
            except ValueError:
              print(f"Error parsing range: {key}")
          else:
            # Single ID
            special_cases[key] = value
        
        print(f"Loaded {len(special_cases)} special cases from {special_cases_file}")
        
    except (json.JSONDecodeError, IOError) as e:
      print(f"Error loading special cases: {e}")
  
  # Load all JSON translation files for the selected language
  # Load different types of translations separately to handle context
  translations = {}
  type_translations = {}
  move_translations = {}
  ability_translations = {}
  item_translations = {}
  
  if os.path.exists(translations_dir):
    # Load generic translations
    for filename in os.listdir(translations_dir):
      if filename.endswith('.json'):
        try:
          with open(os.path.join(translations_dir, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if filename.startswith('type-'):
              type_translations.update(data)
              print(f"Loaded types file: {filename} ({len(data)} translations)")
            elif filename.startswith('move-'):
              move_translations.update(data)
              print(f"Loaded moves file: {filename} ({len(data)} translations)")
            elif filename.startswith('ability-'):
              ability_translations.update(data)
              print(f"Loaded abilities file: {filename} ({len(data)} translations)")
            elif filename.startswith('item-'):
              item_translations.update(data)
              print(f"Loaded items file: {filename} ({len(data)} translations)")
            else:
              translations.update(data)
              print(f"Loaded generic file: {filename} ({len(data)} translations)")
        except (json.JSONDecodeError, IOError) as e:
          print(f"Error loading {filename}: {e}")
  
  # Add global additional translations to base translations
  if global_add_translations:
    translations.update(global_add_translations)
    print(f"Added {len(global_add_translations)} global translations to base dictionary")
  
  if not any([translations, type_translations, move_translations, ability_translations, item_translations]):
    print(f"No translations found for language '{lang_code}'")
    return
  
  total_translations = len(translations) + len(type_translations) + len(move_translations) + len(ability_translations) + len(item_translations)
  context_specific_count = len(type_translations) + len(move_translations) + len(ability_translations) + len(item_translations)
  print(f"Loaded {total_translations} translations for '{lang_code}' (context-specific: {context_specific_count})")
  
  def get_contextual_translation(english_term, context_text):
    """
    Decides which translation to use based on context.
    
    Args:
      english_term (str): English term to translate
      context_text (str): Context text for analysis
      
    Returns:
      str or None: Translated term or None if no translation found
    """
    context_lower = context_text.lower()
    
    # If text is very long (>50 chars) or contains complete sentences, 
    # it's probably a description/dialogue → don't translate technical terms like "Psychic"
    is_description = (
      len(context_text) > 50 or 
      any(phrase in context_lower for phrase in [
        'hello', 'hi ', 'thank you', 'would you like', 'do you want', 
        'i am', 'i can', 'it is', 'the user', 'the target', 'this move',
        'you have', 'sorry', 'congratulations', 'welcome'
      ])
    )
    
    # For descriptions, don't translate single technical terms like "Psychic"
    if is_description and len(english_term.split()) == 1:
      return None
    
    # MAX PRIORITY: Special check for parentheses - always types
    if '(' in context_text and ')' in context_text:
      # Extract parentheses content
      parentheses_match = re.search(r'\(([^)]+)\)', context_text)
      if parentheses_match and english_term == parentheses_match.group(1):
        # It's parentheses content → always a type
        if english_term in type_translations:
          return type_translations.get(english_term)
    
    # Check first in category-specific translations
    # 2. Check if it's an item
    if english_term in item_translations:
      return item_translations.get(english_term)
    
    # 3. Check if it's a move
    if english_term in move_translations:
      return move_translations.get(english_term)
    
    # 4. Check if it's an ability
    if english_term in ability_translations:
      return ability_translations.get(english_term)
    
    # 5. Check if it's a type with context indicators
    type_indicators = [
      'incense', 'plate', 'berry', 'gem', 'type', 'resistance', 'weakness',
      'power', 'boost', 'stone', 'charm'
    ]
    
    if any(indicator in context_lower for indicator in type_indicators) and english_term in type_translations:
      return type_translations.get(english_term)
    
    # 6. Context indicators for moves (only for short names, not descriptions)
    move_indicators = [
      'learns', 'teach', 'tutor', 'tm', 'level up', 'move', 'attack', 'skill'
    ]
    
    if not is_description and any(indicator in context_lower for indicator in move_indicators) and english_term in move_translations:
      return move_translations.get(english_term)
    
    # 7. Context indicators for abilities
    ability_indicators = [
      'ability', 'abilities', 'hidden', 'effect', 'activates'
    ]
    
    if any(indicator in context_lower for indicator in ability_indicators) and english_term in ability_translations:
      return ability_translations.get(english_term)
    
    # 8. Fallback: generic translations for short names or complete translation
    if len(context_text.split()) <= 3 or english_term == context_text:
      return translations.get(english_term)
    
    return None
  
  # Combine all translations for sorting and pre-compile patterns
  all_terms = set()
  all_terms.update(translations.keys())
  all_terms.update(type_translations.keys()) 
  all_terms.update(move_translations.keys())
  all_terms.update(ability_translations.keys())
  all_terms.update(item_translations.keys())
  
  # Sort by decreasing length to prioritize more specific ones
  sorted_terms = sorted(all_terms, key=len, reverse=True)
  
  # Pre-compile regex patterns to improve performance
  compiled_patterns = []
  for english_term in sorted_terms:
    # Intelligent word boundary handling for terms with punctuation
    escaped_term = re.escape(english_term)
    
    # If the term ends with punctuation, don't use word boundary at the end
    if english_term[-1] in '.!?,:;':
      pattern = re.compile(r'\b' + escaped_term, re.IGNORECASE)
    # If the term starts with punctuation, don't use word boundary at the beginning  
    elif english_term[0] in '.!?,:;':
      pattern = re.compile(escaped_term + r'\b', re.IGNORECASE)
    # Normal term with full word boundary
    else:
      pattern = re.compile(r'\b' + escaped_term + r'\b', re.IGNORECASE)
    
    compiled_patterns.append((pattern, english_term))
  
  print(f"Processing file: {input_file} -> {output_file}")
  print(f"Compiled regex patterns: {len(compiled_patterns)}")
  
  # Find all string tags with regex that includes the ID
  string_pattern = r'(<string\s+id="([^"]+)"[^>]*>)(.*?)(</string>)'
  
  total_elements = len(re.findall(string_pattern, xml_content, re.DOTALL))
  current = 0
  translated_count = 0
  not_translated_count = 0
  special_cases_applied = 0
  
  def replace_content(match):
    nonlocal current, translated_count, not_translated_count, special_cases_applied
    
    current += 1
    percent = (current / total_elements) * 100
    
    opening_tag = match.group(1)
    string_id = match.group(2)
    original_text = match.group(3).strip()
    closing_tag = match.group(4)
    
    # Skip empty elements
    if not original_text:
      return match.group(0)
    
    # ABSOLUTE PRIORITY: Check global override_translation first
    if string_id in global_override_translations:
      override_data = global_override_translations[string_id]
      translated_text = override_data.get("translation", "")
      reason = override_data.get("reason", "Global override")
      
      # Always apply override_translation, even if translation is empty
      translated_count += 1
      special_cases_applied += 1
      print(f"[File {current_file}/{total_files}] [{current:04}/{total_elements} - {percent:.1f}%] - [GLOBAL_OVERRIDE] ID:{string_id} - {reason}")
      print(f"  [EN] {original_text} = [{lang_code.upper()}] {translated_text}")
      return f"{opening_tag}{translated_text}{closing_tag}"

    # ABSOLUTE PRIORITY: Check global no_translation
    if string_id in global_no_translation_ids:
      not_translated_count += 1
      special_cases_applied += 1
      print(f"[File {current_file}/{total_files}] [{current:04}/{total_elements} - {percent:.1f}%] - [NO_TRANSLATION] ID:{string_id} - Global category")
      return match.group(0)  # Returns original text without changes

    # HIGH PRIORITY: Check global transform_translation
    if string_id in global_transform_translations:
      transform_data = global_transform_translations[string_id]
      patterns = transform_data.get("patterns", [])
      reason = transform_data.get("reason", "Global transform")
      
      if patterns:
        special_cases_applied += 1
        
        for pattern_config in patterns:
          regex_pattern = pattern_config.get("regex")
          template = pattern_config.get("template")
          description = pattern_config.get("description", "Transformation")
          
          if not regex_pattern or not template:
            continue
            
          regex_match = re.search(regex_pattern, original_text)
          if regex_match:
            # Prepare template variables
            template_vars = {
              "original": original_text,
              "match": regex_match.group(0)
            }
            
            # Add captured groups
            for i, group in enumerate(regex_match.groups(), 1):
              template_vars[f"group{i}"] = group if group else ""
            
            # Search translations for the main term (group 1 or complete text)
            main_term = regex_match.group(1) if len(regex_match.groups()) > 0 else original_text
            translated_term = None
            
            # Search in additional global translations first
            if main_term in global_add_translations:
              translated_term = global_add_translations[main_term]
            # Then search with contextual function
            else:
              translated_term = get_contextual_translation(main_term, original_text)
            
            if translated_term:
              template_vars["translated"] = translated_term
            else:
              template_vars["translated"] = main_term  # Fallback to original term
            
            # Apply template
            try:
              result = template.format(**template_vars)
              translated_count += 1
              print(f"[File {current_file}/{total_files}] [{current:04}/{total_elements} - {percent:.1f}%] - [GLOBAL_TRANSFORM] ID:{string_id} - {description}")
              print(f"  [EN] {original_text} = [{lang_code.upper()}] {result}")
              return f"{opening_tag}{result}{closing_tag}"
            except KeyError as e:
              print(f"Template error for ID {string_id}: missing variable {e}")
            
            # If the pattern matched, don't try other patterns
            break
    
    # MAXIMUM PRIORITY: Check special cases
    if string_id in special_cases:
      case = special_cases[string_id]
      case_type = case.get("type")
      
      if case_type == "no_translation":
        not_translated_count += 1
        special_cases_applied += 1
        reason = case.get("reason", "Special case")
        print(f"[File {current_file}/{total_files}] [{current:04}/{total_elements} - {percent:.1f}%] - [SKIP] ID:{string_id} - {reason}")
        return match.group(0)  # Returns original text without changes
      
      elif case_type == "add_translation":
        # Adds temporary translations for this specific string
        temp_translations = case.get("translations", {})
        if temp_translations:
          special_cases_applied += 1
          # Use temporary translations together with normal ones
          working_text = original_text
          
          # First apply temporary translations (priority)
          for english_term, temp_translation in temp_translations.items():
            pattern_temp = re.compile(r'\b' + re.escape(english_term) + r'\b')
            if pattern_temp.search(working_text):
              working_text = pattern_temp.sub(temp_translation, working_text)
          
          # If at least one temporary translation was applied
          if working_text != original_text:
            translated_count += 1
            reason = case.get("reason", "Added translation")
            print(f"[File {current_file}/{total_files}] [{current:04}/{total_elements} - {percent:.1f}%] - [ADD_TRANS] ID:{string_id} - {reason}")
            print(f"  [EN] {original_text} = [{lang_code.upper()}] {working_text}")
            return f"{opening_tag}{working_text}{closing_tag}"
          # If no temporary translation was applied, continue with normal logic
    
    # Normal translation logic (only if not handled by special cases)
    translated_text = None
    
    # First try a complete translation with context
    contextual_translation = get_contextual_translation(original_text, original_text)
    if contextual_translation:
      translated_text = contextual_translation
    else:
      # If no complete translation is found, try partial translations
      # Use pre-compiled patterns to improve performance
      working_text = original_text
      
      for compiled_pattern, english_term in compiled_patterns:
        if compiled_pattern.search(working_text):
          # Use contextual translation for each term
          context_translation = get_contextual_translation(english_term, original_text)
          if context_translation:
            working_text = compiled_pattern.sub(context_translation, working_text)
      
      # If the text has changed, it means we made at least one partial translation
      if working_text != original_text:
        translated_text = working_text
    
    # Additional check: if the translated text still contains parentheses with English types,
    # also try to translate the parentheses content (ALWAYS as types)
    if translated_text and '(' in translated_text and ')' in translated_text:
      def translate_parentheses_content(match):
        content = match.group(1)
        # Parentheses ALWAYS indicate a type, so force type_translations
        if content in type_translations:
          return f"({type_translations[content]})"
        return match.group(0)
      
      translated_text = re.sub(r'\(([^)]+)\)', translate_parentheses_content, translated_text)
    
    if translated_text:
      translated_count += 1
      status = f"[EN] {original_text} = [{lang_code.upper()}] {translated_text}"
      print(f"[File {current_file}/{total_files}] [{current:04}/{total_elements} - {percent:.1f}%] - {status}")
      return f"{opening_tag}{translated_text}{closing_tag}"
    else:
      not_translated_count += 1
      status = f"[EN] {original_text} = [NO TRANSLATION]"
      print(f"[File {current_file}/{total_files}] [{current:04}/{total_elements} - {percent:.1f}%] - {status}")
      return match.group(0)
  
  # Apply translations using re.sub with a function
  xml_content = re.sub(string_pattern, replace_content, xml_content, flags=re.DOTALL)
  
  # Apply add_block AFTER translations (to not translate added content)
  if add_block_data:
    for file_path, block_info in add_block_data.items():
      # Normalize paths for comparison (convert separators and compare relative paths)
      normalized_input = input_file.replace("\\", "/")
      if file_path == normalized_input:  # Compare normalized paths
        content_to_add = block_info.get("content", "")
        reason = block_info.get("reason", "Block addition")
        
        if content_to_add:
          # Find the last closing tag (presumably the main container)
          last_close_tag_pos = xml_content.rfind("</" )
          if last_close_tag_pos != -1:
            # Insert content before the last closing tag
            xml_content = (xml_content[:last_close_tag_pos] + content_to_add + "\n" + xml_content[last_close_tag_pos:])
            print(f"Added block to file {file_path}: {reason}")
            print(f"Content added: {len(content_to_add)} characters")
          else:
            print(f"Error: closing tag not found to add block in {file_path}")
  
  # Save translated XML
  try:
    # Save the modified XML content
    with open(output_file, 'w', encoding='utf-8') as f:
      f.write(xml_content)
    
    print(f"\nProcessing completed!")
    print(f"Translated elements: {translated_count}/{total_elements}. Non-translated elements: {not_translated_count}/{total_elements}")
    print(f"Special cases applied: {special_cases_applied}")
    print(f"File saved: {output_file}")
  except IOError as e:
    print(f"Error saving file: {e}")
