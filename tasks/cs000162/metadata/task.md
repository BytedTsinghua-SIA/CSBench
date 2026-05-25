# 10-708 PGM (Spring 2019): Homework 2

## Background

This homework focuses on probabilistic graphical models and their applications, covering sequential models for part-of-speech tagging, variational inference, importance sampling, and Markov Chain Monte Carlo methods. The assignment builds upon concepts from unsupervised Hidden Markov Models (HMMs) and extends to supervised learning, discriminative models, and approximate inference techniques.

## Core Tasks

### 1. Sequential Models for POS Tagging [30 pts]

#### Background

Part-of-speech (POS) tagging involves categorizing each word in a sentence with its corresponding part of speech tag. For example:

- Sentence: The reaction in the newsroom was emotional .
- POS tags: DET NOUN ADP DET NOUN VERB ADJ .

This problem uses the universal tagset (12 tags) and the Penn Treebank (PTB) corpus. The data can be downloaded from: https://sailinglab.github.io/pgm-spring-2019/assets/assignments/hw2/pos-data.zip

The data folder contains:

- `train set.npy`: training sentences
- `test set.npy`: testing sentences
- `vocab.txt`: vocabulary
- `tagset.txt`: tagset

#### 1.1 POS Tagging with HMM [10 pts]

**Task 1.1.1 [1 point]**
Define an HMM for modeling sequences of words and POS tags:

- Denote the sequence of T words as x := (x₁, ..., xₜ) and corresponding POS tags as y := (y₁, ..., yₜ)
- Specify how observations and latent states are represented
- Specify the parameters of the model

**Task 1.1.2 [3 points]**
Given a set of tagged training sentences:

- Describe and implement the learning algorithm for the HMM
- Use smoothing with λ = 0.01 for emission probability estimation (due to sparsity)
- Report:
  - The obtained state transition matrix A (rounded/truncated to reasonable precision for visualization)
  - The negative log likelihood for the HMM on train and test sets (specify whether reporting −log Pθ(x) or −log Pθ(x, y))

**Task 1.1.3 [6 points]**
Implement inference for finding the most likely sequence of tags:

- Solve: y\* = arg max_y P_HMM(y | x)
- Describe and implement an efficient algorithm (hint: use primitives from Baum-Welch algorithm)
- Infer the most likely sequences of tags for test set sentences
- Report:
  - Per-word accuracy
  - Confusion matrix between tags (visualized)

#### 1.2 POS Tagging with Linear-Chain CRF [20 pts]

**Task 1.2.1 [2 points]**
Show that the conditional distribution P(y | x) from an HMM is a particular kind of linear chain CRF (hint: write down the complete likelihood for the HMM as a product of exponents).

**Task 1.2.2 [2 points]**
Mathematically define a linear chain CRF model with potentials Ψₜ(yₜ, yₜ₋₁, x) that are log-linear functions of the following features:

- (a) Identity of the given word xₜ and the current tag yₜ
- (b) Identity for whether xₜ is the first word in the sentence, and the current tag yₜ
- (c) Identity for whether xₜ is the last word in the sentence, and the current tag yₜ
- (d) Identity of the previous word xₜ₋₁ and the current tag yₜ
- (e) Identity of the next word xₜ₊₁ and the current tag yₜ
- (f) Identity for whether xₜ contains a capital letter, and the current tag yₜ
- (g) Identity of the previous tag yₜ₋₁ and the current tag yₜ

**Task 1.2.3 [2 points]**
Derive an inference algorithm for determining the most likely sequence of POS tags under the CRF model (hint: similar to the HMM algorithm in 1.1).

**Task 1.2.4 [2 points]**
Derive a maximum likelihood learning algorithm for the linear chain CRF.

**Task 1.2.5 [10 points]**
Implement the learning and inference procedures for CRF:

- Pre-process training and test data to incorporate the additional features defined for potential functions
- Implement the learning and inference algorithms as described above
  - **Constraint**: External libraries providing complete CRF implementations are prohibited (0/10 credit if used)
  - **Allowed**: External packages for solving optimization problems as building blocks (including PyTorch or TensorFlow)
- Train the model on the train set and run inference on the test set
- Report:
  - Negative log conditional likelihood (−log P(y | x)) on both training and test sets
  - Per-word accuracy and confusion matrix for model predictions on the test set

**Task 1.2.6 [2 points]**
Discuss advantages/disadvantages of HMM (generative) vs. CRF (discriminative) approaches for sequence prediction. What if we have limited labeled data?

### 2. Variational Inference (VI) [40 pts]

#### 2.1 Warm-up: VI vs. MCMC [10 pts]

Compare Variational Inference (VI) with Markov Chain Monte Carlo (MCMC). For each item below, link to either VI or MCMC and reason briefly (1-2 sentences):

1. [1 point] Inference results are generally closer to target distributions.
2. [1 point] Non-parametric.
3. [1 point] Amenable to batched computation using GPUs.
4. [1 point] Transform inference into optimization problems.
5. [1 point] Easier to integrate with back-propagation.
6. [1 point] Involves more stochasticity.
7. [1 point] Easier to set the termination condition for the computational loop.
8. [1 point] Higher variance under limited computational resources.
9. [1 point] Problem case: Estimating a topic model with online streaming text data.
10. [1 point] Problem case: Estimating a topic model from a very small text corpus.
11. [Bonus, 1 point] Problem case: Posterior inference with non-conjugate distributions.
12. [Bonus, 1 point] More naturally fit with stick-breaking process.

#### 2.2 VI in Practice [30 pts]

##### 2.2.1 A Review of the Vanilla LDA [9 pts]

Given a collection of text documents D = {w_d}ᵈ₌₁ᴰ, where w_d is the d-th document and w_d = {w_di}ᵢ₌₁ᴺᵈ with w_di being the i-th word in w_d, and N_d as the number of words in w_d. LDA assumes each document is generated from a mixture of K topics, with mixture proportion θ_d, where each topic is a multinomial distribution parametrized by βₖ over all V words in the vocabulary.

**Generative process:**

- For k = 1 → K: Draw topic βₖ ~ Dirichlet(η)
- For each document w_d ∈ D:
  - Draw per-document mixture proportion θ_d ~ Dirichlet(α)
  - For each word w_di ∈ w_d:
    - Sample a topic indicator z_di ~ Multinomial(θ_d)
    - Sample the word w*di ~ Multinomial(β*{z_di})

Answer the following questions about LDA (no need to explain):

1. [1 point] True or False: Solving LDA involves posterior inference with non-conjugate distributions.
2. [1 point] True or False: Solving LDA using Variational EM involves non-convex optimization at E-step.
3. [2 points] Count the number of model parameters of LDA using the notations defined above.
4. [2 points] Write down the computational complexity of mean-field VI for LDA using Big O notation.
5. [2 points] Write down the memory complexity of mean-field VI for LDA using Big O notation.
6. [1 point] True or False: The vanilla LDA can be used to extract word embeddings.

##### 2.2.2 More HMMs [21 pts]

The vanilla LDA assumes each word is independently generated given topic vectors. This question enhances it by considering word order during document generation, modeling that the topic of word at index i might depend on the topic of the previous word (at index i − 1).

**HMM-enhanced LDA (HMM-LDA):**

- Assume a transition matrix T among K topics where T\_{mn} represents the probability of topic m transitioning to topic n
- For word w*di (i > 1), with probability p (0 < p < 1), sample from topic z_di; with probability 1 − p, transition from topic z*{d(i−1)}

**Altered generative process:**

- For each document w_d:
  - Sample p_d ~ Beta(γ)
  - Sample θ_d ~ Dirichlet(α)
  - For the first word (head of HMM): sample z*d1 ~ Multinomial(θ_d), w_d1 ~ Multinomial(β*{z_d1})
  - For each word w_di (i > 1):
    - Sample δ_di ~ Bernoulli(p_d)
    - If δ*di = 1: sample z_di ~ Multinomial(θ_d), then w_di ~ Multinomial(β*{z_di})
    - If δ*di = 0: sample z_di ~ Multinomial(T*{z*{d(i−1)},:}), then w_di ~ Multinomial(β*{z_di})

Use variational EM to perform posterior inference and estimate model parameters.

**Tasks:**

1. [3 points] Identify (a) the set of observed variables, (b) the set of hidden variables, (c) the set of model parameters to be estimated.
2. [3 points] Based on the altered generative process, draw the new graphical model for HMM-enhanced LDA (HMM-LDA).
3. [2 points] Write down the joint distribution defined by this generative process.
4. [3 points] Define variational distributions over hidden variables using proper distributions and variational parameters.
5. [2 points] Derive the ELBO using variational distributions.
6. [4 points] Derive the update rules for all variational parameters, which will be used in the E step.
7. [4 points] Derive the update rules for all model parameters, which will be applied in the M step.
8. [Bonus, 6 points] Implement the derived variational EM algorithm for HMM-LDA using Python (≥ 3.5). Train the model on the provided Wikipedia corpus (details in bundled readme.txt). Set K = 10 topics.
9. [Bonus, 4 points] Visualize each of the learned 10 topics by printing its top 10 words with highest probabilities, both in script and write-up.

**Implementation notes for questions 8 and 9:**

- Submit a single Python script named `YourAndrewID.py` and a `requirements.txt`
- Ensure the script is executable under a clean Python (≥ 3.5) virtual environment with:
  ```
  pip install -r requirements.txt
  python YourAndrewID.py
  ```
- Tune hyper-parameters properly for convergence
- Print ELBO values after each iteration of E-step and M-step during training
- Report the iteration of convergence and the final ELBO value
- Visualize learned K topics after convergence in both stdout and write-up (similar to Figure 8 in [3])

### 3. Importance Sampling [10 pts]

Given a random distribution p(x) on x = [x₁, ..., x_D]ᵀ ∈ ℝᴰ, perform inference E\_{p(x)}[f(x)] using importance sampling with q(x) as the proposal distribution. Draw L i.i.d. samples x⁽¹⁾, ..., x⁽ᴸ⁾ from q(x), and compute:

E\_{p(x)}[f(x)] ≈ (1 / Σᵢ₌₁ᴸ uᵢ) Σᵢ₌₁ᴸ f(x⁽ⁱ⁾)uᵢ

where the (unnormalized) importance weights uᵢ = p(x⁽ⁱ⁾) / q(x⁽ⁱ⁾).

**Tasks:**

1. [2 points] Find the mean and variance of the unnormalized importance weights: E*{q(x)}[uᵢ] and Var*{q(x)}[uᵢ]. You may leave your answer in terms of E\_{p(x)}.
2. [3 points] Prove the following lemma: E\_{p(x)}[p(x)/q(x)] ≥ 1 with equality if and only if p = q.
3. [4 points] A measure of variability of two components in vector u = [u₁, ..., u_L]ᵀ is given by E*{q(x)}[(uᵢ − uⱼ)²]. Assume there exists some α > 1 such that E*{p(xᵢ)}[p(xᵢ)/q(xᵢ)] ≥ α for all i, and that both p and q can be factorized: p(x) = ∏ᵢ₌₁ᴰ pᵢ(xᵢ), and q(x) = ∏ᵢ₌₁ᴰ qᵢ(xᵢ). Show that E\_{q(x)}[(uᵢ − uⱼ)²] has exponential growth with respect to D.
4. [1 point] Use the conclusion in (c) to explain why standard importance sampling does not scale well with dimensionality and would blow up in high-dimensional cases.

### 4. Markov Chain Monte Carlo [20 pts]

Build a predictive model for the number of goals scored in Premier League games using Bayesian hierarchical modeling. Model each team's strength (attacking and defending) as latent variables. In each game, goals scored by the home team depend on the attacking strength of the home team and defending strength of the away team. Similarly, goals scored by the away team depend on the attack strength of the away team and defense strength of the home team.

**Model specification:**

- Premier League has 20 teams (indexed 0-19 as shown in Table 1)
- Each team plays 38 matches (380 games total per season)
- For game g, home team index is h(g), away team index is a(g)
- Observed goals (y*{g0}, y*{g1}) are independent Poisson random variables:
  - y*{gj} | θ*{gj} ~ Poisson(θ\_{gj}), j = 0, 1
- Log-linear model for scoring intensities:
  - log θ*{g0} = home + att*{h(g)} − def\_{a(g)}
  - log θ*{g1} = att*{a(g)} − def\_{h(g)}
- Priors:
  - home ~ N(0, τ₀⁻¹), where τ₀ = 0.0001
  - att*t ~ N(μ*{att}, τ\_{att}⁻¹)
  - def*t ~ N(μ*{def}, τ\_{def}⁻¹)
  - μ*{att} ~ N(0, τ₁⁻¹), μ*{def} ~ N(0, τ₁⁻¹), where τ₁ = 0.0001
  - τ*{att} ~ Gamma(α, β), τ*{def} ~ Gamma(α, β), where α = β = 0.1
- Identifiability constraint: att₀ = def₀ = 0 (first team as reference)

**Goal:** Estimate posterior means E*{p(θ,η|y)}[attᵢ], E*{p(θ,η|y)}[defᵢ], and E\_{p(θ,η|y)}[home]

**Tasks:**

1. [4 points] Find the joint likelihood p(y, θ, η).
2. [4 points] Write down the Metropolis-Hastings algorithm for sampling from posterior p(θ, η | y), and derive the acceptance function for a proposal distribution of your choice (e.g., isotropic Gaussian).
3. [12 points] Implement the Metropolis-Hastings algorithm for posterior inference:
   - Data: https://sailinglab.github.io/pgm-spring-2019/assets/assignments/hw2/premier_league_2013_2014.dat
   - Data format: 380×4 matrix where columns are: y*{g0}, y*{g1}, h(g), a(g)
   - Use isotropic Gaussian proposal N(0, σ²I) with starting point 0.1
   - Run MCMC chain for 5000 steps burn-in, then collect 5000 samples with thinning parameter t (i.e., run M-H for 5000t steps and collect each t-th sample)
   - Parameter sets: σ = 0.005, 0.05, 0.5, and t = 1, 5, 20, 50
   - For each parameter setting:
     - Plot trace plot of burn-in phase and MCMC samples for variable `home`
     - Estimate and report rejection ratio in a table
   - Comment on results: which parameter setting worked best?
   - Using optimal parameter setting:
     - (a) Plot posterior histogram of variable `home` from MCMC samples
     - (b) Plot estimated attacking strength E*{p(θ,η|y)}[attᵢ] vs. estimated defending strength E*{p(θ,η|y)}[defᵢ] for each team in a scatter plot, identifying team indices using Table 1 mapping

**Note:** You may use Python or MATLAB. You are NOT allowed to use any existing implementations of Metropolis-Hastings. Include all required results (figures + tables) in your writeup PDF submission, and submit your code separately.

## Data Sources

- POS tagging data: https://sailinglab.github.io/pgm-spring-2019/assets/assignments/hw2/pos-data.zip
- Premier League data: https://sailinglab.github.io/pgm-spring-2019/assets/assignments/hw2/premier_league_2013_2014.dat

## References

[1] John Lafferty, Andrew McCallum, and Fernando CN Pereira. Conditional random fields: Probabilistic models for segmenting and labeling sequence data. 2001.

[2] Slav Petrov, Dipanjan Das, and Ryan McDonald. A universal part-of-speech tagset. arXiv preprint arXiv:1104.2086, 2011.

[3] David M Blei, Andrew Y Ng, and Michael I Jordan. Latent dirichlet allocation. Journal of machine Learning research, 3(Jan):993–1022, 2003.

[4] Gianluca Baio and Marta Blangiardo. Bayesian hierarchical model for the prediction of football results. Journal of Applied Statistics, 37(2):253–264, 2010.
