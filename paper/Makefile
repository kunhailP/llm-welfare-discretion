# Paper 1 build. Needs latexmk + TeX Live (texlive-latex-extra, texlive-bibtex-extra).
#   make           -> main.pdf (review mode, anonymous)
#   make pages     -> page count of the content before Limitations (short paper: 4 pages max)
#   make clean
.PHONY: all pages clean
all: main.pdf
main.pdf: main.tex references.bib added.bib acl.sty acl_natbib.bst
	latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
pages: main.pdf
	@pdfinfo main.pdf | grep Pages
	@echo "Limitations starts on page:" $$(pdftotext -layout main.pdf - | awk 'BEGIN{p=1} /\f/{p++} /^ *Limitations *$$/{print p; exit}')
clean:
	latexmk -C main.tex; rm -f main.bbl main.run.xml
