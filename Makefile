default: main.pdf

TEXSRC = main.tex

main.bib: bibtex
	@cat bibtex/*.bib > main.bib

main.pdf: $(TEXSRC) main.bib
	latexmk -pdflua -halt-on-error main.tex
	bibtex main.aux
	lualatex main.tex
	lualatex main.tex

.PHONY: clean
clean:
	rm -f main.aux main.bbl main.blg main.log main.pdf
