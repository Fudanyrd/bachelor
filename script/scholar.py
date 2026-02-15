"""
SYNOPSIS
    scholar.py <snowball_result.jsonl>

DESCRIPTION
    Automate searching on Google scholar, bypassing cloudflare.

    It reads snowballing result, and try to search on Google Scholar
    based on the collected article titles.

BUGS
    It is too slow, taking 30 seconds to export a single bibtex citation.

SEE ALSO
    scholar.js(file)
    snowball.py(1)
"""
import os
import time
import random
import sys
import json
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from seleniumbase import Driver
from bs4 import BeautifulSoup
from urllib.parse import quote

def transform_url(txt: str) -> str:
    return quote(txt)


def _js_lib() -> str:
    with open("scholar.js", "r", encoding="utf-8") as f:
        return f.read()


def make_url(search_string: str) -> str:
    prefix = "https://scholar.google.com/scholar?hl=zh-CN&as_sdt=0%2C5&q="
    url = prefix + transform_url(search_string) + "&oq="
    return url


def _invoke_browser(url: str) -> Driver:
    driver = Driver(uc = True, headless=False)
    driver.uc_open_with_reconnect(url, reconnect_time=10)
    return driver


def export_bibtex(query: str) -> str | None:

    browser = _invoke_browser(make_url(query))
    # browser.execute_script(_js_lib())
    lib:str = _js_lib()

    # returns:
    # null if no result;
    # a string whose first line is the url, rest is abstract.
    # (if no url, first line is '')
    script = lib + \
"""
first_result = locate_result();
if (first_result == null) {
    return null;
}
abstract = extract_abstract(first_result);
if (abstract == null) {
    abstract = '';
}
url = extract_url(first_result);
if (url == null) {
    url = '';
}
return url + '\\n' + abstract;
"""
    abstract_and_url = browser.execute_script(script)
    if abstract_and_url is None:
        browser.quit()
        return None

    lines = abstract_and_url.split("\n", 1)
    url = lines[0]
    abstract = lines[1] if len(lines) > 1 else ''
    del lines

    script = lib + \
"""
first_result = locate_result();
if (first_result == null) {
    return null;
}
button = export_reference_button(first_result);
if (button) {
    button.click();
}

return '';
"""
    result_exist = browser.execute_script(script)
    if result_exist is None:
        browser.quit()
        return None

    time.sleep(7)

    script = lib + \
"""
first_result = locate_result();
return export_bibtex_url(first_result);
"""
    bibtex_url = browser.execute_script(script)
    if bibtex_url is None:
        browser.quit()
        return None
    browser.uc_open_with_reconnect(bibtex_url, reconnect_time=3)

    # extract bibtex inside <pre></pre>
    page_source = browser.page_source
    browser.quit()
    soup = BeautifulSoup(page_source, "html.parser")
    pre = soup.find("pre")
    biblib: BibDatabase | None = None
    if pre is None:
        # try parse as a bibtex file
        biblib = bibtexparser.loads(page_source)
        if len(biblib.entries) == 0:
            return None
        else:
            pass
    else:
        biblib = bibtexparser.loads(pre.text)
    
    # add abstract and url to biblib if not exists.
    if 'abstract' not in biblib.entries[0] and abstract != '':
        biblib.entries[0]['abstract'] = abstract
    if 'url' not in biblib.entries[0] and url != '':
        biblib.entries[0]['url'] = url
    return bibtexparser.dumps(biblib)


def download_bibtex_batch(records: list[dict], ofiles: None | dict):
    """
    Download all references from records.

    :param: records: list of reference items, each contains key 'category', 'title'
    :param: ofiles: open files for each type of reference.
    """
    all_categories = ['technical', 'survey', 'benchmark']

    if ofiles is None:
        ofiles = dict()
    for k in all_categories:
        if k not in ofiles:
            ofiles[k] = k + '.bib'

    ofobjs = dict()
    for k in all_categories:
        ofobjs[k] = open(ofiles[k], 'a', encoding='utf-8')

    failed: list[str] = []
    for record in records:
        if 'category' not in record:
            continue
        if 'title' not in record:
            continue
        category = record['category']
        if category not in all_categories:
            continue
        title = record['title']
        try:
            bibtex = export_bibtex(title)
            if bibtex is not None:
                ofobjs[category].write(bibtex + '\n')
                ofobjs[category].flush()
        except Exception as e:
            print(f"Failed to download: {title}, error: {e}", file=sys.stderr)
            failed.append(title)

    if len(failed) > 0:
        ofobj = ofobjs[all_categories[0]]
        ofobj.write('@comment{\n')
        for title in failed:
            ofobj.write(f"Failed to download: {title}\n")
        ofobj.write('}\n')
        ofobj.flush()

    # clean up ofiles
    for k in all_categories:
        ofobjs[k].close()


def demo():
    # randomly select a title from ../bibtex/bench.bib
    random.seed(int(time.time()) % 97751)
    pth = os.path.join("..", "bibtex", "bench.bib")
    biblib = bibtexparser.load(open(pth, encoding="utf-8"))
    titles = []
    for entry in biblib.entries:
        if 'title' in entry:
            titles.append(entry['title'])

    query = random.choice(titles)
    # query = "Ad-hoc transactions in web applications: the good, the bad, and the ugly"
    print(quote(query), file=sys.stderr)
    del titles
    del biblib

    try:
        start_time = time.time()
        citation = export_bibtex(query)
        end_time = time.time()
        print(f"Time taken: {end_time - start_time:.2f} seconds", file=sys.stderr)
        if citation is None:
            print("No result found.", file=sys.stderr)
        else:
            print(citation)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("Usage: scholar.py <snowball_result.jsonl>", file=sys.stderr)
        exit(1)

    records = []
    with open(args[1], 'r', encoding='utf-8') as fobj:
        for line in fobj:
            if len(line) == 0:
                continue
            records.append(json.loads(line))

    download_bibtex_batch(records, None)
