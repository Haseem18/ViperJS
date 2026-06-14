// Write your own JS code

console.log("=== VIPER JS DEMO ===");

// Variables
let firstName = "Haseem";
const age = 20;

console.log(`Name: ${firstName}`);
console.log(`Age: ${age}`);

// Functions
function add(a, b) {
    return a + b;
}

console.log("Addition:", add(10, 20));

// Closures
function makeCounter() {
    let count = 0;

    return function () {
        count++;
        return count;
    };
}

const counter = makeCounter();

console.log("Counter:", counter());
console.log("Counter:", counter());
console.log("Counter:", counter());

// Arrays
const numbers = [1, 2, 3, 4, 5];

console.log(
    "Even Numbers:",
    numbers.filter(num => num % 2 === 0)
);

console.log(
    "Squares:",
    numbers.map(num => num * num)
);

console.log(
    "Sum:",
    numbers.reduce((acc, curr) => acc + curr, 0)
);

// Objects
const person = {
    name: "Haseem",
    city: "Ratnagiri"
};

console.log("Person:", person);

// for...of
console.log("for...of:");

for (let value of numbers) {
    console.log(value);
}

// for...in
console.log("for...in:");

for (let index in numbers) {
    console.log(index);
}

// Recursion
function factorial(n) {
    if (n === 0) {
        return 1;
    }

    return n * factorial(n - 1);
}

console.log("Factorial:", factorial(5));

// Promise
Promise.resolve("Promise Resolved")
    .then(value => {
        console.log(value);
    });

// Async / Await
async function demo() {
    console.log("Async Start");

    await Promise.resolve();

    console.log("Async End");
}

demo();

console.log("Program Finished");
