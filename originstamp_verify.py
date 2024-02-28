#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script verifies timestamps created with Originstamp. Currently only Bitcoin
timestamps and pdf proofs are supported.
The program currently uses Blockstream's Bitcoin transaction API, see 
https://github.com/Blockstream/esplora/blob/master/API.md
Please be reasonable with the number of requests you make.


The following steps are undertaken to verify a file:
1) extract transaction and timestamped document hash
2) query bitcoin blockchain and fetch merkle root (OP_RETURN value)
3) check integrity of merkle tree
4) check that document hash is in merkle tree
5) check the merkle root is identical to value stored in blockchain

@author: Tobias E. Naegele, 02/2024

Copyright (c) 2024 Tobias E. Naegele

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

__author__ = "Tobias E. Naegele"
__maintainer__ = __author__
__version__ = "1.0"
__email__ = "github@tobiasnaegele.com"


import requests
import hashlib
import xml.etree.ElementTree as ET
import pdfextract as pdf  # scrapes the xml data from the originstamp pdf
import argparse
import sys

API_URL = 'https://blockstream.info/api/tx/' # hardcode API URL

def init_argparse():
    parser = argparse.ArgumentParser(
        prog='originstamp_verify',
        description='Verifies an Originstamp blockchain timestamp pdf proof. Currently only Bitcoin timestamps are supported and script can only verify pdf proofs.')
    parser.add_argument(
        'file', help='Originstamp proof pdf file to be verified')
    return parser


def print_ok():
    '''
    Prints success message.

    Returns
    -------
    None.

    '''
    print('\033[92m success ✓ \033[0m')


def print_fail():
    '''
    Prints failure message.

    Returns
    -------
    None.

    '''
    print('\033[91m failure ✗\033[0m')

def check_bitcoin(transaction: str, api_url=API_URL):
    '''
    Queries the bitcoin blockchain and return the OP_return value and the number of confirmations of a transaction

    Parameters
    ----------
    transaction : str
        Transaction hash to be checked.
    api_url : str
        URL of the bitcoin blockchain API to be contacted.

    Raises
    ------
    Exception
        Request to blockchain server has failed or transaction not found.

    Returns
    -------
    op_return : str
        OP_RETURN field of blockchain transaction.
    confirmations : int
        Number of blockchain confirmations of transaction.
    timestamp : str
        Timestamp of transaction.

    '''
    response = requests.get(api_url + transaction)
    if response.status_code == 404:
        raise Exception('Transaction not found on Blockchain.')
    elif response.status_code != 200:  # if transaction not found or no connection to api
        raise Exception('Request to Blockchain API has failed.')
    payload = response.json()
    op_return = payload['vout'][0]['scriptpubkey_asm'].split(' ')[2]
    confirmations = payload['status']['block_height']
    timestamp = payload['status']['block_time']

    return op_return, confirmations, timestamp


def verify_tree(tree):
    '''
    Recursive function, iterates through all children of an originstamp hash xml tree
    and checks integrity, will return 0 if tree ok and raise ValueError if compromised
    el needs to be tree root, i.e.
    import xml.etree.ElementTree as ET
    tree = ET.parse('data.xml')
    el = tree.getroot()

    Parameters
    ----------
    tree : str
        Originstamp XML tree.

    Raises
    ------
    ValueError
        Integrity failure - merkle tree not valid.

    Returns
    -------
    int
        Returns 0 if verification successful.

    '''
    ''' '''
    element_hash = tree.attrib['value']  # extract the element hash
    children = list(tree)  # get the children of the element
    if children == []:  # end recursion on this branch if no children exist
        return 0
    # fill dictionary with hashes of children
    child_dict = {}
    for i in children:
        child_dict[i.tag] = i.attrib['value']
        verify_tree(i)   # recursively call the function also for each child

    # concatenate hashes in right order ...
    hash_conc = child_dict['left'] + child_dict['right']
    calculated_hash = hashlib.sha256(
        hash_conc.encode()).hexdigest()  # ... and calculate the hash
    if element_hash != calculated_hash:  # check if the parent hash is identical to the calculated hash
        # if not abort the entire recursion
        raise ValueError('integrity failure - the merkle tree is not valid')
    return 0


def hash_in_tree(tree, hash_value):
    '''
    Checks if hash_value appears anywhere in tree.

    Parameters
    ----------
    tree : str
        Originstamp XML tree.
    hash_value : str
        Hash value to be found in tree.

    Returns
    -------
    int
        0 if successful, 1 if fail.

    '''
    hashes = [i.attrib['value'].strip() for i in list(tree.iter())]
    if hash_value in hashes:
        return 0
    else:
        return 1


def pdf_text_to_xml(text):
    '''
    Parses text extracted from pdf document adn extracts xml data and transaaction details.

    Parameters
    ----------
    text : str
        Raw text extarcted from Originstamp pdf file.

    Returns
    -------
    pdf_xml : str
        XML Merkle tree of transaction.
    pdf_hash : str
        Hash of timestamped document or file.
    pdf_transaction : str
        Bitcoin transaction hash of timestamped Merkle tree.

    '''
    pdf_xml = text.split('reproducibility of your document.\n\n')[
        1].split('\n\n\x0cTimestamp Certiﬁcate')[0]
    pdf_hash = text.split('Hash:\n')[1].split('\nTransaction')[
        0].strip()  # document hash, not root hash!
    pdf_transaction = text.split('Transaction:\n')[
        1].split('\nRoot Hash:\n')[0].strip()

    return pdf_xml, pdf_hash, pdf_transaction


def verify_file(file):
    '''
    Verify Originstamp tiemstamop proof pdf file.

    Parameters
    ----------
    file : str
        Path to pdf file to be verified.
    api_url : str
        URL of Bitcoin blockchain api to be used.

    Returns
    -------
    int
        0 of successful.

    '''
    text = pdf.pdf2text(file)
    pdf_xml, pdf_hash, pdf_transaction = pdf_text_to_xml(text)
    print(f'extracted from pdf: \ndocument hash {
          pdf_hash}\nbitcoin transaction {pdf_transaction}\n\n')

    print('Checking existence of bitcoin blockchain transaction')
    try:
        op_return, confirms, timestamp = check_bitcoin(
            pdf_transaction)
    except BaseException:
        print_fail()
        exit(0)
    print_ok()

    tree = ET.ElementTree(ET.fromstring(pdf_xml))
    root = tree.getroot()

    print('Check if document hash is in the merkle tree: ')
    if hash_in_tree(root, pdf_hash) == 0:
        print_ok()
    else:
        print_fail()
        exit(0)

    print('Check merkle tree integrity: ')
    try:
        ret = verify_tree(root)
        print_ok()
    except BaseException:
        print_fail()
        exit(0)

    print('Check if merkle root identical to op_return value in bitcoin blockchain: ')
    if root.attrib['value'] == op_return:
        print_ok()
    else:
        print_fail()
        exit(0)

    print(f'\n\nDocument hash {
          pdf_hash} has been successfully embedded in the bitcoin blockchain')
    print(f'Number of confirmations: {
          confirms}\nBlockchain timestamp {timestamp}')
    return 0


if __name__ == '__main__':
    parser = init_argparse()
    args = parser.parse_args()
    file = args.file
    try:
        verify_file(file=file)
    except (FileNotFoundError, IsADirectoryError) as err:
        print(f"{sys.argv[0]}: {file}: {err.strerror}", file=sys.stderr)
