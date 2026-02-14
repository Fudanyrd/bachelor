"""
generate-graph.py: automatically generate (tikz) images and tables
    from SLR results.
"""
import json
import os

def make_deps(targets: list[str]):
    with open("images.d", "w") as fobj:
        fobj.write("figures/lang.tex: draw.py pdfs/benchmark/language.json\n")
        fobj.write('main.pdf: figures/lang.tex images.d\n')
    
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


if __name__ == "__main__":
    image_dir = 'figures'
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    make_deps(['figures/lang.tex'])

    # figures/lang.tex
    src = json.load(open(os.path.join('pdfs', 'benchmark', 'language.json')))
    draw_pie(os.path.join(image_dir, "lang.tex"), src)

