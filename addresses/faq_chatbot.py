import os
import warnings
from gensim.models import doc2vec
from gensim.models.doc2vec import TaggedDocument
import pandas as pd
import jpype

d2v_faqs = doc2vec.Doc2Vec.load(os.path.join('./model/d2v_faqs_size200_min5_epoch20_naver_physics_qna.model'))

# csv 파일 불러오기 (사전작업은 노트북에서 주피터 노트북 켜고 data_extraction.ipynb으로 함)
faqs = pd.read_csv(os.path.join('./data/total.csv'), sep="\t", encoding='UTF8')
df2 = pd.DataFrame(columns=['질문', '답변'])  # faqs에서 질문에 해당하는 답변을 한 세트로 묶어 df2에 저장하려고 빈 데이터프레임을 만든다.
qna_num = 0  # 질문답변 번호인 qna_num 초기화

for i in range(0, len(faqs)):  # 질문-답변 행 개수만큼 반복
    if int(faqs.loc[i, :][1]) == 1:
        qna_num = qna_num + 1  # 이 줄 때문에 데이터프레임에 질문과 답변이 1번부터 들어감
        # DataFrame에 특정 정보를 이용하여 data 채우기
        df2.at[qna_num, '질문'] = faqs.loc[i, :][4]  # 데이터프레임에 질문 입력
        df2_temp = []  # 답변 넣을 리스트 초기화
    else:
        df2_temp.append(faqs.loc[i, :][4])  # 같은 질문에 대한 답변을 누적하여 저장
        df2.at[qna_num, '답변'] = df2_temp  # qna_num에 해당하는 데이터프레임의 답변 열에 답변 입력

from konlpy.tag import Mecab

mecab = Mecab()
text = u"""이제 구글 코랩에서 Mecab-ko라이브러리 사용이 가능합니다. 읽어주셔서 감사합니다."""
nouns = mecab.nouns(text)
print(nouns)

filter_mecab = ['NNG',  # 보통명사
                'NNP',  # 고유명사
                'SL',  # 외국어
                ]

def tokenize_mecab(doc):
    # jpype.attachThreadToJVM()
    token_doc = ['/'.join(word) for word in mecab.pos(doc)]
    return token_doc

def tokenize_mecab_noun(doc):
    # jpype.attachThreadToJVM()
    token_doc = ['/'.join(word) for word in mecab.pos(doc) if word[1] in filter_mecab]
    return token_doc

index_questions = []
for i in range(1, len(df2) + 1):  # df2가 1부터 시작하므로 개수+1개만큼까지 써줘야 전체 데이터를 쓸 수 있다.
    index_questions.append([tokenize_mecab_noun(df2['질문'][i]), i])  # 명사만 추출

# Doc2Vec에서 사용하는 태그문서형으로 변경
tagged_questions = [TaggedDocument(d, [int(c)]) for d, c in index_questions]

# FAQ 답변
def faq_answer(input):
    # 테스트하는 문장도 같은 전처리를 해준다.
    tokened_test_string = tokenize_mecab_noun(input)

    topn = 3  # 가장 유사한 질문 세 개까지만
    test_vector = d2v_faqs.infer_vector(tokened_test_string)
    result = d2v_faqs.docvecs.most_similar([test_vector], topn=topn)

    for i in range(topn):
        print("유사질문 {}위 | 유사도: {:0.3f} | 문장 번호: {} | {}".format(i + 1, result[i][1], result[i][0], df2['질문'][result[i][0]]))
        #print("\t질문 {} | 문장 번호: {} | {}".format(i + 1, result[i][0], df2['답변'][result[i][0]]))
        #print(len(df2['답변'][result[i][0]]))
        #for j in range(len(df2['답변'][result[i][0]])):
        #    #print(j)
        #    print("\t질문 {} | 답글순서 {} | 문장 번호: {} | {}".format(i + 1, j + 1, result[i][0], df2['답변'][result[i][0]][j]))

    return df2['답변'][result[i][0]]

print('챗봇 불러오기 완료')