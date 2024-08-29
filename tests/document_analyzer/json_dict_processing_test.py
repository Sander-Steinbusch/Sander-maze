
from document_analyzer.json.dict_processing import remove_empty_objects, remove_empty_objects_from_list
from tests.document_analyzer.json.dict_fixture import *

class TestWhenRemoveEmptyObjects:

    def test_should_remove_empty_books(self):
        input = dict_with_empty_book()
        expected = dict_valid()

        actual = remove_empty_objects(input)

        assert actual == expected

    def test_should_remove_empty_languages(self):
        input = dict_with_empty_language()
        expected = dict_valid()
        
        actual = remove_empty_objects(input)

        assert actual == expected

    def test_should_remove_empty_projects(self):
        input = dict_with_empty_consultancy_assignment()
        expected = dict_valid()

        actual = remove_empty_objects(input)

        assert actual == expected

    def test_should_not_have_sideeffects(self):
        input = dict_with_empty_book()
        copy_of_input = dict_with_empty_book()
        
        remove_empty_objects(input)

        assert input == copy_of_input

    def test_should_leave_list_of_strings_untouched(self):
        input = dict_with_hobbies()
        expected = dict_with_hobbies()

        actual = remove_empty_objects(input)

        assert actual == expected


class TestWhenRemoveEmptyObjectsFromList:

    def test_should_remove_empty_objects(self):
        input = list_with_empty_dict()
        expected = []

        actual = remove_empty_objects_from_list(input)

        assert actual == expected

    def test_with_list_of_strings(self):
        input = list_with_strings()
        expected = list_with_strings()

        actual = remove_empty_objects_from_list(input)

        assert actual == expected

    def test_should_only_remove_empty_objects(self):
        input = list_with_both_empty_and_valid_dict()
        expected = list_with_only_valid_dict()

        actual = remove_empty_objects_from_list(input)

        assert actual == expected

