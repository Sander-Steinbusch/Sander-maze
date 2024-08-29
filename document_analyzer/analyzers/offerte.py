from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda, RunnableSerializable, RunnableParallel
from typing import Any, Type
from langchain.pydantic_v1 import BaseModel

from document_analyzer.json.dict_processing import remove_empty_objects
from document_analyzer.json.string_processing import remove_trailing_commas_from_message
from document_analyzer.models.offerte_response import Offerte
from document_analyzer.prompts.analysis.offerte import build_offerte_prompt
from document_analyzer.tools.custom.model import CustomTextExtractorTool

#SUGGESTION: make this chain a dedicated class/object
def build_chain(requested_data: Type[BaseModel], model: ChatOpenAI) -> RunnableSerializable[str, Any]:
	return (
		build_offerte_prompt(data_model=requested_data)
		| model
		| RunnableLambda(remove_trailing_commas_from_message)
		| JsonOutputParser(pydantic_object=requested_data)
		| RunnableLambda(remove_empty_objects)
	)

def parse_offerte(text: str, model: ChatOpenAI) -> dict: 

	chain = (
		RunnableParallel(
			offerte=build_chain(Offerte, model)
		)
		| RunnableLambda(lambda x: x["offerte"])
	)

	return chain.invoke(text)

#TODO: https://github.com/continuum-consulting/document-analyser/issues/60
def parse_offerte_file(filename: str, model: ChatOpenAI, ocr: CustomTextExtractorTool):
	file_text = ocr.run(filename)
	return parse_offerte(file_text, model)