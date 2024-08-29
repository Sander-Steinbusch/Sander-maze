from document_analyzer.tools.langchain import init_langchain_ocr_tool
from pytest import mark


def test_can_initialize_tool():
    tool = init_langchain_ocr_tool()

    assert tool is not None


IT_RESUME_URL = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.YMm3apU85deTJVbSYrSr8gHaKe%26pid%3DApi&f=1&ipt=a3111b4b2889b201159f71c0d9ccb4b021f840df037371990a09376204c5a8b1&ipo=images"  # noqa: B950


@mark.skip(reason="uses external resource")
def test_run_returns_expected_output():
    tool = init_langchain_ocr_tool()

    result = tool.run(IT_RESUME_URL)

    assert result == "fail this test because it should be disabled anyway!"
