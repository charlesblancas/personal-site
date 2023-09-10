import { TrieNode } from './trie.mjs';
import { google10kWords } from './google10k.mjs';
import { words } from './words.mjs';

const input = document.getElementById('input');
const result = document.getElementById('result');
const notRecognized = document.getElementById('notRecognized');
const addToDictionary = document.getElementById('addToDictionary');
const wordsButton = document.getElementById('words');
const currentWordlist = document.getElementById('currentWordlist');

let root = new TrieNode('', {});
let currentDictionary = 'google10kWords';

google10kWords.forEach((word) => {
    root.insertWord(word);
});

const switchDictionary = () => {
    let dictionary;

    if (currentDictionary === 'google10kWords') {
        currentDictionary = 'words';
        currentWordlist.innerText = 'Current Wordlist: dwyl 400k';
        wordsButton.innerText = 'Switch to Google 10k';
        dictionary = words;
    } else {
        currentDictionary = 'google10kWords';
        currentWordlist.innerText = 'Current Wordlist: Google 10k';
        wordsButton.innerText = 'Switch to dwyl 400k';
        dictionary = google10kWords;
    }

    console.log('hi');
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

wordsButton.addEventListener('click', () => switchDictionary());

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
