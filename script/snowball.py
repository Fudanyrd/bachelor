"""
SYNOPSIS
    snowball.py <reference-list>

DESCRIPTION
    After extracting the references of collected articles (provided
    in a text file; each line is a reference item),
    this script automatically query an chat model to categorize
    and filter articles referenced by the list.

ENVIRONMENT
    API_KEY (Required): your api key
    MODEL (Required): the chat model to use
    BASE_URL (Required): the base url of model provider

DEPENDENCY
    openai>=1.0

SEE ALSO
    article.ts (file)
"""

import sys
import time
import os
import json

from openai import OpenAI

def sane_environ():
    def _raise_if_missing(key: str):
        if key not in os.environ:
            raise RuntimeError(key + " environment variable is not set")
    _raise_if_missing('API_KEY')
    _raise_if_missing('MODEL')
    _raise_if_missing('BASE_URL')


def build_prompt(item: str) -> str:
    BEFORE =  \
"""
## Background
I'm a researcher conducting a Systematic Literature Review on
Large Language Model for Automated Program Repair.

## Your Task
Given the following reference item extracted from paper:
"""
    AFTER = \
"""
Please read this carefully and find the title, authors, and year.

Next, please help me determine the relevance of this referenced article.
If the article is not about program repair, bug fix, debugging, patch synthesis, or fault/bug localization,
mark it as irrelevant. If the article is relevant to my study, judge its title
and categorize it into one of the following:

**survey**: the article is a survey, literature review, empirical study.
**technical**: the article seems to be a technical paper in which a novel methodology is proposed.
**benchmark**: the article attempts to build a dataset/benchmark for program repair research.

## Output format
Please generate json data satisfying the following TypeScript interface:
```ts

enum Category {
    Survey = 'survey',
    Technical = 'technical',
    Benchmark = 'benchmark',
    Irrelevant = 'irrelevant'
}

interface Article {
    title: string;
    authors: string[];
    year: number;
    category: Category; 
}
``` 
**do not provide extra explanations**, and **do not use ```json and ``` quotes**.
"""
    return BEFORE + item + '\n\n' + AFTER


def process_file(ifile: str, **kwargs) -> None:
    client = OpenAI(
            api_key = os.environ['API_KEY'],
            base_url = os.environ['BASE_URL']
            )

    temperature: float = kwargs['temperature'] if 'temperature' in kwargs else 0.6

    if 'message' in kwargs:
        message = kwargs['message']
    else:
        system_prompt = "You are a helpful assistant."
        if 'system' in kwargs:
            system_prompt = kwargs['system']
        message = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": None}
        ]

    failure_log = open("failed.log", 'w', encoding='utf-8')
    ofile = open("result.jsonl", "a", encoding='utf-8')
    failure_tol = 5
    num_failed = 0
    with open(ifile, 'r', encoding='utf-8') as fobj:
        for item in fobj:
            if len(item) == 0:
                continue
            message[1]['content']  = build_prompt(item.strip())
            success = False
            try:
                completion = client.chat.completions.create(
                    model = os.environ['MODEL'],
                    messages = message,
                    temperature = temperature
                )
                result: str = completion.choices[0].message.content
                del completion

                obj: dict = json.loads(result)
                ofile.write(json.dumps(obj) + '\n')
                ofile.flush()
                success = True
            except Exception as e:
                print(e, file=sys.stderr)
                failure_log.write(item)
                failure_log.flush()
                num_failed += 1
                if num_failed > failure_tol:
                    print("Too many failures, stop processing.", file=sys.stderr)
                    break
            if success:
                num_failed = 0
            time.sleep(1) # avoid hitting rate limit
    ofile.close()
    failure_log.close()


if __name__ == "__main__":
    sane_environ()
    args  = sys.argv    
    if len(args) != 2:
        print("Usage: snowball.py <reference-list>", file=sys.stderr)
        sys.exit(1)
    process_file(args[1])

