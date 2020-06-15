#!/usr/bin/env python3
import requests
from packaging import version
from argparse import ArgumentParser
import re
import os
import datetime
import json
from functools import reduce


def make_auth_header(token):
    return {"Authorization": f"token {token}"}


def list_github_tags(token, repo):
    return requests.get(f"https://api.github.com/repos/{repo}/tags", headers=make_auth_header(token)).json()


def list_version_tags(github_tags):
    return list(filter(lambda v: isinstance(v, version.Version), map(lambda t: version.parse(t['name']), github_tags)))


def reduce_tag(acc, tag):
    acc[version.parse(tag['name'])] = tag
    return acc


def make_tags_search_hash(github_tags):
    return reduce(reduce_tag, github_tags, {})


def get_latest_version(parsed_tags):
    sorted_tags = sorted(parsed_tags, reverse=True)
    if sorted_tags:
        return sorted_tags[0]
    else:
        return version.parse("0.0.0")


def get_branch_commit_sha(token, repo, branch):
    url = f"https://api.github.com/repos/{repo}/branches/{branch}"
    return requests.get(url, headers=make_auth_header(token)).json()['commit']['sha']


def get_branch_commit_message(token, repo, branch):
    url = f"https://api.github.com/repos/{repo}/branches/{branch}"
    return requests.get(url, headers=make_auth_header(token)).json()['commit']['commit']['message']


def create_lightweight_tag(token, repo, tag_obj):
    url = f"https://api.github.com/repos/{repo}/git/refs"
    r = requests.post(url, headers=make_auth_header(token), json=tag_obj)
    # meh, just roughly
    if 201 <= r.status_code < 300:
        return True
    else:
        print(
            f"Failed to create tag {json.dumps(tag_obj, indent=4)}, because {r.status_code} {json.dumps(r.json(), indent=4)}")
        return False


def create_annotated_tag(token, repo, tag_obj):
    url = f"https://api.github.com/repos/{repo}/git/tags"
    r = requests.post(url, headers=make_auth_header(token), json=tag_obj)
    # meh, just roughly
    if 201 <= r.status_code < 300:
        return True
    else:
        print(
            f"Failed to create tag {json.dumps(tag_obj, indent=4)}, because {r.status_code} {json.dumps(r.json(), indent=4)}")
        return False


def make_lightweight_tag_object(version, sha):
    return {
        "ref": f"refs/tags/v{version}",
        "sha": sha
    }


def make_annotated_tag_object(version, tag_message, sha, tagger='CI Bot', email='travis@travis'):
    date = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    return {
        "tag": f"v{version}",
        "message": tag_message,
        "object": sha,
        "type": "commit",
        "tagger": {
            "name": tagger,
            "email": email,
            "date": date
        }
    }


if __name__ == "__main__":
    parser = ArgumentParser(description="Calculates and returns new version based on the version tags of the "
                                        "specified repo, only PEP440 versions are taken into account. "
                                        "If micro version is not passed, "
                                        "version is incremented by --increment, default is 1")
    parser.add_argument("-t", "--token", dest="token",
                        help="github api token, if not set taken from GITHUB_SECRET_TOKEN",
                        default=os.getenv('GITHUB_SECRET_TOKEN'))
    parser.add_argument("-c", "--create_release", action="store_true", default=False,
                        dest="do_release", help="create calculated new release")
    parser.add_argument("-b", "--branch", dest="branch", help="branch to tag", default="master")
    parser.add_argument("-r", "--repo", dest="repo", help="github repo", required=True)
    parser.add_argument("-re", "--commit_message_regex", dest="regex", default=".*",
                        help="commit regex to be tagged, if not set any commit on given branch will be tagged")
    parser.add_argument("-m", "--micro", dest="micro", type=int, help="new micro version <major>.<minor>.<micro>")
    parser.add_argument("-i", "--increment", dest="increment", help="increment minor version by this number",
                        default=1, type=int)
    options = parser.parse_args()
    sec_token = options.token
    if not sec_token:
        print("Secret token is not set neither by parameter nor by environment variable")
        exit(1)
    repo = options.repo
    do_release = options.do_release
    newmicro = options.micro
    increment = options.increment
    branch = options.branch
    regex = options.regex
    tags = list_github_tags(sec_token, repo)
    tag_search = make_tags_search_hash(tags)
    parsed_tags = list_version_tags(tags)
    latest = get_latest_version(parsed_tags)
    latest_tag_sha = tag_search[latest]['commit']['sha']
    ma = latest.major
    mi = latest.minor
    mic = latest.micro
    if newmicro:
        if mic > newmicro:
            print(f"latest micro version {ma}.{mi}.{mic} is bigger than provided, provided {newmicro}")
            exit(1)
        else:
            newrel_version = f"{ma}.{mi}.{newmicro}"
    else:
        newrel_version = f"{ma}.{mi}.{mic + 1}"
    new_commit_sha = get_branch_commit_sha(sec_token, repo, branch)
    commit_message = get_branch_commit_message(sec_token, repo, branch)
    tag_anno_obj = make_annotated_tag_object(newrel_version, commit_message, new_commit_sha)
    tag_ref_obj = make_lightweight_tag_object(newrel_version, new_commit_sha)
    create_log = f"Will create tag \n{json.dumps(tag_anno_obj, indent=4)} \n" \
                 f" new commit {new_commit_sha}, tag {newrel_version}\n " \
                 f"old commit {latest_tag_sha}, tag {str(latest)}"
    if re.match(regex, commit_message):
        print(f"Commit message {commit_message} matched {regex}, proceeding to release {newrel_version}")
        if latest_tag_sha == new_commit_sha:
            print(f"Release aborted release {latest} already created for {new_commit_sha}")
        else:
            if do_release:
                print(create_log)
                create_annotated_tag(sec_token, repo, tag_anno_obj)
                create_lightweight_tag(sec_token, repo, tag_ref_obj)
            else:
                print(create_log)
                print("Release aborted, specify -c to actually do release")
    else:
        print(f"Commit message {commit_message} don't match {regex}, aborted release")
