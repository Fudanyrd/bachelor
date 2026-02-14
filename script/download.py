import requests
import subprocess
import os
import time
import sys
from seleniumbase import Driver
import bibtexparser

# FIXME: not usage; Segmentation Fault
# import magic

def format_is_pdf(file: str) -> bool:
    if not os.path.exists(file):
        raise FileNotFoundError(f"File '{file}' does not exist.")
    res = subprocess.run(['file', '--mime-type', file], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to run 'file' command: {res.stderr}")
    ret ='application/pdf' in res.stdout.lower()
    del res
    return ret


def download_others(url: str, ofile: str):
    """
    Assume url points to a pdf file, and can access being blocked.
    """
    res = requests.get(url)
    with open(ofile, 'wb') as fobj:
        fobj.write(res.content)
    if not format_is_pdf(ofile):
        raise ValueError(f"Downloaded file '{ofile}' is not a PDF.")


def download_arxiv(url: str, ofile: str):
    """
    Download a paper from arXiv given its URL and save it to the specified output file.
    """
    url = url.replace('abs', 'pdf')
    download_others(url, ofile)


def download_acm_dl(url: str, ofile: str):
    """
    Download a paper from ACM Digital Library given its URL and save it to the specified output file.
    """
    driver = Driver(uc=True, headless=False)
    driver.uc_open_with_reconnect(url, reconnect_time=10)

    cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    headers = {
        "User-Agent": driver.execute_script("return navigator.userAgent;")
    }

    response = session.get(url, headers=headers)
    status_code = response.status_code

    if status_code != 200:
        driver.quit()
        raise ValueError(f"Failed to download paper from {url}. HTTP status code: {status_code}")

    with open(ofile, "wb") as f:
        f.write(response.content)

    driver.quit()
    if not format_is_pdf(ofile):
        raise ValueError(f"Downloaded file '{ofile}' is not a PDF.")


def download_doi_org(url: str, ofile: str):
    """
    Download a paper from DOI.org given its URL and save it to the specified output file.
    """
    success = False
    try:
        download_others(url, ofile)
        success = True
    except Exception as e:
        success = False
    # translate the url:
    # https://doi.org/10.1145/3395363.3397369
    # -> https://dl.acm.org/doi/pdf/10.1145/3395363.3397369
    if success:
        return
    toks = url.split('/')
    if len(toks) < 2:
        raise ValueError(f"Invalid DOI URL: {url}")
    doi = toks[-2] + '/' + toks[-1]
    acm_url = f"https://dl.acm.org/doi/pdf/{doi}"
    download_acm_dl(acm_url, ofile)


DEFAULT_DOWNLOADER = {
    "dl.acm.org": download_acm_dl,
    "arxiv.org": download_arxiv,
    "doi.org": download_doi_org,
}


def domain_name(url: str) -> str:
    try:
        idx = url.index('://')
        url = url[idx+3:]
    except ValueError:
        pass
    try:
        idx = url.index('/')
        url = url[:idx]
    except ValueError:
        pass
    return url


def download_paper(url: str, ofile: str):
    domain = domain_name(url)
    downloader = DEFAULT_DOWNLOADER.get(domain, download_others)

    try:
        downloader(url, ofile)
    except Exception as e:
        print(f"Error downloading paper from {url}: {e}", file=sys.stderr)
        # manually download the paper.
        if os.path.exists(ofile):
            os.unlink(ofile)


def download_from_bib(bibfile: str, savedir: str | None) -> str:
    """
    Parse the bib file, and download the pdf file to {savedir}/{id}.pdf
    """
    lib = bibtexparser.load(open(bibfile, encoding='utf-8'))
    for entry in lib.entries:
        if 'url' not in entry:
            print(f"Entry '{entry.get('ID', 'unknown')}' does not have a URL. Skipping.", file=sys.stderr)
            continue
        if 'ID' not in entry:
            print(f"Entry with URL '{entry['url']}' does not have an ID. Using 'unknown' as filename.", file=sys.stderr)
        url = entry['url']
        obasename = f"{entry.get('ID', 'unknown')}.pdf"
        ofile = os.path.join(savedir, obasename) if savedir else obasename
        if not os.path.exists(ofile):
            download_paper(url, ofile)
            time.sleep(10)  # avoid being blocked by the server


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        print("Usage: download.py <bibsource> <save dir>")
        sys.exit(1)

    download_from_bib(args[1], args[2])
