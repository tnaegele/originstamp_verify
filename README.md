# originstamp_verify
A script which verifies blockchain timestamps created with [Originstamp](https://originstamp.com/). Currently only Bitcoin timestamps are supported and the program can only parse pdf proofs. 

## Usage
Just clone this repo, create a virtualenv which fulfils the requirements from requirements.txt and run
~~~bash
python originstamp_verify <filename>
~~~
where <filename> points to an Originstamp Bitcoin pdf proof.

Example output
~~~
extracted from pdf:
document hash 3d8d0baaa101e63ce25de59b9c8153b4d4368004a9e6e251e6366e247179399f
bitcoin transaction b5582ae6b5a96c645f78c8e10a3b46527b1900097eda6f57c003a2187a230408


Checking existence of bitcoin blockchain transaction
 success ✓
Check if document hash is in the merkle tree:
 success ✓
Check merkle tree integrity:
 success ✓
Check if merkle root identical to op_return value in bitcoin blockchain:
 success ✓


Document hash 3d8d0baaa101e63ce25de59b9c8153b4d4368004a9e6e251e6366e247179399f has been successfully embedded in the bitcoin blockchain
Number of confirmations: 694521
Blockchain timestamp 1628278522
~~~


## Bitcoin API
The script uses uses Blocktree's Bitcoin transaction API, see https://github.com/Blockstream/esplora/blob/master/API.md. 
Please be reasonable with the number of requests you make.

## Verification process
The following steps are undertaken in the verification process:
1) extract transaction and timestamped document hash
2) query bitcoin blockchain and fetch merkle root (OP_RETURN value)
3) check integrity of merkle tree
4) check that document hash is in merkle tree
5) check the merkle root is identical to value stored in blockchain


## License
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
