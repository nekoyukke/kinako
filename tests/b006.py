from tests.util import *

parser(
"""
fn add(a:int read, b:int read) -> int {
    let result: int onwer = 0;
    for i in - {
        result = result + i;
    }
    return a+b;
}
""", True
)
r"""
なんか踏んだ
ただ単に[]が定義できてなかったっぽい。
ただ、この量のエラーはきついのでパスできるようにしたいところ

Python:
Traceback (most recent call last):
  File "<frozen runpy>", line 189, in _run_module_as_main
  File "<frozen runpy>", line 159, in _get_module_details
  File "<frozen importlib._bootstrap_external>", line 893, in get_code
  File "<frozen importlib._bootstrap_external>", line 823, in source_to_code
  File "<frozen importlib._bootstrap>", line 491, in _call_with_frames_removed
  File "D:\program\kinako\tests\b006.py", line 14
    for i in -:
              ^
SyntaxError: invalid syntax

見た感じ、forでおかしくなる->fnがおかしくなる->その周りの{}が死ぬ

me:
Traceback (most recent call last):
  File "D:\program\kinako\src\frontend\parser\parser.py", line 118, in _Stmt_entry
  File "D:\program\kinako\src\frontend\parser\parser.py", line 139, in _Stmt
  File "D:\program\kinako\src\frontend\parser\parser.py", line 276, in block_node
  File "D:\program\kinako\src\frontend\parser\parser.py", line 131, in _Stmt
  File "D:\program\kinako\src\frontend\parser\parser.py", line 214, in for_node
  File "D:\program\kinako\src\frontend\parser\parser.py", line 393, in _expr_entry
  File "D:\program\kinako\src\frontend\parser\parser.py", line 396, in assignment
  File "D:\program\kinako\src\frontend\parser\parser.py", line 331, in right_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 404, in logical_or
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 411, in logical_and
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 414, in equality
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 417, in comparison
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 425, in term
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 428, in factor
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 434, in prefix
  File "D:\program\kinako\src\frontend\parser\parser.py", line 440, in prefix
  File "D:\program\kinako\src\frontend\parser\parser.py", line 444, in postfix
  File "D:\program\kinako\src\frontend\parser\parser.py", line 490, in primary
  File "D:\program\kinako\src\frontend\parser\parser.py", line 83, in CallError


Traceback (most recent call last):
  File "<source>", line 4
 2 fn add(a:int read, b:int read) -> int {
 3     let result: int onwer = 0;
>4     for i in - {
 5         result = result + i;
 6     }

KinakoSyntaxError: 不明なトークン{。
Traceback (most recent call last):
  File "D:\program\kinako\src\frontend\parser\parser.py", line 118, in _Stmt_entry
  File "D:\program\kinako\src\frontend\parser\parser.py", line 129, in _Stmt
  File "D:\program\kinako\src\frontend\parser\parser.py", line 258, in fndefine_node
  File "D:\program\kinako\src\frontend\parser\parser.py", line 83, in CallError


Traceback (most recent call last):
  File "<source>", line 2
 1 
>2 fn add(a:int read, b:int read) -> int {
 3     let result: int onwer = 0;
 4     for i in - {

KinakoSyntaxError: Body不明
Traceback (most recent call last):
  File "D:\program\kinako\src\frontend\parser\parser.py", line 118, in _Stmt_entry
  File "D:\program\kinako\src\frontend\parser\parser.py", line 141, in _Stmt
  File "D:\program\kinako\src\frontend\parser\parser.py", line 393, in _expr_entry
  File "D:\program\kinako\src\frontend\parser\parser.py", line 396, in assignment
  File "D:\program\kinako\src\frontend\parser\parser.py", line 331, in right_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 404, in logical_or
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 411, in logical_and
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 414, in equality
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 417, in comparison
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 425, in term
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 428, in factor
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 440, in prefix
  File "D:\program\kinako\src\frontend\parser\parser.py", line 444, in postfix
  File "D:\program\kinako\src\frontend\parser\parser.py", line 490, in primary
  File "D:\program\kinako\src\frontend\parser\parser.py", line 83, in CallError


Traceback (most recent call last):
  File "<source>", line 8
 6     }
 7     return a+b;
>8 }

KinakoSyntaxError: 不明なトークン}。
"""

r"""
これは解決
Traceback (most recent call last):
  File "D:\program\kinako\src\frontend\parser\parser.py", line 118, in _Stmt_entry
  File "D:\program\kinako\src\frontend\parser\parser.py", line 139, in _Stmt
  File "D:\program\kinako\src\frontend\parser\parser.py", line 276, in block_node
  File "D:\program\kinako\src\frontend\parser\parser.py", line 131, in _Stmt
  File "D:\program\kinako\src\frontend\parser\parser.py", line 214, in for_node
  File "D:\program\kinako\src\frontend\parser\parser.py", line 393, in _expr_entry
  File "D:\program\kinako\src\frontend\parser\parser.py", line 396, in assignment
  File "D:\program\kinako\src\frontend\parser\parser.py", line 331, in right_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 404, in logical_or
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 411, in logical_and
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 414, in equality
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 417, in comparison
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 425, in term
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 428, in factor
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 440, in prefix
  File "D:\program\kinako\src\frontend\parser\parser.py", line 444, in postfix
  File "D:\program\kinako\src\frontend\parser\parser.py", line 490, in primary
  File "D:\program\kinako\src\frontend\parser\parser.py", line 83, in CallError


Traceback (most recent call last):
  File "<source>", line 4
 2 fn add(a:int read, b:int read) -> int {
 3     let result: int onwer = 0;
>4     for i in [a,b] {
 5         result = result + i;
 6     }

KinakoSyntaxError: 不明なトークン[。
Traceback (most recent call last):
  File "D:\program\kinako\src\frontend\parser\parser.py", line 118, in _Stmt_entry
  File "D:\program\kinako\src\frontend\parser\parser.py", line 129, in _Stmt
  File "D:\program\kinako\src\frontend\parser\parser.py", line 258, in fndefine_node
  File "D:\program\kinako\src\frontend\parser\parser.py", line 83, in CallError


Traceback (most recent call last):
  File "<source>", line 2
 1 
>2 fn add(a:int read, b:int read) -> int {
 3     let result: int onwer = 0;
 4     for i in [a,b] {

KinakoSyntaxError: Body不明
Traceback (most recent call last):
  File "D:\program\kinako\src\frontend\parser\parser.py", line 118, in _Stmt_entry
  File "D:\program\kinako\src\frontend\parser\parser.py", line 141, in _Stmt
  File "D:\program\kinako\src\frontend\parser\parser.py", line 393, in _expr_entry
  File "D:\program\kinako\src\frontend\parser\parser.py", line 396, in assignment
  File "D:\program\kinako\src\frontend\parser\parser.py", line 331, in right_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 404, in logical_or
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 411, in logical_and
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 414, in equality
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 417, in comparison
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 425, in term
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 428, in factor
  File "D:\program\kinako\src\frontend\parser\parser.py", line 315, in left_binary_op
  File "D:\program\kinako\src\frontend\parser\parser.py", line 440, in prefix
  File "D:\program\kinako\src\frontend\parser\parser.py", line 444, in postfix
  File "D:\program\kinako\src\frontend\parser\parser.py", line 490, in primary
  File "D:\program\kinako\src\frontend\parser\parser.py", line 83, in CallError


Traceback (most recent call last):
  File "<source>", line 8
 6     }
 7     return a+b;
>8 }

KinakoSyntaxError: 不明なトークン}。
"""