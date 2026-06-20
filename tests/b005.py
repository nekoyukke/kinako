from tests.util import *
parser(
"""
fn add(a, b) {
    return a+b;
}
"""
)
parser(
"""
fn add(a:int, b) {
    return a+b;
}
"""
)
parser(
"""
fn add(a, b:int) {
    return a+b;
}
"""
)
parser(
"""
fn add(a, b) -> int {
    return a+b;
}
"""
)
parser(
"""
fn add(a:int read, b:int read) -> int {
    return a+b;
}
"""
)
parser(
"""
fn add(a:int read, b:int read) -> int {
    let result: int onwer = 0;
    for i in lol {
        result = result + i;
    }
    return a+b;
}
"""
)