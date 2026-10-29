# Deployment runbook (synthetic demo)

## Application rollout process

1. Build from the release branch.  
2. Run smoke tests in staging.  
3. Obtain change approval from operations.  
4. Deploy to production using the standard rollout playbook.  
5. Monitor error rate; rollback if thresholds are exceeded.

## Rollback

Use the rollback runbook section in the operations guide if deployment fails.
