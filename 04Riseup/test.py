my_str = "I love python"
res = my_str.split()

print(res)

def r_str(s):
    add_str = ''
    for char in s:
        add_str = char + add_str
    return add_str

res1 = r_str("Hello world")
print(res1)

data = [32, 335, 78, 10, 12, 14, 2]
for i in data:
    if i == 2:
        print(i)
        
print(i)