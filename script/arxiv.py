import os
import sys
import bibtexparser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

class ArXiv():
    @staticmethod
    def _get_reference(browser: webdriver, id: int) -> str | None:
        jsscript = """
    let node = document.querySelector("#bib\\\\.bib" + arguments[0]);
    if (node == null) {
        return null;
    }
    let children = node.childNodes;
    let ret = '';
    for (let i = 0; i < children.length; i++) {
        let child = children[i];
        if (i == 0) {
            continue;
        } else {
            ret += ' ';
        }
        ret += child.textContent;
    }

    return ret.replaceAll("\\n", " ").replace("↑", ";").trim();
"""
        result  = browser.execute_script(jsscript, str(id))
        return result

    @staticmethod
    def get_references(browser: webdriver) -> list[str]:
        id = 1
        ret = []
        while True:
            ref = ArXiv._get_reference(browser, id)
            if ref is None:
                break
            if ref != '':
                ret.append(ref)
            id += 1
        return ret

if __name__ == "__main__":
    myoptions = Options()
    myoptions.add_argument("-headless") # Enable headless mode

    bibfile = os.path.join("..", "dataset", "arxiv.bib")
    lib = bibtexparser.load(open(bibfile, 'r'));
    logfile = open("arxiv.log", 'w')
    reffile = open("arxiv.txt", 'w')

    for entry in lib.entries:
        if 'eprint' not in entry:
            continue
        article_id  = entry['eprint']
        print(article_id, file=sys.stderr)
        url = 'https://arxiv.org/html/' + article_id
        browser = webdriver.Firefox(options=myoptions)
        references = []
        try:
            browser.get(url)
            references = ArXiv.get_references(browser)
        except:
            logfile.write(f"Error: {article_id}\n")
        browser.quit()

        for ref in references:
            reffile.write(ref + "\n")
        if len(references) == 0:
            logfile.write(f"No reference: {article_id}\n")

        reffile.flush()
        time.sleep(1)
        del references
        del browser

    logfile.close()
    reffile.close()
