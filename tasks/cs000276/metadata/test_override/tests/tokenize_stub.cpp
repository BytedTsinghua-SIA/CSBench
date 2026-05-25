#include "WhatAreYouDoing.h"
#include <cctype>
using namespace std;

Vector<string> tokenize(const string& sentence) {
    Vector<string> result;
    if (sentence.empty()) {
        return result;
    }

    auto isWordChar = [](char ch) {
        return std::isalpha(static_cast<unsigned char>(ch)) || ch == '\'';
    };

    string current;
    bool inWord = isWordChar(sentence[0]);
    current += sentence[0];

    for (size_t i = 1; i < sentence.size(); i++) {
        char ch = sentence[i];
        bool word = isWordChar(ch);
        if (word == inWord) {
            current += ch;
        } else {
            result += current;
            current.clear();
            current += ch;
            inWord = word;
        }
    }

    if (!current.empty()) {
        result += current;
    }

    return result;
}
