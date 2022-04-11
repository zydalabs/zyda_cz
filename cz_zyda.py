import os
import re

from commitizen import defaults
from commitizen.cz.base import BaseCommitizen
from commitizen.defaults import Questions
from commitizen.cz.utils import multiple_line_breaker, required_validator

__all__ = ["ConventionalCommitsCz"]

def parse_scope(text):
    if not text:
        return ""

    scope = text.strip().split()
    if len(scope) == 1:
        return scope[0]

    return "-".join(scope)


def parse_subject(text):
    if isinstance(text, str):
        text = text.strip(".").strip()

    return required_validator(text, msg="Subject is required.")
    
class ZydaCz(BaseCommitizen):
    # Questions = Iterable[MutableMapping[str, Any]]
    # It expects a list with dictionaries.
    def questions(self) -> Questions:
        """Questions regarding the commit message."""
        questions = [
            {
                "type": "list",
                "name": "prefix",
                "message": "Select the type of change you are committing",
                "choices": [
                    {
                        "value": "Bug",
                        "name": "Bug: non-breaking change which fixes an issue",
                        "key": "b",
                    },
                    {
                        "value": "Chore",
                        "name": (
                            "Chore: updating build tasks, package manager configs, etc; no production code change"
                        ),
                        "key": "c",
                    },
                    {
                        "value": "Docs",
                        "name": "Docs: Documentation only changes",
                        "key": "d",
                    },
                    {
                        "value": "Feature",
                        "name": "Feature: Add a new feature",
                        "key": "f",
                    },
                    {
                        "value": "Fix",
                        "name": "Fix: A bug fix",
                        "key": "x",
                    },
                    {
                        "value": "Hotfix",
                        "name": "Hotfix: A bug fix",
                        "key": "h",
                    },
                    {
                        "value": "Refactor",
                        "name": (
                            "Refactor: A code change that neither fixes "
                            "a bug nor adds a feature"
                        ),
                        "key": "r",
                    },
                    {
                        "value": "Release",
                        "name": (
                            "Release: release a new version of the project"
                            "scripts (example scopes: GitLabCI)"
                        ),
                        "key": "z",
                    },
                    {
                        "value": "Test",
                        "name": (
                            "Test: Adding missing or correcting " "existing tests"
                        ),
                        "key": "t",
                    },
                ],
            },
            {
                "type": "input",
                "name": "scope",
                "message": (
                    "What is the scope of this change? (class or file name): (press [enter] to skip)\n"
                ),
                "filter": parse_scope,
            },
            {
                "type": "input",
                "name": "subject",
                "filter": parse_subject,
                "message": (
                    "Write a short and imperative summary of the code changes: (lower case and no period)\n"
                ),
            },
            {
                "type": "input",
                "name": "body",
                "message": (
                    "Provide additional contextual information about the code changes: (press [enter] to skip)\n"
                ),
                "filter": multiple_line_breaker,
            },
            {
                "type": "confirm",
                "message": "Is this a BREAKING CHANGE? Correlates with MAJOR in SemVer",
                "name": "is_breaking_change",
                "default": False,
            },
            {
                "type": "input",
                "name": "footer",
                "message": (
                    "Footer. Information about Breaking Changes and "
                    "reference issues that this commit closes: (press [enter] to skip)\n"
                ),
            },
        ]
        return questions

    def message(self, answers: dict) -> str:
        prefix = answers["prefix"]
        scope = answers["scope"]
        subject = answers["subject"]
        body = answers["body"]
        footer = answers["footer"]
        is_breaking_change = answers["is_breaking_change"]

        if scope:
            scope = f"/{scope}"
        if body:
            body = f"\n\n{body}"
        if is_breaking_change:
            footer = f"BREAKING CHANGE: {footer}"
        if footer:
            footer = f"\n\n{footer}"

        message = f"{prefix}{scope}: {subject}{body}{footer}"

        return message

    def example(self) -> str:
        """Provide an example to help understand the style (OPTIONAL)

        Used by `cz example`.
        """
        return 'Problem with user (#321)'

    def schema(self) -> str:
        return (
            "<type>(<scope>): <subject>\n"
            "<BLANK LINE>\n"
            "<body>\n"
            "<BLANK LINE>\n"
            "(BREAKING CHANGE: )<footer>"
        )

    def schema_pattern(self) -> str:
        PATTERN = (
            r"(chore|docs|feat|fix|init|refactor|release|style|test)"
            r"(\(\S+\))?!?:(\s.*)"
        )
        return PATTERN

    def info(self) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "conventional_commits_info.txt")
        with open(filepath, "r") as f:
            content = f.read()
        return content
    
    def process_commit(self, commit: str) -> str:
        pat = re.compile(self.schema_pattern())
        m = re.match(pat, commit)
        if m is None:
            return ""
        return m.group(3).strip()


discover_this = ZydaCz  # used by the plug-in system
