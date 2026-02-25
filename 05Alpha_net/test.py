import time
import bisect
import asyncio
from dataclasses import dataclass
from contextlib import contextmanager

# Mutable default argument example
def m_arr(a, blank=[]):
    blank.append(a)
    print(blank) 

# String slicing examples
def r_string():
    s = "abcdefg"
    print(s[1:6:2])
    print(s[::-1][2:5])
    
# List comprehension example
def list_comp_example():
    result = [x*x for x in range(6) if x % 2 == 0]
    print(result)
    
# Dictionary comprehension example
def dict_comp_example():
    result = {x: x*x for x in range(6) if x % 2 == 0}
    print(result)

# Dataclass example   
@dataclass(frozen=True)
class Point:
    x: int
    y: int

# Context manager to time code execution
@contextmanager
def timer():
    """
    Context manager to time a code block.
    @contextmanager ব্যবহার করলে yield সেই জায়গা যেখানে with ব্লকের কোড চলবে।
    yield এর আগে টাইম শুরু করা হয়, আর yield এর পরে finally ব্লকে টাইম শেষ করে print করা হয়।

    অর্থাৎ:
    start = time.perf_counter() → টাইম মাপা শুরু
    yield → তুমি যখন with timer(): লিখে ব্লকের ভিতরে কোড লিখবে, সেটা এখানে execute হবে
    finally: → ব্লক শেষ হলে total elapsed time প্রিন্ট হবে

    """
    start = time.perf_counter()
    try:
        yield start # Control goes to the with block here
    finally:
        print(f"elapsed: {time.perf_counter() - start:.3f} seconds")

# Asynchronous example       
async def work(n):
    await asyncio.sleep(0)
    print(n)
    
async  def main():
    tasks = [work(i) for i in range(1,4)]
    await asyncio.gather(*tasks)

# Bisect module examples   
def arr_sort():
    a = [1, 3, 5, 9]
    print(a)
    bisect.insort(a, 7)
    print(a)

# Binary search examples  
def binary_sort_exam():
    a = [1, 3, 5, 9]
    idx = bisect.bisect_left(a, 5)
    print(idx)
    idx = bisect.bisect_right(a, 5)
    print(idx)

# Enumerate example   
def index_value():
    items = ['apple', 'banana', 'cherry']
    for index, value in enumerate(items):
        print(f"Index: {index}, Value: {value}")

# Function with variable arguments example      
def sumation_example(a, b=10, *args, **kwargs):
    print("Args Length: ", len(args), "Value", args)
    print("Kwargs Length: ", len(kwargs), "Value", kwargs)
    total = a + b + len(args) + len(kwargs)
    print("Total sum is: ", total)


# Main execution
if __name__ == "__main__":
    
    # Mutable default argument demonstration
    m_arr(1)
    m_arr(2) 
    m_arr(3, []) # Providing a new list to avoid shared default mutable argument issue
    
    # String slicing demonstration
    r_string()
    
    # Dataclass and set demonstration
    s = {Point(1, 2), Point(1, 2)}
    print(len(s))
    
    # Timing a code block demonstration
    with timer():
        time.sleep(1)
    
    # Asynchronous execution demonstration    
    asyncio.run(main())
    
    # Bisect module demonstrations  
    arr_sort()
    
    # Binary search demonstration by bisect
    binary_sort_exam()
    
    # Enumerate demonstration
    index_value()
    
    # Function with variable arguments demonstration
    sumation_example(1)
    sumation_example(1, 2, 3, 4, 5, c=5, d=6)
    
    # List and dictionary comprehension demonstrations
    list_comp_example()
    dict_comp_example()