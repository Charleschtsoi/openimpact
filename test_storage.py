#!/usr/bin/env python3
"""
Comprehensive test suite for storage functionality.
Tests save, load, duplicate detection, and integration.
"""

import json
import os
import sys
from datetime import datetime

# Import functions from fetch_fact.py
# We'll import them directly by reading and executing, or use importlib
# For simplicity, we'll duplicate the logic here for testing
# Actually, let's import the module properly
try:
    from fetch_fact import (
        load_facts,
        save_facts,
        is_duplicate,
        add_fact_to_archive,
        get_fact_count
    )
except ImportError:
    print("Error: Could not import functions from fetch_fact.py", file=sys.stderr)
    sys.exit(1)


# Test configuration
TEST_ARCHIVE = "test_facts_archive.json"
TEST_SOURCE_URL = "https://uselessfacts.jsph.pl/api/v2/facts/random"

# Test results tracking
test_results = []
passed_tests = 0
failed_tests = 0


def run_test(test_name, test_func):
    """Run a test and track results."""
    global passed_tests, failed_tests
    try:
        result = test_func()
        if result:
            print(f"✓ PASS: {test_name}")
            test_results.append((test_name, True, None))
            passed_tests += 1
        else:
            print(f"✗ FAIL: {test_name}")
            test_results.append((test_name, False, "Test returned False"))
            failed_tests += 1
    except Exception as e:
        print(f"✗ FAIL: {test_name} - {str(e)}")
        test_results.append((test_name, False, str(e)))
        failed_tests += 1


def cleanup_test_file():
    """Remove test archive file if it exists."""
    if os.path.exists(TEST_ARCHIVE):
        os.remove(TEST_ARCHIVE)


def setup_test():
    """Setup before each test - clean up any existing test file."""
    cleanup_test_file()


# ============================================================================
# Test 1: Save Functionality
# ============================================================================

def test_save_creates_file():
    """Test that save_facts creates a file if it doesn't exist."""
    setup_test()
    facts = [{
        "text": "Test fact 1",
        "timestamp": "2024-01-01T00:00:00",
        "source": TEST_SOURCE_URL
    }]
    result = save_facts(facts, TEST_ARCHIVE)
    file_exists = os.path.exists(TEST_ARCHIVE)
    cleanup_test_file()
    return result and file_exists


def test_save_formats_json():
    """Test that save_facts properly formats JSON with metadata."""
    setup_test()
    facts = [{
        "text": "Test fact with metadata",
        "timestamp": "2024-01-01T12:00:00",
        "source": TEST_SOURCE_URL
    }]
    save_facts(facts, TEST_ARCHIVE)
    
    with open(TEST_ARCHIVE, 'r', encoding='utf-8') as f:
        loaded = json.load(f)
    
    cleanup_test_file()
    return (isinstance(loaded, list) and 
            len(loaded) == 1 and
            loaded[0]['text'] == "Test fact with metadata" and
            'timestamp' in loaded[0] and
            'source' in loaded[0])


def test_save_multiple_facts():
    """Test that multiple facts can be saved."""
    setup_test()
    facts = [
        {"text": "Fact 1", "timestamp": "2024-01-01T00:00:00", "source": TEST_SOURCE_URL},
        {"text": "Fact 2", "timestamp": "2024-01-01T01:00:00", "source": TEST_SOURCE_URL},
        {"text": "Fact 3", "timestamp": "2024-01-01T02:00:00", "source": TEST_SOURCE_URL}
    ]
    save_facts(facts, TEST_ARCHIVE)
    loaded = load_facts(TEST_ARCHIVE)
    cleanup_test_file()
    return len(loaded) == 3


# ============================================================================
# Test 2: Load Functionality
# ============================================================================

def test_load_nonexistent_file():
    """Test that load_facts returns empty list for non-existent file."""
    setup_test()
    result = load_facts("nonexistent_file.json")
    return result == []


def test_load_existing_file():
    """Test that load_facts can load facts from existing file."""
    setup_test()
    facts = [{
        "text": "Loaded fact",
        "timestamp": "2024-01-01T00:00:00",
        "source": TEST_SOURCE_URL
    }]
    save_facts(facts, TEST_ARCHIVE)
    loaded = load_facts(TEST_ARCHIVE)
    cleanup_test_file()
    return len(loaded) == 1 and loaded[0]['text'] == "Loaded fact"


def test_load_preserves_metadata():
    """Test that load_facts preserves all metadata fields."""
    setup_test()
    original_fact = {
        "text": "Fact with metadata",
        "timestamp": "2024-01-01T12:34:56",
        "source": TEST_SOURCE_URL
    }
    save_facts([original_fact], TEST_ARCHIVE)
    loaded = load_facts(TEST_ARCHIVE)
    cleanup_test_file()
    return (len(loaded) == 1 and
            loaded[0]['text'] == original_fact['text'] and
            loaded[0]['timestamp'] == original_fact['timestamp'] and
            loaded[0]['source'] == original_fact['source'])


def test_load_handles_corrupted_json():
    """Test that load_facts handles corrupted JSON gracefully."""
    setup_test()
    # Create a corrupted JSON file
    with open(TEST_ARCHIVE, 'w', encoding='utf-8') as f:
        f.write("{ invalid json }")
    
    result = load_facts(TEST_ARCHIVE)
    cleanup_test_file()
    return result == []


def test_load_handles_invalid_format():
    """Test that load_facts handles invalid format (not a list)."""
    setup_test()
    # Create a JSON file that's not a list
    with open(TEST_ARCHIVE, 'w', encoding='utf-8') as f:
        json.dump({"not": "a list"}, f)
    
    result = load_facts(TEST_ARCHIVE)
    cleanup_test_file()
    return result == []


# ============================================================================
# Test 3: Duplicate Detection
# ============================================================================

def test_duplicate_exact_match():
    """Test duplicate detection with exact match."""
    setup_test()
    facts = [{"text": "Exact match fact", "timestamp": "2024-01-01T00:00:00", "source": TEST_SOURCE_URL}]
    result = is_duplicate("Exact match fact", facts)
    cleanup_test_file()
    return result is True


def test_duplicate_case_insensitive():
    """Test duplicate detection is case-insensitive."""
    setup_test()
    facts = [{"text": "Case Sensitive Fact", "timestamp": "2024-01-01T00:00:00", "source": TEST_SOURCE_URL}]
    test_cases = [
        ("case sensitive fact", True),
        ("CASE SENSITIVE FACT", True),
        ("CaSe SeNsItIvE fAcT", True),
        ("Different Fact", False)
    ]
    all_passed = True
    for test_text, expected in test_cases:
        result = is_duplicate(test_text, facts)
        if result != expected:
            all_passed = False
    cleanup_test_file()
    return all_passed


def test_duplicate_whitespace_normalization():
    """Test duplicate detection normalizes whitespace."""
    setup_test()
    facts = [{"text": "Fact with spaces", "timestamp": "2024-01-01T00:00:00", "source": TEST_SOURCE_URL}]
    test_cases = [
        ("Fact   with   spaces", True),
        ("Fact\twith\tspaces", True),
        ("Fact\nwith\nspaces", True),
        ("  Fact with spaces  ", True),
        ("Factwithspaces", False)
    ]
    all_passed = True
    for test_text, expected in test_cases:
        result = is_duplicate(test_text, facts)
        if result != expected:
            all_passed = False
    cleanup_test_file()
    return all_passed


def test_duplicate_unique_fact():
    """Test that unique facts are not detected as duplicates."""
    setup_test()
    facts = [{"text": "Original fact", "timestamp": "2024-01-01T00:00:00", "source": TEST_SOURCE_URL}]
    result = is_duplicate("Completely different fact", facts)
    cleanup_test_file()
    return result is False


# ============================================================================
# Test 4: Integration Testing
# ============================================================================

def test_add_fact_to_archive():
    """Test that add_fact_to_archive saves a new fact."""
    setup_test()
    result = add_fact_to_archive("New unique fact", TEST_ARCHIVE, TEST_SOURCE_URL)
    loaded = load_facts(TEST_ARCHIVE)
    cleanup_test_file()
    return result is True and len(loaded) == 1 and loaded[0]['text'] == "New unique fact"


def test_add_fact_prevents_duplicate():
    """Test that add_fact_to_archive prevents adding duplicates."""
    setup_test()
    # Add first fact
    add_fact_to_archive("Duplicate test fact", TEST_ARCHIVE, TEST_SOURCE_URL)
    initial_count = get_fact_count(TEST_ARCHIVE)
    
    # Try to add duplicate
    result = add_fact_to_archive("Duplicate test fact", TEST_ARCHIVE, TEST_SOURCE_URL)
    final_count = get_fact_count(TEST_ARCHIVE)
    
    cleanup_test_file()
    return result is False and initial_count == 1 and final_count == 1


def test_multiple_facts_sequential():
    """Test that multiple facts can be saved sequentially."""
    setup_test()
    facts_to_add = ["Fact A", "Fact B", "Fact C"]
    
    for fact in facts_to_add:
        add_fact_to_archive(fact, TEST_ARCHIVE, TEST_SOURCE_URL)
    
    loaded = load_facts(TEST_ARCHIVE)
    cleanup_test_file()
    return len(loaded) == 3


def test_archive_grows_correctly():
    """Test that archive file grows correctly with new unique facts."""
    setup_test()
    initial_count = get_fact_count(TEST_ARCHIVE)
    
    add_fact_to_archive("Fact 1", TEST_ARCHIVE, TEST_SOURCE_URL)
    count_after_one = get_fact_count(TEST_ARCHIVE)
    
    add_fact_to_archive("Fact 2", TEST_ARCHIVE, TEST_SOURCE_URL)
    count_after_two = get_fact_count(TEST_ARCHIVE)
    
    cleanup_test_file()
    return (initial_count == 0 and
            count_after_one == 1 and
            count_after_two == 2)


# ============================================================================
# Test 5: Edge Cases
# ============================================================================

def test_empty_archive_file():
    """Test handling of empty archive file."""
    setup_test()
    # Create empty file
    with open(TEST_ARCHIVE, 'w', encoding='utf-8') as f:
        f.write("[]")
    
    result = load_facts(TEST_ARCHIVE)
    cleanup_test_file()
    return result == []


def test_facts_with_special_characters():
    """Test facts with special characters."""
    setup_test()
    special_fact = "Fact with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
    result = add_fact_to_archive(special_fact, TEST_ARCHIVE, TEST_SOURCE_URL)
    loaded = load_facts(TEST_ARCHIVE)
    cleanup_test_file()
    return result is True and len(loaded) == 1 and loaded[0]['text'] == special_fact


def test_very_long_fact():
    """Test facts with very long text."""
    setup_test()
    long_fact = "A" * 1000  # 1000 character fact
    result = add_fact_to_archive(long_fact, TEST_ARCHIVE, TEST_SOURCE_URL)
    loaded = load_facts(TEST_ARCHIVE)
    cleanup_test_file()
    return result is True and len(loaded) == 1 and len(loaded[0]['text']) == 1000


def test_unicode_characters():
    """Test facts with unicode characters."""
    setup_test()
    unicode_fact = "Fact with unicode: 你好世界 🌍 émojis 🎉"
    result = add_fact_to_archive(unicode_fact, TEST_ARCHIVE, TEST_SOURCE_URL)
    loaded = load_facts(TEST_ARCHIVE)
    cleanup_test_file()
    return result is True and len(loaded) == 1 and loaded[0]['text'] == unicode_fact


def test_get_fact_count():
    """Test get_fact_count function."""
    setup_test()
    add_fact_to_archive("Count test 1", TEST_ARCHIVE, TEST_SOURCE_URL)
    add_fact_to_archive("Count test 2", TEST_ARCHIVE, TEST_SOURCE_URL)
    count = get_fact_count(TEST_ARCHIVE)
    cleanup_test_file()
    return count == 2


# ============================================================================
# Main Test Runner
# ============================================================================

def main():
    """Run all tests."""
    print("=" * 70)
    print("Storage Functionality Test Suite")
    print("=" * 70)
    print()
    
    # Test 1: Save Functionality
    print("Test Category 1: Save Functionality")
    print("-" * 70)
    run_test("Save creates file", test_save_creates_file)
    run_test("Save formats JSON correctly", test_save_formats_json)
    run_test("Save multiple facts", test_save_multiple_facts)
    print()
    
    # Test 2: Load Functionality
    print("Test Category 2: Load Functionality")
    print("-" * 70)
    run_test("Load nonexistent file returns empty list", test_load_nonexistent_file)
    run_test("Load existing file", test_load_existing_file)
    run_test("Load preserves metadata", test_load_preserves_metadata)
    run_test("Load handles corrupted JSON", test_load_handles_corrupted_json)
    run_test("Load handles invalid format", test_load_handles_invalid_format)
    print()
    
    # Test 3: Duplicate Detection
    print("Test Category 3: Duplicate Detection")
    print("-" * 70)
    run_test("Duplicate exact match", test_duplicate_exact_match)
    run_test("Duplicate case-insensitive", test_duplicate_case_insensitive)
    run_test("Duplicate whitespace normalization", test_duplicate_whitespace_normalization)
    run_test("Unique fact not detected as duplicate", test_duplicate_unique_fact)
    print()
    
    # Test 4: Integration Testing
    print("Test Category 4: Integration Testing")
    print("-" * 70)
    run_test("Add fact to archive", test_add_fact_to_archive)
    run_test("Add fact prevents duplicate", test_add_fact_prevents_duplicate)
    run_test("Multiple facts sequential", test_multiple_facts_sequential)
    run_test("Archive grows correctly", test_archive_grows_correctly)
    print()
    
    # Test 5: Edge Cases
    print("Test Category 5: Edge Cases")
    print("-" * 70)
    run_test("Empty archive file", test_empty_archive_file)
    run_test("Facts with special characters", test_facts_with_special_characters)
    run_test("Very long fact", test_very_long_fact)
    run_test("Unicode characters", test_unicode_characters)
    run_test("Get fact count", test_get_fact_count)
    print()
    
    # Final cleanup
    cleanup_test_file()
    
    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Total tests: {passed_tests + failed_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print()
    
    if failed_tests == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
