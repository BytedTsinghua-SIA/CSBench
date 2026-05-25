"""
Data loading and formatting utilities module
"""
import json
import csv
import random
from typing import List, Dict, Any, Optional


def load_jsonlines(file_name: str) -> List[Dict[str, Any]]:
    """
    Load JSONL format file
    
    Args:
        file_name: Path to JSONL file
        
    Returns:
        List containing all JSON objects
    """
    # TODO: Implement this function
    raise NotImplementedError("load_jsonlines not implemented")


def load_csv(file_name: str) -> List[str]:
    """
    Load CSV file and extract prompt_text column
    
    Args:
        file_name: Path to CSV file
        
    Returns:
        List containing all prompt_text values
    """
    # TODO: Implement this function
    raise NotImplementedError("load_csv not implemented")


def nshot_chats(
    nshot_data: List[Dict[str, Any]], 
    n: int, 
    question: str, 
    answer: Optional[str], 
    mode: str,
    fixed_examples: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, str]]:
    """
    Create n-shot chat format data
    
    Args:
        nshot_data: Example data for few-shot
        n: Number of few-shot examples
        question: Current question
        answer: Current answer (required for train mode, None for test mode)
        mode: 'train' or 'test'
        fixed_examples: Fixed few-shot examples (if provided, will use these instead of random sampling)
        
    Returns:
        Formatted chat message list
    """
    # TODO: Implement this function
    raise NotImplementedError("nshot_chats not implemented")


def extract_ans_from_response(answer: str) -> str:
    """
    Extract answer from model response
    
    Args:
        answer: Model generated response string
        
    Returns:
        Extracted answer (with special characters removed)
    """
    # TODO: Implement this function
    return ""

