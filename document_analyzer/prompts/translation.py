from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.prompts import SystemMessagePromptTemplate
from typing import List

__template = """
You will translate all following messages to {language}.
Your tasks is as follows:
1. Translate each message to {language}.
2. Maintain the original order of messages in the response.
3. Separate each translated message with two empty lines.
4. If a message is already in {language}, return the original message.
5. If the original language cannot be determined or the text is nonsensical,
return the original text.
6. Do not add any additional context.
"""


def build_persona_message(language: str) -> SystemMessage:
    promptTemplate = SystemMessagePromptTemplate.from_template(template=__template)
    return promptTemplate.format(language=language.capitalize())


def build_messages(input: dict) -> List[BaseMessage]:
    messages = [build_persona_message(input["language"])]
    for text in input["texts"]:
        messages.append(HumanMessage(content=text["text"]))

    return messages
