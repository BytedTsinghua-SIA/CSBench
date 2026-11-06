# Lab 0: Password Cracking and Hashes

## Background
Unix-like systems store hashed passwords instead of plaintext. This lab explores how password hashing works, how preimage attacks can recover weak passwords in a toy setting, and how collision probabilities behave.

## Tasks
1. Implement the required functions in `sol.py` for Problems 2–4, including password recovery, preimage search using `hashes.txt`, collision probability calculations, and collision finding for `hashbig.py`.
2. Use the provided `hashall.py` and `hashbig.py` for hashing; do not use off-the-shelf password-cracking tools or libraries.
3. Write your written responses for Problem 1 and the theory questions in `questions.txt`.
##  Problem 1: Storing passwords

Unix-like operating systems store password hashes in a file called `/etc/shadow`.Answer the following questions:

1.  Typically, only the `root` user on a machine has access to the `shadow` file. The `shadow` file only contains passwords _hashes_ -- not the passwords themselves. In one sentence, explain why it is important to protect the hashed passwords.

1.  Look online for information about the `shadow` file format. Why does the format allow the password hashes for each user to be hashed with a different hash function?

    _Learn about the PBKDF2 hash function by reading Chapter 18.4.3 of the [Boneh-Shoup book](https://toc.cryptobook.us/book.pdf). Then answer the following questions:_

1.  What security benefit does iterating a hash function provide?

1. Say that you are using PBKDF2 to protect passwords for authenticating   to a popular web service (e.g., MIT Touchstone). How would you set the iteration count?

1. If you were instead using PBKDF2 to protect   passwords for authenticating to your laptop, would your answer be the same or different as in part (d)? Why?


## Problem 3: Collisions

In this problem, we will explore the cost of finding collisions in hash functions. The "Birthday Paradox" analysis we cover here is one of the most fundamental tools for reasoning about the security of cryptosystems, so it's important to understand.

Consider throwing $$B$$ balls into $$N$$ bins at random. That is, for each ball, we pick a bin in $$\{1, \dots, N\}$$ independently and uniformly at random, and toss the ball into that bin.

1. For a particular ball $$i$$ and bin $$k$$, what    is the probability, as a function of $$B$$ and    $$N$$, that ball $$i$$ falls into bin $$k$$? Place your answer in `problem_3a(B,N)`

1. For particular distinct balls $$i$$ and $$j$$, and for a particular bin $$k$$, what is the probability, as a function of $$B$$ and $$N$$,  that ball $$i$$ _and_ ball $$j$$ fall into bin $$k$$? Place your answer in `problem_3b(B,N)`

1.  How many _pairs_ of distinct balls $$(i,j)$$ are there in total, as a function of $$B$$? For example, if there were three balls $$(B=3)$$ there would be a total of three pairs: $$(1, 2), (1, 3), (2, 3)$$. Place your answer in `problem_3c(B)`

1.  Give a non-trivial _upper bound_, as a function of $$B$$  and $$N$$ on the probability that any two balls fall into the same bin.  In other words, you will compute an expression of the form $$\Pr[\text{two balls in same bin}] \leq \text{???}$$. Place your answer in `problem_3d(B,N)`
    
    _Hint: Use the union bound. That is, if $$B_1$$ and $$B_2$$ are two bad events, then the probability that either bad event occurs is at most the sum of $$\Pr[B_1]$$ and $$\Pr[B_2]$$, even if the events are dependent. That is: $$\Pr[B_1 \lor B_2] \leq \Pr[B_1] + \Pr[B_2]$$._
   
1.  Let $$H \colon \{0,1\}^n \to \{0,1\}^n$$ be     a random function. That is, for all $$x \in \{0,1\}^n$$, the value $$H(x)$$ is a random $$n$$-bit string chosen independent and uniformly at random. Place your answer in `problem_3e(L,n)`

    Using your answer to part (D), compute give    a non-trivial upper bound on the probability    that there is a collision among $$H(x_1), H(x_2), \dots, H(x_L)$$,where $$x_1, \dots, x_L$$ are distinct $$n$$-bit    strings with $$L \ll 2^n$$.
## Scoring
- Correct outputs for `problem_2a`, `problem_2c`, and `problem_4b`.
- Completeness and clarity of `questions.txt`.
