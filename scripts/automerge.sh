#!/bin/bash -e

# Inspired by https://github.com/cdown/travis-automerge
# See https://github.com/cdown/travis-automerge/blob/90cc2a65a887d0a80f78c098892f29d458b29813/LICENSE

: "${BRANCHES_TO_MERGE_REGEX?}" "${BRANCH_TO_MERGE_INTO?}"
: "${GITHUB_TOKEN?}" "${GITHUB_REPO?}"

git config --global user.email "support@alertlogic.com"
git config --global user.name "CI bot"

if [ "$GITHUB_REPOSITORY" != "$GITHUB_REPO" ]; then
    printf "PR repo %s is not current %s, exiting\\n" \
        "$GITHUB_REPOSITORY" "$GITHUB_REPO" >&2
    exit 0
fi

if ! grep -q "$BRANCHES_TO_MERGE_REGEX" <<< "$GITHUB_HEAD_REF"; then
    printf "Current branch %s doesn't match regex %s, exiting\\n" \
        "$GITHUB_HEAD_REF" "$BRANCHES_TO_MERGE_REGEX" >&2
    exit 0
fi

# Since Travis does a partial checkout, we need to get the whole thing
repo_temp=$(mktemp -d)
git clone "https://github.com/$GITHUB_REPO" "$repo_temp"

# shellcheck disable=SC2164
cd "$repo_temp"

printf 'Fetching branch %s to merge to %s\n' "$GITHUB_HEAD_REF" "$BRANCH_TO_MERGE_INTO" >&2
git fetch origin $GITHUB_HEAD_REF:$GITHUB_HEAD_REF

printf 'Checking out %s\n' "$BRANCH_TO_MERGE_INTO" >&2
git checkout "$BRANCH_TO_MERGE_INTO"

MERGE_COMMIT_MESSAGE=$(git show-branch --no-name $GITHUB_HEAD_REF)

printf 'Merging %s using "%s" message for if merge commit\n' "$GITHUB_HEAD_REF" "${MERGE_COMMIT_MESSAGE}" >&2
git merge "$GITHUB_HEAD_REF" -m "${MERGE_COMMIT_MESSAGE}"

printf 'Pushing to %s\n' "$GITHUB_REPO" >&2

push_uri="https://$GITHUB_TOKEN@github.com/$GITHUB_REPO"

# Redirect to /dev/null to avoid secret leakage
#git push "$push_uri" "$BRANCH_TO_MERGE_INTO" >/dev/null 2>&1
git push "$push_uri" "$BRANCH_TO_MERGE_INTO"
#git push "$push_uri" :"$GITHUB_HEAD_REF" >/dev/null 2>&1
git push "$push_uri" :"$GITHUB_HEAD_REF" || true
