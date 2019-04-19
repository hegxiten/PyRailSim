class Student():
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __lt__(self, other):
        if self.age < other.age:
            return True
        else:
            return False

s = [Student("tjh", 9), Student("wzz", 10), Student("gk", 11)]
s.sort(reverse=True)

for ss in s:
    print(ss.name)
