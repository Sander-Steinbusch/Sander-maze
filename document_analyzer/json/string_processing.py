from re import search, Match
from langchain_core.messages import AIMessage

def remove_trailing_commas(text: str) -> str:
    pattern = "(,[\s]*])|(,[\s]*})"
    m = search(pattern, text)
    
    while isinstance(m, Match):
        old = m.group(0)
        new = old[1:]
        text = text.replace(old, new)
        m = search(pattern, text)
    
    return text

def remove_trailing_commas_from_message(message: AIMessage) -> AIMessage:
	content = message.content
	return AIMessage(remove_trailing_commas(content))