from document_analyzer.tools.custom.helpers import group_by_background

class TestGroupByBackground:

    def test_expected_result(self, analyze_result_with_styles):
        actual = group_by_background(analyze_result_with_styles)

        assert actual == ["first second", "third fourth"]

    def test_given_no_styles(self, analyze_result_with_styles_null):
        actual = group_by_background(analyze_result_with_styles_null)

        assert actual == [analyze_result_with_styles_null.content]

    def test_given_empty_styles(self, analyze_result_with_styles_empty):
        actual = group_by_background(analyze_result_with_styles_empty)

        assert actual == [analyze_result_with_styles_empty.content]
