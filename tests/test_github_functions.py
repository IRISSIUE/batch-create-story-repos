import sys

sys.path.append('..')  # Add parent directory to path

from github_functions import update_variable_with_data_sheet_link


def test_update_variable_with_data_sheet_link():
    """Test the update_variable_with_data_sheet_link function"""
    
    # Test 1: Scrolly Story style with const and double quotes
    lines = [
        "Line 1 no changes",
        'const googleSheetURL ="https://docs.google.com/spreadsheets/d/OLD_ID";',
        "Another line"
    ]
    story_data_sheet_URL = "https://docs.google.com/spreadsheets/d/NEW_ID/edit"
    variable_to_update = "googleSheetURL"
    result = update_variable_with_data_sheet_link(lines, story_data_sheet_URL, variable_to_update)
    expected = [
        "Line 1 no changes",
        'const googleSheetURL ="https://docs.google.com/spreadsheets/d/NEW_ID/edit";',
        "Another line"
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 1 passed: Normal case with multiple rows and authors")


    # Test 2: Leaflet story map style with var and single quotes
    lines = [
        "Line 1 no changes",
        "var googleSheetURL ='https://docs.google.com/spreadsheets/d/OLD_ID';",
        "Another line"
    ]
    story_data_sheet_URL = "https://docs.google.com/spreadsheets/d/NEW_ID/edit"
    variable_to_update = "googleSheetURL"
    result = update_variable_with_data_sheet_link(lines, story_data_sheet_URL, variable_to_update)
    expected = [
        "Line 1 no changes",
        "var googleSheetURL ='https://docs.google.com/spreadsheets/d/NEW_ID/edit';",
        "Another line"
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 2 passed: Leaflet story map style with var and single quotes")
    
    # Test 3: No variable found
    lines = [
        "Line 1 no changes",
        "var googleSheetU1 ='https://docs.google.com/spreadsheets/d/OLD_ID';",
        "Another line"
    ]
    story_data_sheet_URL = "https://docs.google.com/spreadsheets/d/NEW_ID/edit"
    variable_to_update = "googleSheetURL"
    result = update_variable_with_data_sheet_link(lines, story_data_sheet_URL, variable_to_update)
    expected = [
        "Line 1 no changes",
        "var googleSheetU1 ='https://docs.google.com/spreadsheets/d/OLD_ID';",
        "Another line"
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 3 passed: No variable found")

    # Test 4: The variable used further down in the file not changed
    lines = [
        "Line 1 no changes",
        "var googleSheetURL ='https://docs.google.com/spreadsheets/d/OLD_ID';",
        "Another line"
        "Another line with googleSheetURL not changed"
    ]
    story_data_sheet_URL = "https://docs.google.com/spreadsheets/d/NEW_ID/edit"
    variable_to_update = "googleSheetURL"
    result = update_variable_with_data_sheet_link(lines, story_data_sheet_URL, variable_to_update)
    expected = [
        "Line 1 no changes",
        "var googleSheetURL ='https://docs.google.com/spreadsheets/d/NEW_ID/edit';",
        "Another line"
        "Another line with googleSheetURL not changed"

    ]
    assert result == expected, f"Expected {expected}, but got {result}"
    print("✓ Test 4 passed: The variable used further down in the file not changed")


# Run all the tests
test_update_variable_with_data_sheet_link()