import sys

sys.path.append('..')  # Add parent directory to path

from google_functions import convert_sheet_values_to_repo_names_and_authors
from google_functions import sanitize_repo_name

def test_convert_sheet_values_to_repo_names_and_authors():
    """Test the convert_sheet_values_to_repo_names_and_authors function"""
    
    # Test 1: Normal case with multiple rows and authors
    sheet_values = [
        ["Project Alpha", "John Smith", "Jane Doe", "Bob Wilson"],
        ["Project Beta", "Alice Johnson", "Charlie Brown"],
        ["Project Gamma", "David Lee"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"name": "Project Alpha", "repo-name": "project-alpha", "authors": "John Smith, Jane Doe, Bob Wilson"},
        {"name": "Project Beta", "repo-name": "project-beta", "authors": "Alice Johnson, Charlie Brown"},
        {"name": "Project Gamma", "repo-name": "project-gamma", "authors": "David Lee"}
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 1 passed: Normal case with multiple rows and authors")
    
    # Test 2: Rows with empty cells in author columns
    sheet_values = [
        ["project-alpha", "John Smith", "", "Jane Doe", ""],
        ["Project Beta", "", "Alice Johnson", ""],
        ["project-gamma", "David Lee", "", "", ""]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"name": "project-alpha", "repo-name": "project-alpha", "authors": "John Smith, Jane Doe"},
        {"name": "Project Beta", "repo-name": "project-beta", "authors": "Alice Johnson"},
        {"name": "project-gamma", "repo-name": "project-gamma", "authors": "David Lee"}
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 2 passed: Rows with empty cells filtered out")
    
    # Test 3: Authors with extra whitespace
    sheet_values = [
        ["project-alpha", "  John S.  Smith  ", " Jane   Doe ", "Bob Wilson"],
        ["Project Beta", "Alice Johnson   ", "  Charlie  Brown"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"name": "project-alpha", "repo-name": "project-alpha", "authors": "John S. Smith, Jane Doe, Bob Wilson"},
        {"name": "Project Beta", "repo-name": "project-beta", "authors": "Alice Johnson, Charlie Brown"}
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 3 passed: Extra whitespace trimmed")
    
    # Test 4: Single row with single author
    sheet_values = [
        ["Solo Project", "John Smith"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"name": "Solo Project", "repo-name": "solo-project", "authors": "John Smith"}
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 4 passed: Single row with single author")
    
    # Test 5: Row with only project name (no authors)
    sheet_values = [
        ["Empty Project"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"name": "Empty Project", "repo-name": "empty-project", "authors": ""}
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 5 passed: Row with only project name")

    # Test 6: Empty rows mixed with data rows
    sheet_values = [
        ["project-alpha", "John Smith", "Jane Doe"],
        [],  # Empty row
        ["Project Beta", "Alice Johnson"],
        [],  # Another empty row
        ["Project Gamma", "David Lee"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"name": "project-alpha", "repo-name": "project-alpha", "authors": "John Smith, Jane Doe"},
        {"name": "Project Beta", "repo-name": "project-beta", "authors": "Alice Johnson"},
        {"name": "Project Gamma", "repo-name": "project-gamma", "authors": "David Lee"}
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 6 passed: Empty rows filtered out")
    
    # Test 7: All empty rows
    sheet_values = [[], [], []]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = []
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 7 passed: All empty rows")
    
    # Test 8: Empty sheet values
    sheet_values = []
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = []
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 8 passed: Empty sheet values")
    
    # Test 9: Variable number of author columns
    sheet_values = [
        ["project-alpha", "John S. Smith", "Jane Doe", "Bob Wilson", "Mary Johnson"],
        ["Project     Beta", "Alice Johnson"],
        ["Project Gamma", "David Lee", "Sarah Connor", "Tom Hardy"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"name": "project-alpha", "repo-name": "project-alpha", "authors": "John S. Smith, Jane Doe, Bob Wilson, Mary Johnson"},
        {"name": "Project     Beta", "repo-name": "project-beta", "authors": "Alice Johnson"},
        {"name": "Project Gamma", "repo-name": "project-gamma", "authors": "David Lee, Sarah Connor, Tom Hardy"}
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 9 passed: Variable number of author columns")
    
    # Test 10: Row with all empty author columns
    sheet_values = [
        ["project-alpha", "", "", ""],
        ["Project Beta", "Alice Johnson", "", ""]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"name": "project-alpha", "repo-name": "project-alpha", "authors": ""},
        {"name": "Project Beta", "repo-name": "project-beta", "authors": "Alice Johnson"}
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 10 passed: Row with all empty author columns")


def test_sanitize_repo_name():
    """Test the sanitize_repo_name function"""
    
    test_cases = [
        ("My Project Alpha", "my-project-alpha"),
        ("Project -  Beta!!!", "project-beta"),
        ("Data's Science 101", "datas-science-101"),
        ("Web@App#2024", "webapp2024"),
        ("   Multiple    Spaces   ", "multiple-spaces"),
        ("Special-Characters!@#$%", "special-characters"),
        ("Already-Good-Name", "already-good-name"),
        ("", ""),
        ("123 Numbers Only", "123-numbers-only"),
        ("UPPERCASE PROJECT", "uppercase-project")
    ]
    
    for original, expected in test_cases:
        result = sanitize_repo_name(original)
        if result == expected:
            print(f"✓ '{original}' -> '{result}'")
        else:
            print(f"✗ '{original}' -> '{result}' (expected '{expected}')")

# Run all the tests
test_sanitize_repo_name()
test_convert_sheet_values_to_repo_names_and_authors()