# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import csv
import unidecode
import streamlit as st
import matplotlib.pyplot as plt
import string
import math
import textdistance
from itertools import chain
from datetime import datetime
import numpy as np
import unidecode
import csv
import os
from flask import Flask, render_template, request
import re
import nltk
import os
import sys
import nltk
import nltk.data
import re
import sys
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
import time
from pandas import DataFrame
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
import plotly_express as px
from pytextdist.vector_similarity import qgram_similarity
from pytextdist.vector_similarity import sorensen_dice_similarity
from pytextdist.vector_similarity import jaccard_similarity
from pytextdist.vector_similarity import cosine_similarity


def main():

    #df = load_data()

    page = st.sidebar.selectbox("Choose a page", ['Consulta', 'Métricas','Exploração Dados Brutos','Exploração Dados Processados'])

    if page == 'Consulta':
        
        st.markdown("### 🎲 ANÁLISE E EXPLORAÇÃO DE DADOS")
        st.markdown("Este aplicativo é um painel Streamlit hospedado no Heroku que pode ser usado para explorar os resultados e verificar métricas.")  
        st.markdown("**♟ Estatísticas Gerais ♟**")
        st.markdown("* O objetivo é oferecer uma ferramenta gerencial com visão geral dos dados, incluindo dataset e SIMILARIDADEs.")       
        
        st.title('Assitente Virtual - Gerencial')

        def bot(a):
            # PREPROCESSAMENTO DA PERGUNTA REMOVE STOPWORDS
            msg = str(a).lower()
            entrada = msg
            stop2 = nltk.corpus.stopwords.words('portuguese')
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
            splitter = re.compile('\\W+')

            lista_palavras = []
            lista = [p for p in splitter.split(entrada) if p != '']
            for p in lista:
                if p not in stop2:
                    if len(p) > 1:
                        lista_palavras.append(p)
            ar = len(lista_palavras)
            e = (lista_palavras[0:ar])

            # JOIN PREPROCESSAMENTO
            joine = " ".join(e)
            # print(joine)

            # REGEX "AND" TERMOS MODO DINAMICO
            base = r'^{}'
            expr = '(?=.*{})'
            words = e
            # print(words)
            # words = ['ajuste', 'sistad']  # example
            sreg = base.format(''.join(expr.format(w) for w in words))
            # print(sreg)

            # SEARCH PANDAS REGEX CONTANIS
            Resultado = []
            df = pd.read_csv('data_PROCESSADO.csv', sep=',', error_bad_lines=False, header=None,
                             engine='python', encoding='utf-8')

            def search(regex: str, df, case=False):
                textlikes = df.select_dtypes(include=[object, "string"])
                return df[
                    textlikes.apply(lambda column: column.str.contains(regex, regex=True, case=case, na=False)).any(
                        axis=1)]
                # return df[textlikes.apply(lambda column: column.str.contains(fr'\b{regex}\b', regex=True, case=case, na=False)).any(axis=1)]

            a = search(sreg, df)

            b = np.array(a)

            c = b.tolist()

            Resultado.append(c)

            set_resultado = list(chain(*Resultado))

            # CLASSIFICA RESULTADOS PELO SIMILARIDADE DE Levenshtein
            # set_resultados = sorted(set_resultado, key=lambda x: x[3], reverse=True)

            set_resultados = process.extract(joine, choices=set_resultado, limit=30, scorer=fuzz.token_sort_ratio)

            set_v = []
            for f in set_resultados:
                joinu = unidecode.unidecode(joine)
                # print(joinu)

                jv = [str(f[0][2]),str(f[0][3]),str(f[0][6]),str(f[0][7]),str(f[0][8])]#,str(f[0][4]),str(f[0][5])]

                js = list(set(jv))
                jj = " ".join(js)

                p1 = jj.lower()
                p2 = re.sub(r'\d+', "", p1)
                p3 = p2.strip()
                p4 = p3.translate(str.maketrans('', '', string.punctuation))
                p5 = unidecode.unidecode(p4)
                # print(p5)

                #CLASSIFICAÇÃO INTERNA DA AMOSTRA SELECIONADO POR Jaccard Similarity
                #tj = textdistance.jaccard.normalized_similarity(joinu, p5)
                tj = cosine_similarity(joinu, p5, n=1)

                #CLASSIFICAÇÃO INTERNA DA AMOSTRA SELECIONADO POR Similaridade de Cosseno
                #tc = textdistance.cosine.normalized_similarity(joinu, p5)
                tc = jaccard_similarity(joinu, p5, n=1)
                
                #CLASSIFICAÇÃO INTERNA DA AMOSTRA SELECIONADO POR ratcliff_obershelp
                #tr = textdistance.ratcliff_obershelp.normalized_similarity(joinu, p5)
                tr = sorensen_dice_similarity(joinu, p5, n=1)
                
                #CLASSIFICAÇÃO INTERNA DA AMOSTRA SELECIONADO POR jaro_winkler
                #tw = textdistance.jaro_winkler.normalized_similarity(joinu, p5)
                tw = qgram_similarity(joinu, p5, n=1)
                
                #RESULTADO ACUMULADO DOS SIMILARIDADES DE TEXT DISTANCE JACCARD + COSSENO 
                tt = (tj + tc + tw + tr) / 4
                
                ab = tt*100
                ac = round(ab,2)
                set_v.append([f[0],ac]) #ATRIBUINDO SIMILARIDADE PARA CADA RESPOSTA SELECIONADA

            set_v = [list(i) for i in set_v]
            # print(set_v)
            # print(set_v[0][-1])

            set_resultadosv = sorted(set_v, key=lambda x: x[-1], reverse=True)

            # SEPARA INDICE PARA MÉTRICA
            listax = []
            listay = []
            for x in set_resultadosv:
                listax.append(str(x[0][2]))
                # print(set_resultadosv[x][0])
                listay.append(float(x[-1]))
                # print(set_resultadosv[x][3])

            dfa = pd.DataFrame(
                {'RESPOSTA': listax[:5],
                 'SIMILARIDADE': listay[:5]
                 })
            
            dfa = dfa.astype(str)
            #print(dfa.dtypes)
            dfa.to_csv('metrica.csv', sep=',', index=False)

            # REMOVE INDEX E FATOR LEVENSHTEIN
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

            df = DataFrame(res, columns=['Respostas'])
            df.index = df.index + 1
            html = df.to_html(classes='table table-striped')
            ag = int(len(res))
            if ag == 0:
                fb = str(
                    "\U0001F614 Desculpe, ainda não tenho uma resposta sobre esse assunto para você!<br><br><b>Mas realizei uma pesquisa para tentar ajudar \U0001f600:</b> <a target='_blank' href='https://www.google.com/search?q=site:gov.br/receitafederal/pt-br/ intext:{}'><button style='background: #6264A7; border-radius: 3px; font-family: Segoe UI SemiBold; padding: 8px; cursor: pointer; color: #fff; border: none; font-size: 16px;'>{}</button></a>".format(
                        msg, msg))

                return st.markdown(body=fb, unsafe_allow_html=True)

            else:
                pass

            return st.markdown(df.to_html(escape=False), unsafe_allow_html=True) 

        def get_text():
            st.info('DIGITE ABAIXO PARA EFETUAR A BUSCA NO BANCO DE DADOS')
            input_text = st.text_input("PESQUISA RÁPIDA", "sistad")

            return input_text

        user_input = get_text()
        bot(user_input)
        # st.text_area(label=' ',value=bot(user_input), height=300, max_chars=None, key=None)
        # st.markdown(body=bot(user_input), unsafe_allow_html=True)

    elif page == 'Exploração Dados Processados':
        st.title("Análise e Exploração dos Dados Processados")
        data_set = 'data_PROCESSADO.csv'
        df = pd.read_csv(data_set, sep=',', error_bad_lines=False, engine='python', encoding='utf-8', na_filter=True)
        pr = ProfileReport(df, explorative=True)
        st.write(df)
        my_bar = st.progress(80)
        for percent_complete in range(100):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 1)
        st_profile_report(pr)
        
    elif page == 'Exploração Dados Brutos':
        st.title("Análise e Exploração dos Dados Brutos")
        data_set = 'data_ORIGINAL.csv'
        df = pd.read_csv(data_set, sep=',', error_bad_lines=False, engine='python', encoding='utf-8', na_filter=True)
        pr = ProfileReport(df, explorative=True)
        st.write(df)
        my_bar = st.progress(80)
        for percent_complete in range(100):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 1)
        st_profile_report(pr)

    else:
        st.title("Métrica de Resultados")
        df_bot = pd.read_csv('metrica.csv', sep=',')
        df_bot = df_bot.astype({"RESPOSTA": str, "SIMILARIDADE": int})
        print(df_bot.dtypes)
        st.dataframe(df_bot)
        #st.markdown('**Gráficos de Resultados**.')
        st.success('Gráficos de Resultados')
        df_bot.plot(kind='hist', x='RESPOSTA', y='SIMILARIDADE')
        fig, ax = plt.subplots()
        ax.hist(df_bot, bins=20)
        st.bar_chart(df_bot['SIMILARIDADE'])
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

                
        fig = px.scatter(df_bot, x ="RESPOSTA",y="SIMILARIDADE")

        st.plotly_chart(fig)

                
        fig2 = px.bar(df_bot, x="RESPOSTA", y="SIMILARIDADE")
        st.plotly_chart(fig2)
        
        fig3 = px.bar(df_bot, y="RESPOSTA", x="SIMILARIDADE", orientation="h", hover_name="SIMILARIDADE",
             color_discrete_sequence=["red", "green", "blue", "goldenrod", "magenta"],
             title="MÉTRICA"
            )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='middle center')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig3)
        
        
        fig4 = px.line(df_bot, x='RESPOSTA', y='SIMILARIDADE')
        st.plotly_chart(fig4)      
        
        
        fig5 = px.bar(df_bot, x='RESPOSTA', y='SIMILARIDADE')
        st.plotly_chart(fig5) 
        
        

@st.cache
def load_data():
    df = pd.read_csv('data_PROCESSADO.csv', sep=',', error_bad_lines=False, engine='python', encoding='utf-8', na_filter=True)
    return df

if __name__ == '__main__':
    main()