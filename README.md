# Viper JS – JavaScript Runtime Built in Python

A JavaScript interpreter/runtime built entirely in **Python** for **Thunder Hackathon 2.0**.

Viper JS accepts JavaScript code from a `.js` file, parses it, executes it, and prints the output to the terminal without relying on **Node.js**, **V8**, or any external JavaScript engine.

---

## Features

### Variables

* `let`
* `const`
* `var`

### Data Types

* Number
* String
* Boolean
* Null
* Undefined
* Arrays
* Objects
* Functions

### Operators

* Arithmetic operators (`+`, `-`, `*`, `/`, `%`, `**`)
* Comparison operators (`==`, `===`, `!=`, `!==`, `<`, `>`, `<=`, `>=`)
* Logical operators (`&&`, `||`, `!`)
* Assignment operators (`=`, `+=`, `-=`, `*=`, `/=`, `%=`, `**=`)

### Control Flow

* `if`
* `else if`
* `else`
* `switch`
* `for`
* `while`
* `do...while`
* `for...of`
* `for...in`

### Functions

* Function declarations
* Function expressions
* Arrow functions
* Closures
* Recursion
* Callback functions
* Function hoisting

### Arrays

* `push()`
* `pop()`
* `shift()`
* `unshift()`
* `slice()`
* `splice()`
* `concat()`
* `includes()`
* `indexOf()`
* `sort()`
* `reverse()`
* `map()`
* `filter()`
* `reduce()`
* `find()`
* `some()`
* `every()`

### Strings

* `replace()`
* `replaceAll()`
* `substring()`
* `slice()`
* `split()`
* `trim()`
* `toUpperCase()`
* `toLowerCase()`
* `includes()`
* `startsWith()`
* `endsWith()`
* `indexOf()`

### Objects

* Object literals
* Dot notation access
* Bracket notation access
* Nested objects
* Object methods
* Human-readable object printing in `console.log`

### Built-in Objects

* `Math`
* `Date`
* `Promise`
* `JSON`
* `console`

### Asynchronous Features

* `Promise.resolve()`
* Promise chaining using `.then()`
* `async` functions
* `await`
* `setTimeout()`
* `setInterval()`
* Microtask queue support
* Event loop implementation

### JavaScript Behaviors

* Type coercion
* Truthy/falsy evaluation
* Correct `Boolean(undefined)` behavior
* Strict equality (`===`)
* Loose equality (`==`)
* `typeof`
* Spread operator (`...`)
* Rest parameters
* Template literals
* Ternary operator

---

## JavaScript Error Handling

Viper JS provides JavaScript-style runtime and syntax errors for common failure scenarios.

Supported errors include:

* `ReferenceError`
* `TypeError`
* `SyntaxError`

Examples:

### ReferenceError

```javascript
console.log(firstName);
```

Output:

```text
ReferenceError: firstName is not defined
```

---

### Assignment to Constant Variable

```javascript
const PI = 3.14;
PI = 10;
```

Output:

```text
TypeError: Assignment to constant variable.
```

---

### Calling Non-Functions

```javascript
let age = 20;
age();
```

Output:

```text
TypeError: age is not a function
```

---

### Duplicate Declarations

```javascript
let name = "A";
let name = "B";
```

Output:

```text
SyntaxError: Identifier 'name' has already been declared
```

---

### Invalid Variable Names

```javascript
const 1 = "Haseem";
```

Output:

```text
SyntaxError: Unexpected token '1'
```

---

## Iteration Support

### `for...of`

Iterates over values.

```javascript
for (let value of [10, 20, 30]) {
    console.log(value);
}
```

Output:

```text
10
20
30
```

---

### `for...in`

Iterates over enumerable keys.

```javascript
for (let index in [10, 20, 30]) {
    console.log(index);
}
```

Output:

```text
0
1
2
```

---

## Architecture

```text
JavaScript Source Code
          ↓
        Lexer
          ↓
        Parser
          ↓
   Abstract Syntax Tree (AST)
          ↓
      Interpreter
          ↓
 Environment / Scope Chain
          ↓
 Event Loop & Microtasks
          ↓
         Output
```

---

## Requirements

* Python 3.x
* No external libraries required

---

## How to Run

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

---

### 2. Create a JavaScript File

Example: `main.js`

```javascript
console.log("Hello, World!");
```

---

### 3. Run the Interpreter

```bash
python viper.py main.js
```

---

## Example

### Input (`main.js`)

```javascript
function greet(name) {
    console.log("Hello, " + name);
}

greet("World");
```

### Output

```text
Hello, World
```

---

## Official Hackathon Test Cases

The interpreter successfully executes the required Thunder Hackathon examples, including:

* Odd/Even Checker
* Triangle Pattern
* Armstrong Number
* Array Reverse
* String Palindrome Check

---

## Additional Testing

The runtime has also been tested with:

* Closures
* Recursion
* Arrow functions
* Template literals
* Spread operator
* Higher-order array methods
* Promise microtasks
* Promise chaining
* Async/Await workflows
* Event loop scheduling
* Reference errors
* Type errors
* Syntax errors
* Object printing
* `for...in` behavior
* `for...of` behavior

---

## Project Structure

```text
project/
│
├── viper.py
├── README.md
└── examples/
    ├── odd_even.js
    ├── armstrong.js
    ├── palindrome.js
    ├── promises.js
    ├── async_await.js
    └── closures.js
```

---

## Limitations

Viper JS is an educational JavaScript runtime created for a hackathon challenge. It aims to support a substantial subset of JavaScript features but is **not intended to be a full replacement for production JavaScript engines such as V8**.

Features not currently implemented include:

* ES Modules (`import` / `export`)
* `Map` and `Set`
* `WeakMap` and `WeakSet`
* `Proxy`
* `Reflect`
* `Symbol`
* Generator functions (`yield`)
* Full DOM APIs
* Complete V8-compatible error messages

---

## License

This project was developed as part of **Thunder Hackathon 2.0 – Build Your Own JavaScript**.

The runtime is implemented entirely in Python using only the Python standard library.
