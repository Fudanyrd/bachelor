
// returns the first result
var locate_result = function() {
    results = document.querySelector("#gs_res_ccl_mid");
    if (results == null) {
        return null;
    }

    var ret = null;
    var children = results.childNodes;
    var i = 0;
    for (; i < children.length; i++) {
        var item = results.children[i];
        if (item.className != null) {
            ret = item;
            break;
        }
    }
    return ret;
};

// Warn: when many search result exists,
// the extracted abstract may be incomplete;
// e.g. "...to attend to all ..."
var extract_abstract = function(result) {
    var abstract = result.querySelector(".gs_rs");
    if (abstract == null) {
        return null;
    }
    return abstract.innerText;
};

var extract_url = function(result) {
    var url = result.querySelector(".gs_rt a");
    if (url == null) {
        return null;
    }
    return url.href;
};

var export_reference_button = function(result) {
    var button = result.querySelector(".gs_or_cit.gs_nph");
    if (button == null) {
        return null;
    }
    return button;
};


var export_bibtex_button = function(result) {
    // var button = export_reference_button(result);
    // if (button == null) {
    //     return null;
    // }
    // button.click();

    var elem = document.querySelector("#gs_citi");
    

    if (elem == null) {
        // alert("No reference found for the first result.");
        return null;
    }

    var ref_buttons = elem.childNodes;
    for (var i = 0; i < ref_buttons.length; i++) {
        var item = ref_buttons[i];
        if (item.innerText == null) {
            continue;
        }
        if (item.innerText.toLowerCase() == "bibtex") {
            return item;
        }
    }
    return null;
};

var export_bibtex_url = function(result) {
    var bibtex_button = export_bibtex_button(result);
    if (bibtex_button == null) {
        return null;
    }
    return bibtex_button.href;
};
