# CI/CD Pipeline and Automation (Part 11)

## Background
You are designing a CI/CD pipeline for a small full-stack project, including automated linting, tests, build, deployment, versioning, and operational checks.

## Core Tasks
1. Workflow setup and quality gates:
   - Define initial workflows for hello world, linting, testing, building, and e2e checks.
   - Ensure workflows run on pull requests and only deploy on the main branch.
2. Deployment and health checks:
   - Configure deployment settings and health check endpoints for reliable releases.
   - Add periodic health checks and notification steps for failures and successes.
3. Versioning and repository hygiene:
   - Add automated tag/versioning steps with skip rules.
   - Define branch protection rules and review requirements.

## Scoring Points (1-3)
- Workflows include required steps, triggers, and guard conditions.
- Deployment configuration includes health checks and safe rollout strategy.
- Versioning and branch protection rules are correctly defined.
