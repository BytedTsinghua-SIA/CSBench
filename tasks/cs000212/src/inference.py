"""
Inference module
"""
from tqdm import tqdm
from typing import List, Dict, Any, Tuple, Optional

from .data_utils import (
    load_jsonlines, 
    load_csv, 
    nshot_chats, 
    extract_ans_from_response
)
from .config import DataConfig


def get_response(generator, chats: List[Dict[str, str]]) -> str:
    """
    Get response from model
    
    Args:
        generator: Text generation pipeline
        chats: Chat message list
        
    Returns:
        Model generated response content
    """
    # TODO: Implement this function
    return ""


def evaluate_gsm8k_public(
    generator,
    test_file: str,
    train_file: str,
    data_config: DataConfig,
    fixed_examples: Optional[List[Dict[str, Any]]] = None
) -> Tuple[List[str], float]:
    """
    Evaluate GSM8K public test set
    
    Args:
        generator: Text generation pipeline
        test_file: Test data file path
        train_file: Training data file path (for few-shot)
        data_config: Data configuration
        fixed_examples: Fixed few-shot examples
        
    Returns:
        (Predicted answer list, accuracy)
    """
    gsm8k_test_public = load_jsonlines(test_file)
    gsm8k_train = load_jsonlines(train_file)
    
    gsm8k_predictions = []
    correct = 0
    total = len(gsm8k_test_public)
    
    progress_bar = tqdm(
        total=total, 
        desc='GSM8K Public Test Data Evaluation', 
        postfix='Current Accuracy = 0.000'
    )
    
    for i, qna in enumerate(gsm8k_test_public):
        messages = nshot_chats(
            nshot_data=gsm8k_train,
            n=data_config.test_n_shot,
            question=qna['question'],
            answer=None,
            mode='test',
            fixed_examples=fixed_examples if data_config.use_fixed_few_shot else None
        )
        
        response = get_response(generator, messages)
        pred_ans = extract_ans_from_response(response)
        true_ans = extract_ans_from_response(qna["answer"])
        
        if pred_ans == true_ans:
            correct += 1
        
        gsm8k_predictions.append(pred_ans)
        progress_bar.set_postfix_str(f'Current Accuracy = {correct/(i+1):.3f}')
        progress_bar.update()
    
    progress_bar.close()
    accuracy = correct / total if total > 0 else 0.0
    
    print(f'GSM8K Public Test Data Evaluation Complete, Total Accuracy: {accuracy:.3f}')
    
    return gsm8k_predictions, accuracy


def infer_gsm8k_private(
    generator,
    test_file: str,
    train_file: str,
    data_config: DataConfig,
    fixed_examples: Optional[List[Dict[str, Any]]] = None
) -> List[str]:
    """
    Perform inference on GSM8K private test set
    
    Args:
        generator: Text generation pipeline
        test_file: Test data file path
        train_file: Training data file path (for few-shot)
        data_config: Data configuration
        fixed_examples: Fixed few-shot examples
        
    Returns:
        Predicted answer list
    """
    gsm8k_test_private = load_jsonlines(test_file)
    gsm8k_train = load_jsonlines(train_file)
    
    gsm8k_predictions = []
    total = len(gsm8k_test_private)
    
    progress_bar = tqdm(
        total=total, 
        desc='GSM8K Private Test Data Inference'
    )
    
    for qna in gsm8k_test_private:
        messages = nshot_chats(
            nshot_data=gsm8k_train,
            n=data_config.test_n_shot,
            question=qna['question'],
            answer=None,
            mode='test',
            fixed_examples=fixed_examples if data_config.use_fixed_few_shot else None
        )
        
        response = get_response(generator, messages)
        pred_ans = extract_ans_from_response(response)
        gsm8k_predictions.append(pred_ans)
        
        progress_bar.update()
    
    progress_bar.close()
    print('GSM8K Private Test Data Inference Complete')
    
    return gsm8k_predictions


def evaluate_ailuminate(
    generator,
    test_file: str
) -> List[str]:
    """
    Evaluate AILuminate test set
    
    Args:
        generator: Text generation pipeline
        test_file: Test data file path
        
    Returns:
        Predicted response list
    """
    ailuminate_test = load_csv(test_file)
    ailuminate_predictions = []
    total = len(ailuminate_test)
    
    progress_bar = tqdm(
        total=total, 
        desc='AILuminate Test Data Evaluation'
    )
    
    for question in ailuminate_test:
        message = [{
            'role': 'user',
            'content': question
        }]
        
        response = get_response(generator, message)
        ailuminate_predictions.append(response)
        
        progress_bar.update()
    
    progress_bar.close()
    print('AILuminate Test Data Evaluation Complete')
    
    return ailuminate_predictions

