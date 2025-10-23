import sys
import pprint

sys.path.append('..')  # Add parent directory to path

from google_functions import convert_sheet_values_to_repo_names_and_authors
from google_functions import sanitize_repo_name
from google_functions import find_header_row_index

def test_convert_sheet_values_to_repo_names_and_authors():
    """Test the convert_sheet_values_to_repo_names_and_authors function"""
    
    # Test 1: Normal case with multiple rows and authors
    sheet_values = [
        ["Project Name", "Author 1", "Author 2", "Author 3"],
        ["Project Alpha", "John Smith", "Jane Doe", "Bob Wilson"],
        ["Project Beta", "Alice Johnson", "Charlie Brown"],
        ["Project Gamma", "David Lee"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"title": "Project Alpha", "repo-name": "project-alpha", "authors": "John Smith, Jane Doe, Bob Wilson"},
        {"title": "Project Beta", "repo-name": "project-beta", "authors": "Alice Johnson, Charlie Brown"},
        {"title": "Project Gamma", "repo-name": "project-gamma", "authors": "David Lee"}
    ]
    #assert result == expected, f"Expected {expected}, but got {result}"
    assert result == expected, f"Expected:\n{pprint.pformat(expected)}\n\nGot:\n{pprint.pformat(result)}"

    print("✓ Test 1 passed: Normal case with multiple rows and authors")
    
    # Test 2: Rows with empty cells in author columns
    sheet_values = [
        ["Project Name", "Author 1", "Author 2", "Author 3"],
        ["project-alpha", "John Smith", "", "Jane Doe", ""],
        ["Project Beta", "", "Alice Johnson", ""],
        ["project-gamma", "David Lee", "", "", ""]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"title": "project-alpha", "repo-name": "project-alpha", "authors": "John Smith, Jane Doe"},
        {"title": "Project Beta", "repo-name": "project-beta", "authors": "Alice Johnson"},
        {"title": "project-gamma", "repo-name": "project-gamma", "authors": "David Lee"}
    ]
    assert result == expected, f"Expected:\n{pprint.pformat(expected)}\n\nGot:\n{pprint.pformat(result)}"
    print("✓ Test 2 passed: Rows with empty cells filtered out")
    
    # Test 3: Authors with extra whitespace
    sheet_values = [
        ["Project Name", "Author 1", "Author 2", "Author 3"],
        ["project-alpha", "  John S.  Smith  ", " Jane   Doe ", "Bob Wilson"],
        ["Project Beta", "Alice Johnson   ", "  Charlie  Brown"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"title": "project-alpha", "repo-name": "project-alpha", "authors": "John S. Smith, Jane Doe, Bob Wilson"},
        {"title": "Project Beta", "repo-name": "project-beta", "authors": "Alice Johnson, Charlie Brown"}
    ]
    assert result == expected, f"Expected:\n{pprint.pformat(expected)}\n\nGot:\n{pprint.pformat(result)}"
    print("✓ Test 3 passed: Extra whitespace trimmed")
    
    # Test 4: Single row with single author
    sheet_values = [
        ["Project Name"],
        ["Solo Project", "John Smith"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"title": "Solo Project", "repo-name": "solo-project", "authors": "John Smith"}
    ]
    assert result == expected, f"Expected:\n{pprint.pformat(expected)}\n\nGot:\n{pprint.pformat(result)}"
    print("✓ Test 4 passed: Single row with single author")
    
    # Test 5: Row with only project name (no authors)
    sheet_values = [
        ["Project Name"],
        ["Empty Project"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"title": "Empty Project", "repo-name": "empty-project", "authors": ""}
    ]
    assert result == expected, f"Expected:\n{pprint.pformat(expected)}\n\nGot:\n{pprint.pformat(result)}"
    print("✓ Test 5 passed: Row with only project name")

    # Test 6: Empty rows mixed with data rows
    sheet_values = [
        ["Project Name"],
        ["project-alpha", "John Smith", "Jane Doe"],
        [],  # Empty row
        ["Project Beta", "Alice Johnson"],
        [],  # Another empty row
        ["Project Gamma", "David Lee"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"title": "project-alpha", "repo-name": "project-alpha", "authors": "John Smith, Jane Doe"},
        {"title": "Project Beta", "repo-name": "project-beta", "authors": "Alice Johnson"},
        {"title": "Project Gamma", "repo-name": "project-gamma", "authors": "David Lee"}
    ]
    assert result == expected, f"Expected:\n{pprint.pformat(expected)}\n\nGot:\n{pprint.pformat(result)}"
    print("✓ Test 6 passed: Empty rows filtered out")
    
    # Test 7: All empty rows
    sheet_values = [[], [], []]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = []
    assert result == expected, f"Expected:\n{pprint.pformat(expected)}\n\nGot:\n{pprint.pformat(result)}"
    print("✓ Test 7 passed: All empty rows")
    
    # Test 8: Empty sheet values
    sheet_values = []
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = []
    assert result == expected, f"Expected:\n{pprint.pformat(expected)}\n\nGot:\n{pprint.pformat(result)}"
    print("✓ Test 8 passed: Empty sheet values")
    
    # Test 9: Variable number of author columns
    sheet_values = [
        ["Project Name"],
        ["project-alpha", "John S. Smith", "Jane Doe", "Bob Wilson", "Mary Johnson"],
        ["Project     Beta", "Alice Johnson"],
        ["Project Gamma", "David Lee", "Sarah Connor", "Tom Hardy"]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"title": "project-alpha", "repo-name": "project-alpha", "authors": "John S. Smith, Jane Doe, Bob Wilson, Mary Johnson"},
        {"title": "Project     Beta", "repo-name": "project-beta", "authors": "Alice Johnson"},
        {"title": "Project Gamma", "repo-name": "project-gamma", "authors": "David Lee, Sarah Connor, Tom Hardy"}
    ]
    assert result == expected, f"Expected:\n{pprint.pformat(expected)}\n\nGot:\n{pprint.pformat(result)}"
    print("✓ Test 9 passed: Variable number of author columns")
    
    # Test 10: Row with all empty author columns
    sheet_values = [
        ["Project Name"],
        ["project-alpha", "", "", ""],
        ["Project Beta", "Alice Johnson", "", ""]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"title": "project-alpha", "repo-name": "project-alpha", "authors": ""},
        {"title": "Project Beta", "repo-name": "project-beta", "authors": "Alice Johnson"}
    ]
    assert result == expected, f"Expected:\n{pprint.pformat(expected)}\n\nGot:\n{pprint.pformat(result)}"
    print("✓ Test 10 passed: Row with all empty author columns")

    # Test 11: Project Name column not first
    sheet_values = [
        ["Faculty Member", "Project Name"],
        ["Laura L", "project-alpha", "", "", ""],
        ["Joe Joe", "Project Beta", "Alice Johnson", "", ""]
    ]
    result = convert_sheet_values_to_repo_names_and_authors(sheet_values)
    expected = [
        {"title": "project-alpha", "repo-name": "project-alpha", "authors": ""},
        {"title": "Project Beta", "repo-name": "project-beta", "authors": "Alice Johnson"}
    ]
    assert result == expected, f"Expected:\n{pprint.pformat(expected)}\n\nGot:\n{pprint.pformat(result)}"
    print("✓ Test 11 passed: Column before Project Name ignored")



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
        ("UPPERCASE PROJECT", "uppercase-project"),
        ("Reclaiming the City: A Counter-Map of St. Louis Monuments", "reclaiming-the-city-a-counter-map-of-st-louis-monuments")
    ]
    
    for original, expected in test_cases:
        result = sanitize_repo_name(original)
        if result == expected:
            print(f"✓ '{original}' -> '{result}'")
        else:
            print(f"✗ '{original}' -> '{result}' (expected '{expected}')")

def test_find_header_row_index():
    """Test the find_header_row_index function"""
    sheet_values = [
        ["Project Name", "John Smith", "Jane Doe", "Bob Wilson"],
        ["Project Beta", "Alice Johnson", "Charlie Brown"],
        ["Project Gamma", "David Lee"]
    ]

    col_name = "Project Name"
    result = find_header_row_index(sheet_values, col_name)
    expected = 0
    if result == expected:
        print(f"✓ {col_name} -> '{result}'")
    else:
        print(f"✗ {col_name} -> '{result}' (expected '{expected}')")
    assert result == expected, f"Expected {expected}, but got {result}"

    col_name = "John Smith"
    result = find_header_row_index(sheet_values, col_name)
    expected = 1
    if result == expected:
        print(f"✓ {col_name} -> '{result}'")
    else:
        print(f"✗ {col_name} -> '{result}' (expected '{expected}')")
    assert result == expected, f"Expected {expected}, but got {result}"

    
    col_name = "David Lee"
    result = find_header_row_index(sheet_values, col_name)
    expected = -1
    if result == expected:
        print(f"✓ {col_name} -> '{result}'")
    else:
        print(f"✗ {col_name} -> '{result}' (expected '{expected}')")
    assert result == expected, f"Expected {expected}, but got {result}"

    col_name = "Nonexistent Column"
    result = find_header_row_index([], col_name)
    expected = -1
    if result == expected:
        print(f"✓ {col_name} -> '{result}'")
    else:
        print(f"✗ {col_name} -> '{result}' (expected '{expected}')")
    assert result == expected, f"Expected {expected}, but got {result}"

    col_name = ""
    result = find_header_row_index([""], col_name)
    expected = -1
    if result == expected:
        print(f"✓ {col_name} -> '{result}'")
    else:
        print(f"✗ {col_name} -> '{result}' (expected '{expected}')")
    assert result == expected, f"Expected {expected}, but got {result}"

    pass


# Run all the tests
test_find_header_row_index()
test_sanitize_repo_name()
test_convert_sheet_values_to_repo_names_and_authors()