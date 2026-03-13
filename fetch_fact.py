#!/usr/bin/env python3
"""
Script to fetch and display a random useless fact from the uselessfacts.jsph.pl API.
This demonstrates how digital tools interact with online data sources.
"""

import requests
import sys


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


def main():
    """Main function to fetch and display a fact."""
    print("Fetching a random useless fact...")
    print("-" * 50)
    
    fact = fetch_random_fact()
    
    if fact:
        print(fact)
        print("-" * 50)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
