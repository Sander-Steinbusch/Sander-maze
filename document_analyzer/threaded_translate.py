import threading
import re
from multiprocessing import Queue

from langchain_openai import AzureChatOpenAI

from document_analyzer.translators.azure import translate_texts as azure_translate_texts

from threading import Barrier


def strip_html_tags(text):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


# replace all consecutive newlines with a single newline
# as long as there are consecutive newlines
def replace_consecutive_newlines(text):
    while "\n\n" in text:
        text = text.replace("\n\n", "\n")
    return text


def sanitize_text(text):
    text = strip_html_tags(text)
    text = replace_consecutive_newlines(text)
    return text


def translate_worker(
    barrier: Barrier,
    q: Queue,
    model: AzureChatOpenAI,
    language: str,
    text_id: str,
    text_string: str,
):
    """
    This funtion runs in a new thread
    """
    text = sanitize_text(text_string)

    # translate the text
    try:
        translation = azure_translate_texts(
            model, {"language": language, "texts": [{"id": text_id, "text": text}]}
        )[0]
    except Exception as e:
        print(f"Error translating text: {e}")
        translation = {"id": text_id, "text": text}

    q.put_nowait(translation)

    # wait for other threads to reach the barrier
    barrier.wait()


def translate_many(model: AzureChatOpenAI, language: str, texts: list[dict]):
    # queue to store the translations
    q = Queue()
    number_of_translations = len(texts)
    barrier = Barrier(number_of_translations)

    threads = []

    # create a thread for each text
    for text in texts:
        text_id = text["id"]
        text_string = text["text"]
        threads.append(
            threading.Thread(
                target=translate_worker,
                args=(barrier, q, model, language, text_id, text_string),
            )
        )

    print(f"Starting {len(threads)} threads...")

    # Start all threads
    for t in threads:
        t.start()

    # wait for all threads to finish
    for t in threads:
        t.join()

    # get the translations from the queue
    translations = []
    while not q.empty():
        translations.append(q.get_nowait())

    print(f"Returning {len(translations)} translations")

    return translations
