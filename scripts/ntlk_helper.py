import logging
import nltk
import os
from pathlib import Path
from typing import Iterable, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ensure nltk data dir inside venv and tell NLTK where to look
venv_nltk = Path('.venv') / 'nltk_data'
venv_nltk.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('NLTK_DATA', str(venv_nltk))


def _nltk_path_for(resource: str) -> str:
    mapping = {
        'words': 'corpora/words',
        'punkt': 'tokenizers/punkt',
        'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng': 'taggers/averaged_perceptron_tagger_eng',
    }
    return mapping.get(resource, resource)


def ensure_nltk_resources(resources: Iterable[str] | None = None) -> Dict[str, bool]:
    """
    Check each resource; download into .venv/nltk_data if missing.
    Returns a dict mapping resource -> True if available after this call.
    """
    resources = resources or ['words', 'punkt', 'averaged_perceptron_tagger_eng']
    results: Dict[str, bool] = {}
    for res in resources:
        path = _nltk_path_for(res)
        try:
            nltk.data.find(path)
            logger.info("NLTK resource found: %s", res)
            results[res] = True
        except LookupError:
            logger.info("NLTK resource missing, downloading: %s", res)
            try:
                nltk.download(res, download_dir=str(venv_nltk), quiet=True)
                # verify after download
                try:
                    nltk.data.find(path)
                    results[res] = True
                    logger.info("Downloaded NLTK resource: %s", res)
                except LookupError:
                    results[res] = False
                    logger.error("Downloaded but could not find resource: %s", res)
            except Exception as exc:
                results[res] = False
                logger.exception("Failed to download NLTK resource %s: %s", res, exc)
    return results


# call early, before any NLP code runs
ensure_nltk_resources()