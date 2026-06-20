from tests.util import *
print(parser(
"""
let animals: list[Animal] Onwer[Read] = make();
for animal in animals {
    animal.speak();
}
"""
))