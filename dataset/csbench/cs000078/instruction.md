# MiniBERT Default Final Project

## Background
The CS224n default final project requires you to re-implement the core components of BERT (“MiniBERT”) to gain a deeper understanding of the Transformer encoder. You will build multi-head self-attention, add&norm blocks, embedding layers, an AdamW optimizer, and downstream classifiers that operate on BERT embeddings for tasks such as Stanford Sentiment Treebank (SST) sentiment analysis. The starter kit in `project/minbert-default-final-project-main` includes a full training harness, tokenizer, dataset utilities, and sanity checks described in the official handout.

## Requirements
1. Complete the TODOs in `bert.py`: implement `BertSelfAttention.attention`, `BertLayer.add_norm`, `BertLayer.forward`, and `BertModel.embed` so that the encoder reproduces the Transformer equations and passes `sanity_check.py`.
2. Fill in `optimizer.AdamW.step` following the AdamW paper (bias-corrected first/second moments plus decoupled weight decay) to train both the encoder and downstream heads.
3. Finish `classifier.BertSentimentClassifier` so it can freeze or finetune the encoder and return 5-class logits for SST sentences.
4. Use the provided data loaders (`datasets.py`) and evaluation helpers (`evaluation.py`) to train/validate models; keep helper utilities intact so loading HuggingFace checkpoints and packaging submissions with `prepare_submit.py` continue to work.
5. (Optional for custom extensions) Implement the multi-task classifier scaffold in `multitask_classifier.py` to share the encoder across sentiment classification, paraphrase detection, and semantic similarity.

## Provided Files
- `bert.py`, `base_bert.py`, `tokenizer.py`, `config.py`, `utils.py`: core MiniBERT architecture and shared helpers.
- `optimizer.py`: AdamW optimizer skeleton plus `optimizer_test.py` reference inputs.
- `classifier.py`, `multitask_classifier.py`, `datasets.py`, `evaluation.py`: downstream models, data pipelines, and evaluation utilities.
- `run.sh`, `setup.sh`, `prepare_submit.py`, `sanity_check.py`, `data/`, `predictions/`: scripts, sanity data, and submission helpers.
- The `src_correct` directory contains a full reference solution; `src` mirrors the same structure but leaves the TODO sections unimplemented for students.