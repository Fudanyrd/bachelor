"""
generate-graph.py: automatically generate (tikz) images and tables
    from SLR results.
"""
import json
import os

def make_deps(targets: list[str]):
    with open("images.d", "w") as fobj:
        fobj.write("figures/lang.tex: draw.py pdfs/benchmark/language.json\n")
        fobj.write('main.pdf: images.d ')
        fobj.write(' '.join(targets) + '\n')
    
        for target in targets:
            fobj.write(f"{target}:\n\tpython draw.py\n")


def draw_pie(ofile: str, dat: dict):
    """
    It draws the pie chart in [tikz format](https://latexdraw.com/how-to-plot-a-pie-chart-in-latex/)

    :param: dat: key is a string to show in the chart;
        value is either integer/float meaning the weight,
        or a list of values (use the length as weight)
    """
    def weight(k: str, dat: dict) -> float:
        v = dat[k]
        if isinstance(v, list):
            return len(v)
        assert isinstance(v, (int, float))
        return v

    weights: dict = dict()
    total: float = 0.0
    for k in dat:
        w = weight(k, dat)
        total += w
        weights[k] = w

    for k in dat:
        weights[k] = weights[k] / total * 100
    _example_fig = """
\\begin{tikzpicture}
 
\\pie{22.97/Los Angeles Lakers,
    22.97/Boston Celtics,
    8.11/Golden State Warriors,
    8.11/Chicago Bulls,
    6.76/San Antonio Spurs,
    31.07/Other Teams}
 
\\end{tikzpicture}
"""

    with open(ofile, "w") as fobj:
        fobj.write("\\begin{tikzpicture}\n")
        fobj.write("\\pie[sum=auto, text=legend, radius=2] {\n")
        isfirst = True
        for k in dat:
            if isfirst:
                isfirst=False
            else:
                fobj.write(',\n')
            fobj.write(f"{weights[k]:.2f}/{k.title()}")
        fobj.write("}\n")
        fobj.write("\\end{tikzpicture}\n")


def create_table(keys: list[str], items: list[dict]) -> str:
    """
    Create a latex table with given keys and items.
    It should have only three '\\hlines'.

    Example:
    >>> keys = ['dataset', 'year']
    >>> items = [{"defects4j", 2014}, {"Bears", 2024}]
    >>> print(create_table(keys, items))
    \\begin{tabular}{ll}
    \\hline
    Dataset & Year \\\\ \\hline
    defects4j & 2014 \\\\
    Bears & 2024 \\\\ \\hline
    \\end{tabular}
    """
    if not items:
        raise ValueError("items should not be empty")
    num_keys = len(keys)
    for it in items:
        if len(it) != num_keys:
            raise ValueError("each item should have the same number of keys as the keys list")
    ret = "\\begin{tabular}{"
    for _ in keys:
        ret += "l"
    ret += "}\n\\hline\n"

    for k in keys:
        ret += k.title() + " & "
    ret = ret[:-2] + " \\\\ \\hline\n"

    for i in range(len(items)):
        for k in keys:
            ret += str(items[i][k]) + " & "
        ret = ret[:-2] + " \\\\\n"
    ret += "\\hline\n\\end{tabular}\n"
    return ret


def draw_references_table(ofile: str, dat: dict, keys: tuple[str, str]):
    """
    :param: dat: a dictionary like pdfs/benchmark/language.json
    :param: keys: Descriptions of what the key/value of dat means.
    """
    items = []
    table_header_keys = [keys[0], "Total", keys[1]]

    total = 0
    for k in dat:
        kstr: str = k
        vlist: list = dat[k]
        assert isinstance(vlist, list)

        reference_list:str = '(None)'
        if len(vlist):
            reference_list = '\\citep{' + ', '.join(vlist) + "}"
        total += len(vlist)
        items.append({keys[0]: kstr.title(), 'Total': len(vlist), keys[1]: reference_list})

    items.append({keys[0]: 'All', 'Total': total, keys[1]: ''})
    table_code = create_table(table_header_keys, items)
    with open(ofile, "w") as fobj:
        fobj.write(table_code)
    del table_code


if __name__ == "__main__":
    image_dir = 'figures'
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    deps = ['figures/lang.tex', 
            'figures/lang-tab.tex', 
            'figures/data.tex',
            'figures/data-tab.tex']

    # figures/lang.tex
    src = json.load(open(os.path.join('pdfs', 'benchmark', 'language.json')))
    draw_pie(os.path.join(image_dir, "lang.tex"), src)

    # figures/lang-tab.tex
    draw_references_table(os.path.join(image_dir, "lang-tab.tex"), src, 
                          ("Programming Language", "References"))

    # figures/data.tex, source of datasets
    src = json.load(open(os.path.join('pdfs', 'benchmark', 'source.json')))
    draw_pie(os.path.join(image_dir, "data.tex"), src)

    # figures/data-tab.tex
    draw_references_table(os.path.join(image_dir, "data-tab.tex"), src, 
                          ("Data Source", "References"))

    make_deps(deps)
