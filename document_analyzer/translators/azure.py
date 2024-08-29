
from typing import List
from langchain_core.messages import AIMessage
from langchain_core.runnables import (
	Runnable, RunnableLambda
)
from langchain_openai import ChatOpenAI
from document_analyzer.prompts.translation import build_messages

def replace_with_translations(input: dict, response: AIMessage) -> List[dict]:
	translations = response.content.split("\n\n")

	results = []
	texts = input['texts']
	for idx in range(len(translations)):
		results.append({
			'id': texts[idx]['id'],
			'text': translations[idx]
		})

	return results

def build_post_processor(input: dict) -> Runnable[AIMessage, List[dict]]:
	return RunnableLambda(lambda message: replace_with_translations(input, message))

def translate_texts(model: ChatOpenAI, input: dict) -> List[dict]:
	chain = (
		RunnableLambda(build_messages)
		| model
		| build_post_processor(input)
	)
	
	return chain.invoke(input)
