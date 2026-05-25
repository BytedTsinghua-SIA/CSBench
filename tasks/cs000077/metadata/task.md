# CS224N Assignment 5 – Self-Attention, Pretraining, and Perceiver Variants

## Background
This task packages the coding portion of CS224N Assignment 5. You work with a character-level Transformer derived from Karpathy's `minGPT` to study how span corruption pretraining enables factual recall for a downstream question answering task: map `Where was <name> born?` questions to birth places. After replicating the vanilla GPT workflow, you extend the model with Perceiver-style down/up projection blocks to shave attention cost.

## Problem Description
1. **Datasets**  
   * `wiki.txt` – character stream for span corruption pretraining.  
   * `birth_places_train/dev/test.tsv` – tab-separated files containing `question\tanswer`.  
   * `birth_test_inputs.tsv` omits the gold answer; predictions go to `*.test.predictions`.
2. **Dataset classes**  
   * `NameDataset` is provided; it glues a training line into `question⁇answer⁇` format (with padding) and produces `(x, y)` tensors.  
   * `CharCorruptionDataset` must be implemented exactly as the spec in `dataset.py`: truncate each document to `[4, 7/8 * block_size]` characters (length sampled uniformly); select a random span (~25% on average) to mask; form `[prefix] MASK [suffix] MASK [masked_span] [PAD…]`, then shift to build input/output tensors sharing one-character offsets.
3. **Training pipeline (`run.py`)**  
   * CLI takes `function ∈ {pretrain, finetune, evaluate}`, `variant ∈ {vanilla, perceiver}`, the corpus path, IO parameter paths, and LR overrides.  
   * Implement vanilla GPT instantiation and the Perceiver variant (set `mconf.perceiver=True` and its `bottleneck_dim`).  
   * `pretrain`: train on `CharCorruptionDataset` with the provided hyperparameters; save weights to `--writing_params_path`.  
   * `finetune`: load the optional pretrained weights, create `NameDataset`, and train with epoch counts that depend on whether pretraining was provided (75 epochs cold-start, 10 when warm-starting).  
   * `evaluate`: already implemented; it samples completions, writes predictions, and prints accuracy via `utils.evaluate_places`.
4. **Model extensions (`model.py`)**  
   * Vanilla `Block` is given.  
   * Implement `DownProjectBlock`: instantiate `CausalCrossAttention`, an MLP, and a learnable latent basis `C ∈ ℝ^{1×m×d}` (Xavier uniform init). The forward pass cross-attends between the input sequence (keys/values) and the latent basis (queries) before running the MLP.  
   * Implement `UpProjectBlock`: reverse the process by cross-attending with the original input as queries and the low-dimensional stream as keys/values to restore the 𝓁-length sequence.  
5. **Baselines and reporting**  
   * Populate `london_baseline.py` (few lines) to compute the accuracy of always predicting “London” on `birth_dev.tsv`.  
   * Report dev accuracy for: vanilla finetune-only, vanilla pretrained+finetuned, and perceiver pretrained+finetuned (handout gives reference values).  
   * Answer the reflection questions in the write-up about why pretraining helps and ethical considerations.

## Specification & Hints
* Keep the block size at 128 characters for both datasets.  
* Use the `Trainer` helper with the hyperparameters embedded in `run.py` comments. The learning-rate schedule relies on token counts (warmup at `512*20`, cosine decay until `final_tokens = 200 * len(dataset) * block_size`).  
* Perceiver variant requires at least 3 blocks: Down-project, ≥1 latent block(s), and an Up-project block.  
* Tensorboard logging works out-of-the-box: `tensorboard --logdir expt/`.  
* When debugging locally without GPU, reduce `DataLoader` workers to 0 if multiprocessing fails.  
* All scripts expect to run from the directory containing `wiki.txt` and the TSV files.