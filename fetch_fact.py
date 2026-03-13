#!/usr/bin/env python3
"""
Script to fetch and display a random useless fact from the uselessfacts.jsph.pl API.
This demonstrates how digital tools interact with online data sources.
Includes persistent storage and duplicate detection capabilities.
"""

import requests
import sys
import json
import os
import argparse
from datetime import datetime


def fetch_random_fact():
    """
    Connect to the uselessfacts API and fetch a random fact.
    
    Returns:
        str: The fact text if successful, None otherwise
    """
    api_url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
    
    try:
        # Make GET request to the API
        response = requests.get(api_url, timeout=10)
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Parse JSON response
        fact_data = response.json()
        
        # Extract the fact text
        fact_text = fact_data.get('text', None)
        
        if fact_text:
            return fact_text
        else:
            print("Error: API response did not contain a fact text.", file=sys.stderr)
            return None
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Please check your internet connection.", file=sys.stderr)
        return None
    except requests.exceptions.Timeout:
        print("Error: Request timed out. The API took too long to respond.", file=sys.stderr)
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error occurred: {e}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred while making the request: {e}", file=sys.stderr)
        return None
    except ValueError as e:
        print(f"Error: Could not parse JSON response: {e}", file=sys.stderr)
        return None


def load_facts(archive_file):
    """
    Load facts from JSON archive file.
    
    Args:
        archive_file (str): Path to the JSON archive file
        
    Returns:
        list: List of fact dictionaries, or empty list if file doesn't exist or is corrupted
    """
    if not os.path.exists(archive_file):
        return []
    
    try:
        with open(archive_file, 'r', encoding='utf-8') as f:
            facts = json.load(f)
            if isinstance(facts, list):
                return facts
            else:
                print(f"Warning: Archive file format is invalid. Expected a list.", file=sys.stderr)
                return []
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse archive file: {e}", file=sys.stderr)
        return []
    except IOError as e:
        print(f"Error: Could not read archive file: {e}", file=sys.stderr)
        return []


def save_facts(facts_list, archive_file):
    """
    Save list of facts to JSON archive file.
    
    Args:
        facts_list (list): List of fact dictionaries to save
        archive_file (str): Path to the JSON archive file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(facts_list, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error: Could not write to archive file: {e}", file=sys.stderr)
        return False


def is_duplicate(fact_text, facts_list):
    """
    Check if a fact text already exists in the archive.
    Uses case-insensitive comparison with normalized whitespace.
    
    Args:
        fact_text (str): The fact text to check
        facts_list (list): List of fact dictionaries to search
        
    Returns:
        bool: True if duplicate found, False otherwise
    """
    # Normalize the input fact text: lowercase and normalize whitespace
    normalized_input = ' '.join(fact_text.lower().split())
    
    for fact in facts_list:
        if 'text' in fact:
            normalized_existing = ' '.join(fact['text'].lower().split())
            if normalized_input == normalized_existing:
                return True
    return False


def add_fact_to_archive(fact_text, archive_file, source_url):
    """
    Add a fact to the archive if it's not a duplicate.
    
    Args:
        fact_text (str): The fact text to add
        archive_file (str): Path to the JSON archive file
        source_url (str): Source URL of the fact
        
    Returns:
        bool: True if fact was added, False if duplicate or error occurred
    """
    # Load existing facts
    facts_list = load_facts(archive_file)
    
    # Check for duplicates
    if is_duplicate(fact_text, facts_list):
        print("This fact is already in the archive. Skipping duplicate.", file=sys.stderr)
        return False
    
    # Create new fact entry with metadata
    new_fact = {
        "text": fact_text,
        "timestamp": datetime.now().isoformat(),
        "source": source_url
    }
    
    # Add to list and save
    facts_list.append(new_fact)
    
    if save_facts(facts_list, archive_file):
        return True
    else:
        return False


def get_fact_count(archive_file):
    """
    Get the total number of facts stored in the archive.
    
    Args:
        archive_file (str): Path to the JSON archive file
        
    Returns:
        int: Number of facts in archive
    """
    facts_list = load_facts(archive_file)
    return len(facts_list)


def show_archive(archive_file):
    """
    Display all facts in the archive.
    
    Args:
        archive_file (str): Path to the JSON archive file
    """
    facts_list = load_facts(archive_file)
    
    if not facts_list:
        print("Archive is empty.")
        return
    
    print(f"\nArchive contains {len(facts_list)} fact(s):")
    print("=" * 70)
    
    for i, fact in enumerate(facts_list, 1):
        print(f"\n{i}. {fact.get('text', 'N/A')}")
        if 'timestamp' in fact:
            print(f"   Saved: {fact['timestamp']}")
        if 'source' in fact:
            print(f"   Source: {fact['source']}")
        print("-" * 70)


def main():
    """Main function to fetch and display a fact."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Fetch random useless facts and manage a fact archive'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        default=True,
        help='Automatically save fetched facts to archive (default: True)'
    )
    parser.add_argument(
        '--no-save',
        dest='save',
        action='store_false',
        help='Do not save fetched facts to archive'
    )
    parser.add_argument(
        '--show-archive',
        action='store_true',
        help='Display all facts in the archive'
    )
    parser.add_argument(
        '--count',
        action='store_true',
        help='Show the number of facts in the archive'
    )
    parser.add_argument(
        '--archive-file',
        default='facts_archive.json',
        help='Path to the archive file (default: facts_archive.json)'
    )
    
    args = parser.parse_args()
    
    archive_file = args.archive_file
    api_url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
    
    # Handle show-archive option
    if args.show_archive:
        show_archive(archive_file)
        return 0
    
    # Handle count option
    if args.count:
        count = get_fact_count(archive_file)
        print(f"Archive contains {count} fact(s).")
        return 0
    
    # Fetch and display fact
    print("Fetching a random useless fact...")
    print("-" * 50)
    
    fact = fetch_random_fact()
    
    if fact:
        print(fact)
        print("-" * 50)
        
        # Save to archive if requested
        if args.save:
            print("\nChecking archive for duplicates...")
            if add_fact_to_archive(fact, archive_file, api_url):
                count = get_fact_count(archive_file)
                print(f"Fact saved to archive! Total facts: {count}")
            else:
                count = get_fact_count(archive_file)
                print(f"Archive already contains {count} fact(s).")
        
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
