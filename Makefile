default: main.pdf

TEXSRC = main.tex Makefile related-work.tex intro.tex
BIBSRC = bibtex/*.bib
TEXFLAGS = --halt-on-error

main.bib: $(BIBSRC) Makefile
	@sync
	@cat $(BIBSRC) > main.bib

main.pdf: $(TEXSRC) main.bib
	latexmk -pdflua -halt-on-error main.tex
	bibtex main.aux
	lualatex $(TEXFLAGS) main.tex
	lualatex $(TEXFLAGS) main.tex

.PHONY: clean
clean:
	-rm -f main.aux main.bbl main.blg main.log main.pdf
	-rm -f main.fdb_latexmk main.fls
