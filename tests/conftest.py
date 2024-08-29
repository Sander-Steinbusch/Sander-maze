from pytest import fixture
from azure.ai.formrecognizer import AnalyzeResult, DocumentStyle, DocumentSpan

@fixture
def analyze_result_with_styles_null() -> AnalyzeResult:
    return AnalyzeResult(
        content="content of the resume",
        styles=None
    )

@fixture
def analyze_result_with_styles_empty() -> AnalyzeResult:
    return AnalyzeResult(
        content="content of the resume",
        styles=[]
    )

@fixture
def analyze_result_with_styles() -> AnalyzeResult:
    return AnalyzeResult(
        content="first third second fourth",
        styles=[
            DocumentStyle(
                background_color="#ffffff",
                spans=[
                    DocumentSpan(offset=0, length=5),
                    DocumentSpan(offset=12, length=6),
                ],
            ),
            DocumentStyle(
                background_color="#ababab",
                spans=[
                    DocumentSpan(offset=6, length=5),
                    DocumentSpan(offset=19, length=6),
                ],
            ),
        ],
    )
