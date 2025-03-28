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
    
import re

with open('questions400.json', 'r', encoding='utf-8') as ic:
    with open('questions400fix.json', 'w', encoding='utf-8') as oc:
        for l in ic.readlines():
            wq = WordQuestion.model_validate_json(l)
            # Some words start from white space
            wq.word.word = re.sub(r'^\s+', '', wq.word.word)

            # If the answer starts from a capital, wrongs must start with capitals
            if 'A' <= wq.question.answer[0] <= 'Z':
                wq.question.wrong = [ w.capitalize() for w in wq.question.wrong ]
                print(wq.question.wrong)

            # wrong cannot be the answer
            wq.question.wrong = [ w for w in wq.question.wrong if w != wq.question.answer ]
            
            # wrong cannot contain space or '
            wq.question.wrong = [ w for w in wq.question.wrong if ' ' not in w and "'" not in w ]
            
            oc.write(wq.model_dump_json())
            oc.write('\n')
