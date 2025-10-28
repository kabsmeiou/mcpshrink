from src.llm_client import get_groq_client
from src.models.configs import ModelConfig
from src.utils import load_config
import logging
from dotenv import load_dotenv
import os
from typing import List

from fastmcp import FastMCP
from collections import Counter
import requests
import re


logging.basicConfig(
    filename='logs/document_analysis.log',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DocumentAnalysisMCPServer")

load_dotenv()

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/dbmdz/bert-large-cased-finetuned-conll03-english"
HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN")

groq_client = get_groq_client()
config: ModelConfig = load_config("config.yaml", section="teacher")
TEACHER_MODEL = config.get("model_name")

mcp = FastMCP(
    name="document_analysis_server",
)


# @mcp.tool
# def search_documents(query: str, top_k: int = 5) -> list:
#     """
#     Retrieves relevant documents from a corpus.

#     Args:
#         query (str): The search query.
#         top_k (int): The number of top documents to retrieve.

#     Returns:    
#         list: A list of relevant documents.
#     """
#     # Your implementation here
#     raise NotImplementedError("search_documents is not implemented yet.")

# @mcp.tool
# def fetch_section(document_id: str, section_name: str) -> str:
#     """
#     Fetches a specific section from a document.

#     Args:
#         document_id (str): The ID of the document.
#         section_name (str): The name of the section to fetch.

#     Returns:    
#         str: The content of the specified section.
#     """
#     # Your implementation here
#     raise NotImplementedError("fetch_section is not implemented yet.")

@mcp.tool
def summarize_text(text: str, maximum_sentences: int) -> str:
    """
    Summarizes the input text to a specified number of sentences.

    Args:
        text (str): The text to summarize.
        maximum_sentences (int): The maximum number of sentences in the summary.

    Returns:
        str: The summarized text.
    """
    try:
        prompt = f"Summarize the following text in no more than {maximum_sentences} sentences:\n\n{text}"

        completion = groq_client.chat.completions.create(
            model=TEACHER_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ]
                }
            ],
            temperature=0.7,
            max_completion_tokens=512,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        return completion.choices[0].message.content

    except Exception as e:
        logger.error(f"Error in generate_report: {str(e)}")
        return f"Error generating report: {str(e)}"
    
    
@mcp.tool
def keyword_extractor(text: str, top_k: int = 5) -> List[str]:
    """
    Extract top-k keywords from a text document.

    Args:
        text: The document content.
        top_k: Number of keywords to extract.

    Returns:
        list: List of top-k keywords.
    """
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    common = Counter(words).most_common(top_k)
    return [w for w, _ in common]


@mcp.tool
def sentiment_analyzer(text: str) -> str:
    """
    Analyze the sentiment of the given text.
    Positive words are: good, great, excellent, happy, love, fantastic, positive.
    Negative words are: bad, terrible, awful, sad, hate, horrible, negative.

    Args:
        text: The document content.

    Returns:
        str: Sentiment label (e.g., 'positive', 'negative', 'neutral').
    """
    positive_words = {'good', 'great', 'excellent', 'happy', 'love', 'fantastic', 'positive'}
    negative_words = {'bad', 'terrible', 'awful', 'sad', 'hate', 'horrible', 'negative'}

    words = set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()))
    pos_count = len(words & positive_words)
    neg_count = len(words & negative_words)

    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'


@mcp.tool
def entity_extractor(text: str) -> dict:
    """
    Extract named entities from the given text using Hugging Face NER model.

    Args:
        text: The document content.

    Returns:
        dict: Extracted entities categorized by type (e.g., persons, organizations, locations).
    """
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    payload = {"inputs": text}

    response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        logger.error(f"Hugging Face API request failed with status code {response.status_code}: {response.text}")
        return {"error": f"API request failed with status code {response.status_code}",
                "details": response.text}

    data = response.json()

    entities = {"PER": set(), "ORG": set(), "LOC": set(), "MISC": set()}

    for item in data:
        entity_type = item.get("entity_group", item.get("entity"))
        word = item.get("word")
        if entity_type in entities:
            entities[entity_type].add(word)

    readable_entities = {
        "person": sorted(list(entities["PER"])),
        "organization": sorted(list(entities["ORG"])),
        "location": sorted(list(entities["LOC"])),
    }
    return readable_entities


@mcp.tool
def tone_classifier(text: str) -> str:
    """
    Classify the tone of the given text.
    Formal words are: therefore, however, moreover, thus, consequently, furthermore.
    Informal words are: cool, awesome, dude, buddy, yeah, lol, omg.

    Args:
        text: The document content.

    Returns:
        str: Tone label (e.g., 'formal', 'informal', 'neutral').
    """
    formal_words = {'therefore', 'however', 'moreover', 'thus', 'consequently', 'furthermore'}
    informal_words = {'cool', 'awesome', 'dude', 'buddy', 'yeah', 'lol', 'omg'}

    words = set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()))
    formal_count = len(words & formal_words)
    informal_count = len(words & informal_words)

    if formal_count > informal_count:
        return 'formal'
    elif informal_count > formal_count:
        return 'informal'
    else:
        return 'neutral'


def create_mcp_server() -> FastMCP:
    return mcp