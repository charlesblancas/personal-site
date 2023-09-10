import { TrieNode } from './trie.mjs';
import { google10kWords } from './google10k.mjs';
import { words } from './words.mjs';

let root = new TrieNode('', {});

const input = document.getElementById('input');
const result = document.getElementById('result');
const notRecognized = document.getElementById('notRecognized');
const addToDictionary = document.getElementById('addToDictionary');
const google10kButton = document.getElementById('google10kWords');
const wordsButton = document.getElementById('words');

const loadDictionary = (dictionary) => {
    result.innerText = '';
    input.classList.remove('invalid');
    input.classList.remove('valid');
    notRecognized.classList.add('hidden');
    addToDictionary.setAttribute('disabled', '');
    input.value = '';

    root = new TrieNode('', {});

    dictionary.forEach((word) => {
        root.insertWord(word);
    });
};

loadDictionary(google10kWords);

google10kButton.addEventListener('click', () => loadDictionary(google10kWords));
wordsButton.addEventListener('click', () => loadDictionary(words));

const validWord = () => {
    input.classList.add('valid');
    input.classList.remove('invalid');
    addToDictionary.setAttribute('disabled', '');
};

const invalidWord = () => {
    input.classList.add('invalid');
    input.classList.remove('valid');
    addToDictionary.removeAttribute('disabled');
};

const inputHandler = (e) => {
    const word = e.target.value;

    if (word === '') {
        result.innerText = '';
        input.classList.remove('invalid');
        input.classList.remove('valid');
        notRecognized.classList.add('hidden');
        addToDictionary.setAttribute('disabled', '');
        return;
    }

    const node = root.findNode(word);

    if (!node) {
        result.innerText = 'No words found';
        invalidWord();
        return;
    }

    let outputs = '';
    let queue = [node];
    let outputCount = 0;

    while (queue.length && outputCount < 10) {
        let currNode = queue.shift();
        if (currNode.isWord) {
            outputs += currNode.word + '\n';
            outputCount += 1;
        }

        for (let key in currNode.children) {
            queue.push(currNode.children[key]);
        }
    }

    result.innerText = outputs || 'No words found';

    notRecognized.classList.remove('hidden');
    node.isWord ? validWord() : invalidWord();
};

input.addEventListener('input', inputHandler);
input.addEventListener('propertychange', inputHandler);

const addToDictionaryHandler = (e) => {
    let word = input.value;
    root.insertWord(word);
    validWord();
    inputHandler({ target: { value: word } });
};

addToDictionary.addEventListener('click', addToDictionaryHandler);
