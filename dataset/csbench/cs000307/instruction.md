# Checkpoint 4: Measuring the Real World

## Overview

By this point in the course, you have implemented the Transmission Control Protocol in an almost fully standards-compliant manner. TCP implementations are arguably the world's single most popular computer program, found in billions of devices. This checkpoint focuses on measuring the long-term statistics of some real-world Internet paths rather than using your TCP implementation.

## Core Task

Choose and characterize at least three "interesting" Internet paths. Each path will be between one computer (e.g., your laptop, or a myth or cardinal machine) and another host. To make the path "interesting", it will either:

1. Go some significant distance (RTT greater than 100 ms), or
2. Include at least one "interesting" link along the way (e.g., a Wi-Fi or tethered cellular or satellite link).

Your final report should include a mix—at least one long-distance path (ideally without any wireless links) and at least one path that includes an "interesting" link.

## Data Collection Requirements

For each path, you must measure and analyze the following statistics:

### 1. Path Selection and Tracing

- Choose a remote host on the Internet to ping
- Use `mtr` or `traceroute` commands to trace the route between your machine and the host
- Suggested remote hosts for long-distance paths:
  - www.cs.ox.ac.uk (Oxford University CS department webserver, United Kingdom)
  - 162.105.253.58 (Computer Center of Peking University, China)
  - www.canterbury.ac.nz (University of Canterbury webserver, New Zealand)
  - 41.186.255.86 (MTN Rwanda)
  - A friend's VM on the CS144 private network
  - Preferred: an original choice with RTT ≥ 100ms or requiring wireless links

### 2. Ping Data Collection

- Run ping for at least one hour to collect path data
- Command example: `ping -D -n -i 0.2 hostname | tee data.txt`
- Parameters: `-D` (timestamps), `-n` (no DNS lookup), `-i 0.2` (0.2s intervals)
- Note: Default ping size every 0.2 seconds is acceptable, but do not flood networks faster than this

## Data Analysis Requirements

Using your preferred programming language and graphing tools, compute and graph:

### Delivery Statistics

1. Overall delivery rate (replies received / requests sent)
2. Longest consecutive string of successful pings
3. Longest burst of consecutive losses

### Path Analysis

4. Geographic path analysis from `mtr`/`traceroute` results

### Loss Correlation Analysis

5. Autocorrelation of packet loss over time:
   - Conditional delivery rates for k = -10 to +10
   - Compare conditional vs. unconditional delivery rates
   - Assess loss independence/burstiness

### RTT Analysis

6. Minimum RTT observed
7. Maximum RTT observed
8. RTT time series graph (time of day vs. milliseconds)
9. Cumulative Distribution Function of RTT distribution
10. RTT correlation scatter plot (RTT*N vs. RTT*{N+1})

### Throughput Analysis

11. Brief experiments with higher data rates:
    - Vary packet size (-s, max 1400) and frequency (-i)
    - Graph reply data rate vs. request data rate
    - Identify maximum achievable throughput

### Conclusions

12. Analysis of network path behavior and surprises
13. Comparisons between characterized paths

## Submission Requirements

Submit your complete report as a PDF via Gradescope, including all graphs, statistics, and analysis.

## Important Notes

- A default-sized ping every 0.2 seconds is acceptable
- Do not flood networks with traffic faster than this for extended periods
- For higher-rate experiments, limit to brief (< 10 seconds) tests
- Disclose any collaborators or collaboration in your writeup
