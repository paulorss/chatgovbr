# -*- coding: utf-8 -*-
import csv
import os
import re
import math
import nltk
import sys
import time
import string
import nltk.data
import numpy as np
import unidecode
import pandas as pd
import textdistance
from itertools import chain
from datetime import datetime
import termplotlib as tpl
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.logic import LogicAdapter
from chatterbot.response_selection import get_first_response
from chatterbot.comparisons import levenshtein_distance
from chatterbot import *
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from flask import Flask, render_template, request
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import spatial
from sent2vec.vectorizer import Vectorizer
from threading import Thread
from pytextdist.vector_similarity import qgram_similarity
from pytextdist.vector_similarity import sorensen_dice_similarity
from pytextdist.vector_similarity import jaccard_similarity
from pytextdist.vector_similarity import cosine_similarity

#REGISTRO DE LOG
logging.basicConfig(filename="Log_Train_File.txt", level=logging.INFO, filemode='a')
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

searchbot = ChatBot(
    "Chatterbot", read_only=False, #True MODO SOMENTE LEITURA
    input_adapter="chatterbot.input.VariableInputTypeAdapter",
    output_adapter="chatterbot.output.OutputAdapter",
    #filters=["chatterbot.filters.RepetitiveResponseFilter"],
    preprocessors=['chatterbot.preprocessors.clean_whitespace'],
    #ADAPTADOR MONGODB
    #storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
    #database='XXXXXXX',
    #database_uri="XXXXXX"
    #database_uri="XXXXXX",
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///database.db',
    statement_comparison_function=levenshtein_distance,
    response_selection_method=get_first_response,
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            "statement_comparision_function": "chatterbot.comparisions.levenshtein_distance",
            "response_selection_method": "chatterbot.response_selection.get_first_response",
            #'default_response': 'Não entendi, poderia repetir, por favor!',
            'maximum_similarity_threshold': 1.0
        },
    ]
)

#TREINAMENTO DO CHATBOT 
trainer = ListTrainer(searchbot)

#CORPUS DE TREINAMENTO
conv = open('train_bot.txt', encoding="utf-8").readlines()
#convi = open('chatbotT.txt', encoding="utf-8").readlines()

trainer.train(conv)
#trainer.train(convi)

#LOG DE TREINAMENTO
trainer.export_for_training('./export.json')


@app.route("/")
def index():
    return render_template('index.html')#FRONT-END HTML CHATBOT


#FUNÇÃO DE RESPOSTA DO BOT
def bot(a):
    #PREPROCESSAMENTO DA PERGUNTA REMOVE STOPWORDS NLTK
    msg = str(a).lower()
    entrada = msg
    stop2 = nltk.corpus.stopwords.words('portuguese')
    #ADICIONAR OU REMOVER MANUALMENTE STOPWORDS NLTK
    stop2.append('faço')
    stop2.append('um')
    stop2.append('gostaria')
    stop2.append('fazer')
    stop2.append('saber')
    stop2.append('posso')
    stop2.append('como')
    stop2.append('se')
    stop2.append('preciso')
    stop2.append('quero')
    stop2.remove('meu')
    stop2.remove('não')

    splitter = re.compile('\\W+')

    lista_palavras = []
    lista = [p for p in splitter.split(entrada) if p != '']
    for p in lista:
        if p not in stop2:
            if len(p) > 1:
                lista_palavras.append(p)
    ar = len(lista_palavras)
    e = (lista_palavras[0:ar])
    
    #INPUT USUÁRIO C/ STOPWORDS REMOVIDAS
    joine = " ".join(e)
    
    #REGEX "AND" TERMOS MODO DINAMICO
    base = r'^{}'
    expr = '(?=.*{})'
    words = e
    #print(words)
    #words = ['ajuste', 'sistad']  # example
    sreg = base.format(''.join(expr.format(w) for w in words))
    #print(sreg)
    
    #SEARCH PANDAS UTILIZANDO REGEX CONTANIS
    Resultado = []
    try:
        df = pd.read_csv('data_PROCESSADO.csv', sep=',',error_bad_lines=False,header=None,engine='python',encoding='utf-8')#DEFINIÇÃO DO DATASET
        def search(regex:str, df, case=False):
            textlikes = df.select_dtypes(include=[object, "string"])
            return df[textlikes.apply(lambda column: column.str.contains(regex, regex=True, case=case, na=False)).any(axis=1)]
    except Exception:
        pass

    a = search(sreg, df)
    b = np.array(a)  
    c = b.tolist()

    Resultado.append(c)

    set_resultado = list(chain(*Resultado))


    #CLASSIFICA RESULTADOS ENCONTRADOS PELO PANDAS DE ACORDO COM ÍNDICE DE Levenshtein BIBLIOTECA fuzzywuzzy * LIMITE DE 50 RESULTADOS
    set_resultados = process.extract(joine, choices=set_resultado,limit=100,scorer=fuzz.token_set_ratio)
    #print(set_resultados)
    
    '''
    #MODELO WORD2VEC BERT DESEMPENHO BAIXO MESMO COM THREAD
    sentences = []
    for f in set_resultados:
        #TRATAMENTO STRING SEM PONTUAÇÃO E ACENTO
        joinu = unidecode.unidecode(joine)
        #print(f[0][1])
        
        #COLUNAS SELECIONADAS PARA COMPARAÇÃO
        jv = [str(f[0][1]),str(f[0][6]),str(f[0][3]),str(f[0][4]),str(f[0][5])]
        
        js = list(set(jv))
        
        #print(js)
        jj = " ".join(js)
        #print(jj)
                
        p1 = jj.lower()
        p2 = re.sub(r'\d+', "", p1)
        p3 = p2.strip()
        p4 = p3.translate(str.maketrans('', '', string.punctuation))
        p5 = unidecode.unidecode(p4)
        sentences.append(p5[:500])
        
    sentences.insert(0, joine) 
    print((sentences[0]))
    vectorizer = Vectorizer()
    vectorizer.bert(sentences)
    vectors_bert = vectorizer.vectors
    def b1():
        dist_1 = spatial.distance.cosine(vectors_bert[0], vectors_bert[1])
        print(dist_1)
    def b2():
        dist_2 = spatial.distance.cosine(vectors_bert[0], vectors_bert[2])
        print(dist_2)
    def b3():
        dist_3 = spatial.distance.cosine(vectors_bert[0], vectors_bert[3])
        print(dist_3)
    t_0 = Thread(target=b1)
    t_1 = Thread(target=b2)
    t_2 = Thread(target=b3)
    t_0.start()
    t_1.start()
    t_2.start()    
    '''
    
    set_v = []
    for f in set_resultados:
        #TRATAMENTO STRING SEM PONTUAÇÃO E ACENTO
        joinu = unidecode.unidecode(joine)
        #print(f[0][1])
        
        #COLUNAS SELECIONADAS PARA COMPARAÇÃO
        jv = [str(f[0][2]),str(f[0][3]),str(f[0][6]),str(f[0][7]),str(f[0][8])]#,str(f[0][4]),str(f[0][5])]
        #print(jv)

        
        js = list(set(jv))
        
        #print(js)
        jj = " ".join(js)
        #print(jj)
        
        p1 = jj.lower()
        p2 = re.sub(r'\d+', "", p1)
        p3 = p2.strip()
        p4 = p3.translate(str.maketrans('', '', string.punctuation))
        p5 = unidecode.unidecode(p4)
        

        #CLASSIFICAÇÃO INTERNA DA AMOSTRA SELECIONADO POR Jaccard Similarity
        #tj = textdistance.jaccard.normalized_similarity(joinu, p5)
        tc = jaccard_similarity(joinu, p5, n=1)

        #CLASSIFICAÇÃO INTERNA DA AMOSTRA SELECIONADO POR Similaridade de Cosseno
        #tc = textdistance.cosine.normalized_similarity(joinu, p5)
        tj = cosine_similarity(joinu, p5, n=1)
                
        #CLASSIFICAÇÃO INTERNA DA AMOSTRA SELECIONADO POR ratcliff_obershelp or sorensen_dice
        #tr = textdistance.ratcliff_obershelp.normalized_similarity(joinu, p5)
        tr = sorensen_dice_similarity(joinu, p5, n=1)
                
        #CLASSIFICAÇÃO INTERNA DA AMOSTRA SELECIONADO POR jaro_winkler OR qgram_similarity
        #tw = textdistance.jaro_winkler.normalized_similarity(joinu, p5)
        tw = qgram_similarity(joinu, p5, n=1)
        
        #RESULTADO ACUMULADO DOS ÍNDICES DE TEXT DISTANCE JACCARD + COSSENO 
        tt = (tj + tc + tw + tr) / 4
        
        ab = tt*100
        ac = round(ab,2)
        set_v.append([f[0],ac]) #ATRIBUINDO ÍNDICE PARA CADA RESPOSTA SELECIONADA

    set_v = [list(i) for i in set_v]
    #ORDENANDO INTERNAMENTE OS RESULTADOS DE ACORDO COM ÍNDICE ATRIBUÍDO    
    set_resultadosv = sorted(set_v, key=lambda x: x[-1], reverse=True)  
    
    #SEPARA INDICE PARA MÉTRICA EM BACK-END TERMINAL
    listax = []
    listay = []
    for x in set_resultadosv:
        listax.append(int(x[0][0]))
        listay.append(float(x[-1]))
    
    x=listax
    y=listay
    
    #MÉTRICA DE ACOMPANHAMENTO DE CLASSIFICAÇÃO DOS RESULTADOS
    try:
        fig = tpl.figure()
        fig.barh(listay,listax,force_ascii=True)
        print('********** CLASSIFICAÇÃO ÍNDICE DE SIMILARIDADE PARA - {} **********'.format(joine.upper()))
        print(' ')
        fig.show()
        print(' ')
        print('*************************************************************')
    except Exception:
        pass

    #REMOVE INDEX E FATOR LEVENSHTEIN PARA GERAR A RESPOSTA DO CHATBOT
    for r in set_resultadosv:
        del r[0][0]
        #del r[0][-1]
        #del r[0][-1]
        del r[-1]
        #print(r)


    def lista_simples(lista):
        if isinstance(lista, list):
            return [sub_elem for elem in lista for sub_elem in lista_simples(elem)]
        else:
            return [lista]
        
    #CONFIGURAÇÃO DO LAYOUT DA RESPOSTA DO CHATBOT
    res = []    
    for e in set_resultadosv:
        lista = e        
        resultadov = lista_simples(lista)
        #print(resultadov)
        link = str("    <a target='_blank' href='{}'><button style='background: #6264A7; border-radius: 2px; padding: 6px; font-family: Segoe UI SemiBold; cursor: pointer; color: #fff; border: none; font-size: 14px;'>Acessar</button></a>".format(resultadov[3]))
        titulo = str("<b><i> {} </b></i>").format(resultadov[2])
        texto = str(resultadov[-1])
        area = str(resultadov[0])
        #RESPOSTA EXPORTADA
        rr = [link,area,titulo,texto]
        rs = ' '.join(rr)
        res.append(rs)

    #RETORNAR LISTA DE RESPOSTAS ORDENADAS ** LIMITE 10
    Resultadoz = []
    for indice, valor in enumerate(res[:11]):
        z = "<b> %s </b> - %s" % (indice + 1, str(valor))#str(valor).lstrip('[').rstrip(']').lstrip('"').rstrip('"'))

        Resultadoz.append(z)
        if valor == 11:
            break
    

    s = " <br><br> "
    ss = s.join(Resultadoz[:3])#AJUSTE DE LIMITE DE OPÇÕES DE RESPOSTAS FORNECIDAS PELO BOT
    ag = int(len(set_resultado))
    if ag == 0:
        #FALLBACK EM CASO DE NÃO ENCONTRAR RESPOSTA QUE ATENDA A SOLICITAÇÃO NO DATASET
        return str("\U0001F614 Desculpe, ainda não tenho uma resposta sobre esse assunto para você!<br><br><b>Mas realizei uma pesquisa para tentar ajudar \U0001f600:</b> <a target='_blank' href='https://www.google.com/search?q=site:gov.br/receitafederal/pt-br/ intext:{}'><button style='background: #6264A7; border-radius: 3px; font-family: Segoe UI SemiBold; padding: 8px; cursor: pointer; color: #fff; border: none; font-size: 16px;'>{}</button></a>".format(msg,msg))

    
    else:
        pass
    #RETORNA RESPOSTA APÓS PROCESSAMENTO E CLASSIFICAÇÃO
    return ('\U0001F609 Encontrei algumas possíveis respostas sobre ' + '<b>' + msg.title() + '.' + '</b>' + '<br><br>Segue relação dos resultados mais relevantes de acordo com sua pesquisa: ' + '<br><br><br><br>' + str(ss) + '<br><br><br><br>' + ' * Não encontrou a resposta? Você pode refazer a pergunta de forma mais específica ou com outras palavras que tentarei ajudar!</b> \U0001F9BE')


@app.route("/get")
#FUNÇÃO DE RESPOTA DO CHATBOT

def get_bot_response():

    while True:
        userText = request.args.get('msg')
        response = searchbot.get_response(userText)
        #COEFICIENTE DE SIMILARIDADE MÁXIMA DO CORPUS DO CHATBOT
        if float(response.confidence) == 1.0:
            #time.sleep(0.5) 
            return str("\U0001F609" + str(searchbot.get_response(userText)))
        #FALLBACK RESPOSTA NÃO ENCONTRADA
        #elif float(0.01 < response.confidence < 0.69):
        #    'IDKresponse' == searchbot.get_response('IDKnull')
        #    time.sleep(0.5)
        #    return str(searchbot.get_response('IDKnull'))
        #ATIVAR PESQUISA EM DATASET
        elif float(response.confidence < 1.0):
            return bot(userText)
        
    
if __name__ == '__main__':
    app.run()

