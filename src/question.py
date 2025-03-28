from pydantic import BaseModel, Field, validator

class Word(BaseModel):
    no : int = Field(description='No.')
    word : str = Field(description='単語')
    klass : str = Field(description='品詞')
    meaning : str = Field(description='意味')
    example : str = Field(description='例文')
    japanese : str = Field(description='和訳')

class Question(BaseModel):
    """英単語問題のデータ"""
    question: str = Field(description="解凍すべき単語が `(    )` で伏せられています。")
    answer: str = Field(description="`(    )` を埋めるべき単語です。")
    wrong: list[str] = Field(description="これを選ぶと不正解になる単語 9 つのカンマで区切られたリスト。answer と似た意味の単号は出現してはいけません。")

class Questions(BaseModel):
    """英単語問題集"""
    questions : list[Question] = Field(description='問題集')
    
class WordQuestion(BaseModel):
    word : Word = Field(description='単語情報')
    question : Question = Field(description='問題')

def load_questions() -> list[WordQuestion]:
    wqs = []
    with open('data/questions400fix.json', 'r', encoding='utf-8') as ic:
        for l in ic.readlines():
            wqs.append(WordQuestion.model_validate_json(l))
    return wqs

import random

def make_options(rng : random.Random, wq : WordQuestion, noptions : int) -> list[str]:
    assert noptions >= 1
    nwrongs = min(noptions - 1, len(wq.question.wrong))
    options = rng.sample(wq.question.wrong, nwrongs)    
    options.append(wq.question.answer)
    rng.shuffle(options)
    return options

class Stat(BaseModel):
    total : int = Field(description='total number of trials')
    failures : int = Field(description='failures')

class Stats(BaseModel):
    stats : dict[int,Stat] = Field(description='Statistics by word no.')

import os

fn_stats = 'data/stats.json'

def load_stats() -> Stats:
    if os.path.exists(fn_stats):
        with open(fn_stats, 'r', encoding='utf-8') as ic:
            return Stats.model_validate_json(ic.read())
    else:
        return Stats(stats= {})

def save_stats(stats : Stats) -> None:
    with open(fn_stats + ".tmp", 'w', encoding='utf-8') as oc:
        oc.write(stats.model_dump_json())
    os.rename(fn_stats + ".tmp", fn_stats)
