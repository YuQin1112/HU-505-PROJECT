import pandas
import sys
import time
from math import radians, cos, sin, asin, sqrt
from dateutil import parser
import pytz
from datetime import datetime, time
import os
from heapq import *
import re

from Trie import Trie

class preprocess:
    def __init__(self):
        self.trie = Trie()
        self.spam_count = 0
        self.normal_count = 0
        self.dump_csv = []


    def is_ascii(self, s):
        return all(ord(c) < 128 for c in s)


    def remove_non_ascii(self, s):
        return re.sub(r'[^\x00-\x7f]',r' ',s)


    def get_trie(self):
        data = pandas.read_csv("spam_or_not_spam.csv")
        for index, row in data.dropna().iterrows():
            # if index > 2600:
            #     continue
            is_spam = int(row["label"])

            seen = set()
            email = self.remove_non_ascii(row["email"])
            for word in email.split():
                if word in seen:
                    continue

                seen.add(word)
                word = ''.join(filter(str.isalnum, word))
                if word.isdigit():
                    continue
                self.trie.insert(word, is_spam)

            if is_spam == 1:
                self.spam_count += 1
            else:
                self.normal_count += 1


    def dfs(self, word = "", node = None):
        if not node:
            node = self.trie.root

        if node.is_word:
            self.dump_csv.append({"word": word, "spam": node.spam_count, "normal": node.normal_count})

        for c in node.children:
            self.dfs(word + c, node.children[c])


    def process(self):
        self.get_trie()
        self.dfs()

        new_df = pandas.DataFrame(self.dump_csv,
            columns=['word', 'spam', 'normal']
        )

        print("test: ", self.trie.search("interred").normal_count)

        with open("cleaned.csv", "w") as f:
            new_df.to_csv(f, header=True, mode='w', line_terminator="\n")


class spam_detection:
    """
    prior:
    P(spam) = P(S) = 16%
    P(normal) = P(N) = 84%

    Given by or dataset with 1/6 spam and 5/6 normal
    """

    def __init__(self, word_info, spam, normal):
        self.word_info = word_info
        self.spam_count = spam
        self.normal_count = normal
        self.P_S = 0.16
        self.P_N = 0.84

        print(self.spam_count, self.normal_count)


    def P_S_W(self, word):
        """
        Calc P(S|W): given a word W, the possibility of email is spam

        P(S|W) = P(W|S)P(S) / P(W|S)P(S) + P(W|N)P(N)
        """
        if not self.word_info.search(word):
            return 0.1

        P_W_S = self.word_info.search(word).spam_count / self.spam_count
        P_W_N = self.word_info.search(word).normal_count / self.normal_count

        #print(word, self.word_info[word])

        P_S_W = (P_W_S * self.P_S) / (P_W_S * self.P_S + P_W_N * self.P_N)

        return P_S_W * 0.9


    def first_15_P(self, context):
        """
        according to Paul Graham, we only care about 15 largest P(S|W)
        """
        heap = []

        seen = set()

        for word in context.split():
            if word in seen:
                continue
            seen.add(word)
            word = ''.join(filter(str.isalnum, word))

            P = self.P_S_W(word)
            if P == 0 or P == 1:
                continue
            if len(heap) < 15:
                heappush(heap, (P, word))
            else:
                if P > heap[0][0]:
                    heappop(heap)
                    heappush(heap, (P, word))
        return heap


    def combined_P(self, first_15_P):
        """
        P = P(~S)P1*P2*...*P15 / (P(~S)P1*P2*...*P15 + P(S)(1-P1)*(1-P2)*...*(1-P15))
        """
        mult = 1
        compliment_mult = 1

        for p, w in first_15_P:
            mult *= p
            compliment_mult *= (1-p)

        P = self.P_N * mult / (self.P_N * mult + self.P_S * compliment_mult)
        return P


    def detect(self, context):
        score = self.combined_P(self.first_15_P(context))
        return score


def visualization(detective):
    rtn = []
    data = pandas.read_csv("spam_or_not_spam.csv")
    for index, row in data.dropna().iterrows():
        if index < 2000:
            continue

        score = detective.detect(row["email"])
        rtn.append({"p": score, "is_spam":row["label"]})

    new_df = pandas.DataFrame(rtn,
        columns=['p', 'is_spam']
    )

    with open("result.csv", "w") as f:
        new_df.to_csv(f, header=True, mode='w', line_terminator="\n")



if __name__ == "__main__":
    pre = preprocess()
    pre.process()

    detect = spam_detection(pre.trie, pre.spam_count, pre.normal_count)

    visualization(detect)
