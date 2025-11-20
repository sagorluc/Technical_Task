# 📘 Python Concepts – Deep Explanation

## ✨ Table of Contents
Mutable Default Arguments
String Slicing
List Comprehension
Dictionary Comprehension
Dataclass & Set Behavior
Context Manager (@contextmanager + timer)
Async Programming (async / await)
Bisect Module (insort, bisect_left, bisect_right)
Enumerate
Variable Arguments (*args, **kwargs)

## 🧩 1. Mutable Default Arguments
### ❌ Problem
Python evaluates default arguments only once, so mutable objects (like lists) get reused.

### Example:
```python
def m_arr(a, blank=[]):
    blank.append(a)
    print(blank)

```
### English:
- Calling m_arr(1) stores [1] in the default list.
- Calling m_arr(2) reuses the same list, so output becomes [1, 2].

### বাংলা ব্যাখ্যা:
- Python এ ফাংশন ডিফাইন করার সময় ডিফল্ট ভ্যালু একবারই তৈরি হয়।
- তাই blank=[] আগের মান জমিয়ে রাখে, ফলে পরের কলগুলোতেও সেই একই লিস্ট ব্যবহার হয়।

## 🔠 2. String Slicing

```python
s = "abcdefg"
print(s[1:6:2])     # Output: bdf
print(s[::-1][2:5]) # gfedcb -> edc
```

### English:
- s[1:6:2]: start at index 1 → stop at index 6 → step 2
- s[::-1]: reverse the string
- [2:5] slice of reversed string

### বাংলা:
- s[1:6:2] → ১ থেকে ৬ পর্যন্ত, প্রতি ২ স্টেপে
- s[::-1] → পুরো স্ট্রিং উল্টো করে
- তারপর সেই রিভার্সড স্ট্রিং থেকে [2:5] স্লাইস নেওয়া হয়েছে

## 🧮 3. List Comprehension
```python
result = [x*x for x in range(6) if x % 2 == 0]
print(result)  # [0, 4, 16]
```
### English:
Generates squares of even numbers from 0 to 5.

### বাংলা:
০–৫ পর্যন্ত জোড় সংখ্যার স্কয়ার তৈরি করে।

## 📘 4. Dictionary Comprehension
```python
result = {x: x*x for x in range(6) if x % 2 == 0}
```
### English:
Creates a dictionary: {number: square} for even numbers.

### বাংলা:
প্রতি জোড় সংখ্যাকে key এবং তার square কে value বানিয়ে dictionary তৈরি করে।

## 📦 5. Dataclass & Set Behavior
```python
@dataclass(frozen=True)
class Point:
    x: int
    y: int

s = {Point(1, 2), Point(1, 2)}
print(len(s))  # 1
```
### English:
- frozen=True makes the dataclass immutable + hashable,
- so set considers duplicate objects as the same.

### বাংলা:
- frozen=True করলে অবজেক্ট immutable হয়,
- ফলে hash ঠিক থাকে — তাই set দুটো একই অবজেক্ট মানে → length = 1।

## ⏱️ 6. Context Manager (@contextmanager) – Timer
```python
@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield start
    finally:
        print(f"elapsed: {time.perf_counter() - start:.3f} seconds")
```
### English:
- start stores timestamp
- yield hands control to the with block
- After block completes, total time is printed

### বাংলা:
- start টাইম ধরে রাখে
- yield → এখানে with ব্লকের কোড রান হবে
- ব্লক শেষ হলে elapsed time দেখানো হয়

### Usage:
```python
with timer():
    time.sleep(1)
```
## ⚡ 7. Async / Await
```python
async def work(n):
    await asyncio.sleep(0)
    print(n)
```
### English:
Tasks run concurrently using event loop.

### বাংলা:
Event loop একাধিক টাস্ক একসাথে (concurrent) রান করে।

## 🔍 8. Bisect Module – Binary Search Helpers
### A. Insert in sorted order (insort)

```python
a = [1, 3, 5, 9]
bisect.insort(a, 7)
print(a)  # [1, 3, 5, 7, 9]
```
English:
Maintains sorted list automatically.

বাংলা:
Sorted লিস্টে আইটেম ইনসার্ট করলেও অর্ডার ঠিক থাকে।

###  B. Binary Search
```python
idx = bisect.bisect_left(a, 5)
idx = bisect.bisect_right(a, 5)
```
### English:
- bisect_left → first position where 5 can be inserted
- bisect_right → position after all 5s

### বাংলা:
- bisect_left → ৫ কোথায় বসলে sorted থাকবে (বাম দিক)
- bisect_right → ৫ এর ডানের ইনডেক্স

## 🔢 9. Enumerate
```python
items = ['apple', 'banana', 'cherry']
for index, value in enumerate(items):
    print(index, value)
```
English:
``enumerate()`` returns `(index, value)` pairs.

বাংলা:
`enumerate()` ইনডেক্সসহ মান রিটার্ন করে।

## 🧮 10. Variable Arguments: *args, **kwargs
```python
def sumation_example(a, b=10, *args, **kwargs):
    total = a + b + len(args) + len(kwargs)
```
### English:
- *args → extra positional values
- **kwargs → extra key-value arguments

### বাংলা:
- *args → বাড়তি positional argument
- **kwargs → বাড়তি key-value argument