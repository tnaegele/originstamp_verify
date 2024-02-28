#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part of originstamp_verify script.
copied from https://pdfminersix.readthedocs.io/en/latest/tutorial/composable.html
"""

from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


def pdf2text(file_path):
    '''
    Extracts raw text from pdf file. Copied from https://pdfminersix.readthedocs.io/en/latest/tutorial/composable.html

    Parameters
    ----------
    file_path : str
        Filepath of pdf to be parsed

    Returns
    -------
    str
        Raw pdf text.

    '''
    output_string = StringIO()
    with open(file_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    return output_string.getvalue()
