#!/usr/bin/env python3
"""
Script to download NLP models at runtime to reduce initial image size.
This should be called during application startup.
"""

import os
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

def download_models():
    """Download required NLP models if they don't exist."""
    
    # Check if spaCy model is already downloaded
    try:
        import spacy
        nlp = spacy.load("uk_core_news_sm")
        logger.info("spaCy Ukrainian model already exists")
    except OSError:
        logger.info("Downloading spaCy Ukrainian model...")
        try:
            subprocess.run([
                sys.executable, "-m", "spacy", "download", "uk_core_news_sm"
            ], check=True)
            logger.info("spaCy Ukrainian model downloaded successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download spaCy model: {e}")
            return False
    
    # Check if transformers model is already downloaded
    model_name = "beogradjanka/bart_multitask_finetuned_for_title_and_keyphrase_generation"
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    model_dir = os.path.join(cache_dir, "models--beogradjanka--bart_multitask_finetuned_for_title_and_keyphrase_generation")
    
    if os.path.exists(model_dir):
        logger.info("Transformers model already exists in cache")
    else:
        logger.info("Downloading transformers model...")
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
            
            # Download tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            logger.info("Transformers model downloaded successfully")
        except Exception as e:
            logger.error(f"Failed to download transformers model: {e}")
            return False
    
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = download_models()
    if success:
        print("All models downloaded successfully")
        sys.exit(0)
    else:
        print("Failed to download some models")
        sys.exit(1)
