#!/usr/bin/env python3
"""
Test script for automated translation logic
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
import shutil
import re
from pathlib import Path

def apply_translations_automated(lang_code, mod_version):
    """
    Automated version of apply_translations with pre-configured choices.
    
    This function replicates the main apply_translations logic but with
    automated choices instead of user input:
    - sws_strings_en.xml: Translate (Y)
    - All other files: Copy only (N)
    
    Args:
        lang_code (str): Target language code (e.g., 'it')
        mod_version (str): Mod version string (e.g., '1.0.1a')
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    print(f"Starting automated translation to: {lang_code.upper()}")
    print(f"Using mod version: {mod_version}")
    
    # Paths
    input_dir = os.path.join("input", "SupersStrings", "SupersStoryStrings")
    info_xml_path = os.path.join(input_dir, "info.xml")
    translations_dir = f"translations/{lang_code}"
    output_dir = f"output/{lang_code.upper()}"
    special_cases_file = f"translations/{lang_code}/special_cases-{lang_code}.json"
    
    # Check paths
    if not os.path.exists(input_dir):
        print(f"Error: Input folder '{input_dir}' not found")
        return False
        
    if not os.path.exists(info_xml_path):
        print(f"Error: info.xml not found in '{input_dir}'")
        return False
    
    print(f"Input directory found: {input_dir}")
    print(f"Info.xml found: {info_xml_path}")
    
    # Parse info.xml
    input_files = []
    original_version = ""
    try:
        tree = ET.parse(info_xml_path)
        root = tree.getroot()
        
        original_version = root.get('version', '')
        print(f"Original version detected: {original_version}")
        
        for string_element in root.find('strings').findall('string'):
            relative_path = string_element.get('path')
            if relative_path:
                absolute_path = os.path.join(input_dir, relative_path)
                if os.path.exists(absolute_path):
                    input_files.append(absolute_path)
                    print(f"  Found file: {relative_path}")
                else:
                    print(f"  File not found: {relative_path}")
        
        print(f"Extracted {len(input_files)} files from info.xml")
        
    except Exception as e:
        print(f"Error parsing info.xml: {e}")
        return False
    
    if not input_files:
        print("No valid files found in info.xml")
        return False
    
    # Clean up old output directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        print(f"Removed old output directory: {output_dir}")
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Copy and update info.xml
    output_info_path = os.path.join(output_dir, "info.xml")
    try:
        with open(info_xml_path, 'r', encoding='utf-8') as f:
            info_content = f.read()
        
        # Update XML attributes
        updated_content = info_content
        
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
        
        with open(output_info_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"Updated info.xml saved to: {output_info_path}")
        
    except Exception as e:
        print(f"Error updating info.xml: {e}")
        return False
    
    # Copy icon.png
    icon_input_path = os.path.join(input_dir, "icon.png")
    if os.path.exists(icon_input_path):
        icon_output_path = os.path.join(output_dir, "icon.png")
        shutil.copy2(icon_input_path, icon_output_path)
        print(f"Copied icon.png to: {icon_output_path}")
    else:
        print(f"Warning: icon.png not found in {input_dir}")
    
    # Process files with automated choices
    processed_files = []
    
    print(f"\nProcessing {len(input_files)} files with automated choices...")
    
    for i, input_file in enumerate(input_files, 1):
        relative_path = os.path.relpath(input_file, input_dir)
        filename = os.path.basename(relative_path)
        
        # Automated choice logic
        if filename == "sws_strings_en.xml":
            choice = "Y"  # Translate sws_strings_en.xml
            action = "TRANSLATE"
        else:
            choice = "N"  # Copy without translation for all others
            action = "COPY ONLY"
        
        print(f"  [{i:02d}/{len(input_files)}] {relative_path} - {action}")
        
        # Create output path
        output_file_path = os.path.join(output_dir, relative_path)
        output_file_dir = os.path.dirname(output_file_path)
        
        if output_file_dir:
            Path(output_file_dir).mkdir(parents=True, exist_ok=True)
        
        if choice == "N":
            # Copy file without translation
            try:
                shutil.copy2(input_file, output_file_path)
                print(f"    Copied: {os.path.basename(output_file_path)}")
                processed_files.append(relative_path)
            except Exception as e:
                print(f"    Error copying: {e}")
                return False
        else:
            # Translate the file
            try:
                # Import here to avoid circular imports
                from translations_applicator import process_single_file
                
                process_single_file(
                    input_file, 
                    lang_code, 
                    translations_dir, 
                    output_file_path, 
                    special_cases_file, 
                    i, 
                    len(input_files)
                )
                print(f"    Translated: {os.path.basename(output_file_path)}")
                processed_files.append(relative_path)
            except Exception as e:
                print(f"    Error translating: {e}")
                return False
    
    # Create zip_name.txt
    try:
        zip_name_content = f"SupersStoryStrings_{lang_code.upper()}-EN_@ClientEN@-@{original_version}-mod_{mod_version}@"
        zip_name_path = os.path.join(output_dir, "zip_name.txt")
        
        with open(zip_name_path, 'w', encoding='utf-8') as f:
            f.write(zip_name_content)
        
        print(f"Created zip name file: {zip_name_path}")
        print(f"Zip name: {zip_name_content}")
        
    except Exception as e:
        print(f"Error creating zip_name.txt: {e}")
        return False
    
    print(f"\nAutomated translation completed successfully!")
    print(f"Files processed: {len(processed_files)}/{len(input_files)}")
    return True

def calculate_next_mod_version(submodule_tag, current_repo_tags):
    """
    Calculate the next mod version based on existing tags.
    
    Logic: Each submodule version gets its own mod versioning starting from 1.0.0a
    - v1.3.4 -> v1.3.4-mod_1.0.0a (first automatic release)
    - v1.4.0 -> v1.4.0-mod_1.0.0a (first automatic release for new submodule)
    
    Args:
        submodule_tag (str): Current submodule tag (e.g., 'v1.3.4')
        current_repo_tags (list): List of existing tags in current repo
        
    Returns:
        str: Next mod version (e.g., 'v1.4.0-mod_1.0.0a')
    """
    # Find existing mod tags for this specific submodule version
    mod_tags = [tag for tag in current_repo_tags if tag.startswith(f"{submodule_tag}-mod_")]
    
    if not mod_tags:
        # First mod version for this submodule tag - always start with 1.0.0a
        return f"{submodule_tag}-mod_1.0.0a"
    
    # If there are existing mod tags for this submodule version, increment patch
    # (this should be rare, but handles edge cases)
    latest_tag = sorted(mod_tags, key=lambda x: x.split('-mod_')[1])[-1]
    
    # Extract version part (e.g., "1.0.0a" from "v1.3.4-mod_1.0.0a")
    version_part = latest_tag.split('-mod_')[1]
    
    # Parse version
    if re.match(r'^(\d+)\.(\d+)\.(\d+)(a?)$', version_part):
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)(a?)$', version_part)
        major, minor, patch, auto_suffix = match.groups()
        
        # Increment patch version for additional release of same submodule version
        new_patch = int(patch) + 1
        new_version = f"{submodule_tag}-mod_{major}.{minor}.{new_patch}a"
        
        return new_version
    else:
        # Fallback
        return f"{submodule_tag}-mod_1.0.1a"

def test_version_calculation():
    """Test the version calculation logic"""
    print("Testing version calculation logic...\n")
    
    test_cases = [
        {
            "submodule": "v1.3.4",
            "existing_tags": [],
            "expected": "v1.3.4-mod_1.0.0a",
            "description": "First release for v1.3.4"
        },
        {
            "submodule": "v1.4.0", 
            "existing_tags": ["v1.3.4-mod_1.0.0a"],
            "expected": "v1.4.0-mod_1.0.0a",
            "description": "First release for v1.4.0 (different submodule)"
        },
        {
            "submodule": "v1.3.4",
            "existing_tags": ["v1.3.4-mod_1.0.0a"],
            "expected": "v1.3.4-mod_1.0.1a",
            "description": "Second release for same submodule version (rare case)"
        },
        {
            "submodule": "v1.4.0",
            "existing_tags": ["v1.3.4-mod_1.0.0a", "v1.4.0-mod_1.0.0a"],
            "expected": "v1.4.0-mod_1.0.1a",
            "description": "Additional release for v1.4.0"
        },
        {
            "submodule": "v2.0.0",
            "existing_tags": ["v1.3.4-mod_1.0.0a", "v1.4.0-mod_1.0.0a", "v1.4.0-mod_1.0.1a"],
            "expected": "v2.0.0-mod_1.0.0a",
            "description": "First release for v2.0.0 (brand new submodule version)"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        result = calculate_next_mod_version(test["submodule"], test["existing_tags"])
        status = "OK" if result == test["expected"] else "ERR"
        
        print(f"Test {i}: {status} - {test['description']}")
        print(f"  Submodule: {test['submodule']}")
        print(f"  Existing: {test['existing_tags']}")
        print(f"  Expected: {test['expected']}")
        print(f"  Got:      {result}")
        print()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run automated translation for PokeMMO strings.")
    parser.add_argument('--lang_code', type=str, required=True, help='Language code for translation (e.g., "it").')
    parser.add_argument('--mod_version', type=str, required=True, help='The version for the mod (e.g., "1.2.3a").')
    
    args = parser.parse_args()

    if apply_translations_automated(args.lang_code, args.mod_version):
        print("✅ Automated translation process completed successfully!")
        sys.exit(0)
    else:
        print("❌ Automated translation process failed.")
        sys.exit(1)