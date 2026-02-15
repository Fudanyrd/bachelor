// source: https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js

//# sourceMappingURL=FileSaver.min.js.map
var export_references = function () {
    var id = 1;
    var ret = '';

    while (1) {
        var ref = document.querySelector("#ref-" + String(id).padStart(5, '0') + " > div > div.citation-content");
        if (ref == null) {
            break;
        }
        var content = ref.textContent.trim();
        // console.log(content);
        ret += content + "\n";
        id += 1;
    }
    return ret;
};


var convert_to_text = function (child) {
    var ret = '';
    var childNodes = child.childNodes;
    if (childNodes == null || childNodes.length == 0) {
        return child.textContent.replaceAll('\n', ' ').trim();
    }
    for (var i = 0; i < childNodes.length; i++) {
        var node = childNodes[i];
        if (node.className == 'entryAuthor') {
            // separate authors with commas
            var grandChildNodes = node.childNodes;
            if (grandChildNodes == null || grandChildNodes.length == 0) {
                continue;
            }
            ret += grandChildNodes[0].textContent.replaceAll('\n', ' ').trim();
            for (var j = 1; j < grandChildNodes.length; j++) {
                var grandChildNode = grandChildNodes[j];
                ret += ', ';
                ret += grandChildNode.textContent.replaceAll('\n', ' ').trim();
            }
        } else {
            ret += node.textContent.replaceAll('\n', ' ').trim() + ' ';
        }
    }
    return ret.trim();
};


var export_cited_by = function () {
    var elem = document.querySelector("#core-cited-by > div > ul");
    if (elem == null) {
        return '';
    }
    var children = elem.childNodes;

    // concate results, separated by newlines
    var result = '';
    for (var i = 0; i < children.length; i++) {
        var child = children[i];
        var text = convert_to_text(child);
        if (text.length > 0) {
            result += text + '\n';
        }
    }
    return result;
};
