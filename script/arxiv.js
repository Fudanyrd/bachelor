var export_reference = function (id) {
    let node = document.querySelector("#bib\\.bib" + String(id));
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

    return ret.replaceAll("\n", " ").replace("↑", ";").trim();
};