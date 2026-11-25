# Automatic pull request merging

`.github/workflows/auto-merge.yml` checks open, non-draft pull requests into
`main` when they change and every five minutes. It requires at least one check
run, waits for every check and commit status to succeed, checks the current head
SHA, and asks GitHub to merge using a merge commit and delete the head branch.
Branch protection, required reviews and other GitHub rules still apply. A
pull request with no checks, failing checks, unresolved conflicts, or unmet
protection requirements is not merged. Merge queues are not supported by this
workflow. Deletion of a fork's branch requires permission on that fork.

`.github/workflows/pull-request-checks.yml` runs the site tests on pull requests.
The merge workflow executes only the trusted workflow from the base branch; it
does not check out or run pull request code. Nevertheless, automatically
merging every passing pull request can merge unwanted or malicious changes.
Use branch protection and required reviews if human approval is needed.

These workflows take effect only after they are merged into `main`. GitHub
Actions must have permission to write repository contents and pull requests.
If a merge or deletion fails, inspect the workflow run and repository rules.
To also delete branches after **manual** merges, an administrator must enable
Settings → General → Pull Requests → Automatically delete head branches.
The Arena GitHub integration did not have permission to change that setting.

GitHub may not trigger subsequent workflows or a Pages build for merges made
with the built-in Actions token. After enabling automatic merges, verify the
Pages deployment for a merged change; if it does not update, adjust the Pages
publishing setup before relying on this workflow for site updates.
