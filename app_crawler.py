# -*- coding: utf-8 -*-
import streamlit as st
import requests
import urllib3
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin
import logging
import html5lib
import itertools
import os
import json
import sys
from newspaper import Article
from newspaper import Config
from goose3.configuration import Configuration, ArticleContextPattern
import nltk
import nltk.data
import csv
import unidecode
from goose3 import Goose
import re
from newspaper import *
from threading import Thread
import requests
from urllib.request import urlopen
from bs4.dammit import EncodingDetector
import lxml
from contextlib import suppress
import html5lib
from goose3.configuration import Configuration, ArticleContextPattern
import warnings
import html2text



#FUNÇÃO CRAWL PARA PERCORRER AS PÁGINAS A PARTIR DE UMA LISTA DE LINKS
def crawl(paginas, profundidade):
    contador = 1
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    for i in range(profundidade):
        novas_paginas = set()
        for pagina in paginas:
            http = urllib3.PoolManager()
            try:
                dados_pagina = http.request('GET', pagina)
            except:
                print('Erro ao abrir a página ' + pagina)
                # 9
                continue
            try:
                sopa = BeautifulSoup(dados_pagina.data, "lxml",parse_only=SoupStrainer('div', {'id':'content'}))
            except Exception:
                continue
            print(contador)
            contador += 1
            
            try:
                lnks = ['/www.gov.br/receitafederal/', 'https://www.gov.br/pgfn/', 'https://www.gov.br/esocial/','https://www.gov.br/empresas-e-negocios/']
                links = sopa.find_all("a",href=re.compile('|'.join(lnks)))
                #links = sopa.find_all("a",href=re.compile('https://www.gov.br/'))
            except Exception:
                continue
            i = 1
            for link in links:
                try:
                    if ('href' in link.attrs):
                        url = urljoin(pagina, str(link.get('href')))
                
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0]
                        #EXTRAÇÃO DOS DADOS
                        g = []
                        if url[0:4] == 'http':
                            r = bool(re.search("@@search", "{}".format(url)))
                            s = bool(re.search("noticias", "{}".format(url)))
                            t = bool(re.search("dados-abertos", "{}".format(url)))
                            u = bool(re.search("/licitacoes-e-contratos/", "{}".format(url)))
                            v = bool(re.search("aduana", "{}".format(url)))
                            if url not in novas_paginas and url.endswith(('/servico','/videos','.zip','.mp4','.pdf','.odt','.exe','.aspx','.png','.doc','.xls','.xlsx','/view','/avaliar','.jpg','.docx','.csv','.ods')) is False and url.startswith(('http://www.facebook.com/','https://twitter.com')) is False and r is False and s is False and t is False and u is False and v is False:
                                novas_paginas.add(url)
                                g.append(url)
                                for l in g:
                                    print(l)
                                    with open("data_ORIGINAL.csv", "a", newline='', encoding="UTF-8") as arquivo:
                                        writer = csv.writer(arquivo)
                                        config = Configuration()
                                        config.strict = False  # turn of strict exception handling
                                        config.browser_user_agent = 'Mozilla 5.0'  # set the browser agent string
                                        try:
                                            config.http_timeout = 30.0  # set http timeout in seconds
                                        except Exception:
                                            continue
                                        config.known_context_patterns = ArticleContextPattern('div', {'id':'content'})
                                        with Goose(config) as g:
                                            link = '{}'.format(l)
                                            artigo = g.extract(link)
                                            conteud = artigo.cleaned_text[:1000]
                                            def printf(text):
                                                text = text.split()
                                                texto = ' '.join(text)
                                                texto = texto.replace('|',"").replace(',',' ').replace('[','').replace(']','').replace("", '').replace('\n', '').replace(':', ' ').replace(';',' ')
                                                return(texto)
                                            
                                            conteudo = printf(conteud)
                                            conteudo = conteudo.replace('Ir para o',' ')
                                            conteudo = conteudo.split('.')
                                            conteudo = conteudo[:-1]
                                            conteudo = '. '.join(conteudo)
                                            conteudo = str(conteudo) + '.' 
                                            
                                            tit = artigo.title
                                            titulo = tit.replace('|',"").replace(',','').replace('[','').replace(']','').replace("", '').replace('\n', '').replace(':', ' ').replace(';',' ').replace('.','').replace('— Português (Brasil)','')
                                            
                                            af = artigo.final_url
                                            tema = artigo.opengraph['site_name']
                                            
                                            try:
                                                http = urllib3.PoolManager()
                                            except Exception:
                                                continue
                                            try:
                                                dados_pag = http.request('GET', l)
                                            except Exception:
                                                continue
                                            try:
                                                sop = BeautifulSoup(dados_pag.data, "lxml",parse_only=SoupStrainer('div', {'id':'content'}))
                                            except Exception:
                                                continue
                                            lk = ['/www.gov.br/receitafederal/', 'https://www.gov.br/pgfn/', 'https://www.gov.br/esocial/','https://www.gov.br/empresas-e-negocios/']
                                            try:
                                                lks = sop.find_all("a",href=re.compile('|'.join(lk)))
                                            except Exception:
                                                continue
                                            
                                            try:
                                                for g in lks:
                                                    a = str(g.get_text()).split()
                                                    ta = " ".join(a).replace(',',' ').replace(';',' ').title()
                                            except Exception:
                                                continue
                                            
                                            config = Config()
                                            config.memoize_articles=False
                                            config.fetch_images=False
                                            config.language='pt'
                                            try:
                                                config.request_timeout=30
                                            except Exception:
                                                continue
                                            try:
                                                article = Article(str(l), language="pt")
                                            except Exception:
                                                continue
                                            try:
                                                article.download()
                                            except Exception:
                                                continue
                                            try:                    
                                                article.parse()
                                            except Exception:
                                                continue    
                                            try:
                                                article.nlp()
                                                #text = article.text
                                            except Exception:
                                                continue
                                            try:
                                                ky = article.keywords
                                                keyw = " ".join(ky)
                                                keywa = keyw.replace('A2ir',' ').replace('o5',' ').replace('a4ir',' ').replace('de3ir',' ').replace('a2ir','').replace('o1ir','').replace('menu','')
                                                sm = str(article.summary).replace('A2ir','').replace('o5','').replace('a4ir','').replace('de3ir','').replace('|',"").replace(',','').replace('[','').replace(']','').replace("", '').replace('\n', '').replace(':', '').replace(';','').replace('Ir para','').replace('o1  a2  o menu de3  a4','').replace('o1 a2 o menu de3 a4','').replace('Ir para o1Ir para a2Ir para o menu de3Ir para a4Ir para','')
                                                #titulo = str(article.title)
                                            except Exception:
                                                continue
                                            
                                            try:
                                                tags = str(af).replace('|'," ").replace("/", ' ').replace("."," ").replace("_"," ").replace("#"," ").replace("-"," ").replace("www gov br","").replace("https:", "").replace("www gov br receitafederal pt br","").replace("receitafederal pt br","").replace("pt br", "").strip()
                                            except Exception:
                                                continue

                                            writer.writerow([tema,ta,titulo,af,sm,tags,keywa,conteudo])
                        

                                            
                except Exception:
                    continue   
                        
                
                i = i + 1
    
            paginas = novas_paginas
                                        

    return list(novas_paginas)   

#LISTA DE PÁGINAS INICIAIS 

listapaginas = ['https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf-1',
'https://www.gov.br/receitafederal/pt-br/servicos','https://www.gov.br/receitafederal/pt-br/assuntos','https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/perguntas-frequentes','https://www.gov.br/receitafederal/pt-br/onde-encontro',
'https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/formularios','https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/download',
'https://www.gov.br/pgfn/pt-br/assuntos', 'https://www.gov.br/pgfn/pt-br/canais_atendimento',
'https://www.gov.br/receitafederal/pt-br/servicos/dau','https://www.gov.br/pgfn/pt-br/servicos',
'https://www.gov.br/esocial/pt-br/empregador-domestico','https://www.gov.br/empresas-e-negocios/pt-br/redesim',
'https://www.gov.br/esocial/pt-br/empregador-domestico/orientacoes',
'https://www.gov.br/pgfn/pt-br/servicos/orientacoes-contribuintes',
'https://www.gov.br/receitafederal/pt-br/servicos/declaracoes-e-demonstrativos',
'https://www.gov.br/receitafederal/pt-br/servicos/mobile',
'https://www.gov.br/receitafederal/pt-br/servicos/isencao','https://www.gov.br/receitafederal/pt-br/servicos/pagamentos-e-parcelamentos',
'https://www.gov.br/receitafederal/pt-br/servicos/processo','https://www.gov.br/receitafederal/pt-br/servicos/procuracao',
'https://www.gov.br/receitafederal/pt-br/servicos/restituicao-e-compensacao','https://www.gov.br/receitafederal/pt-br/servicos/senhas',
'https://www.gov.br/receitafederal/pt-br/servicos/simples-nacional','https://www.gov.br/receitafederal/pt-br/assuntos/irpf/2020',
'https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria','https://www.gov.br/receitafederal/pt-br/assuntos/processos',
'https://www.gov.br/receitafederal/pt-br/canais_atendimento',
'https://www.gov.br/receitafederal/pt-br/servicos/cadastros','https://www.gov.br/receitafederal/pt-br/servicos/cadastros/cpf','https://www.gov.br/receitafederal/pt-br/servicos/cadastros/cadastro-previdenciario','https://www.gov.br/receitafederal/pt-br/servicos/cadastros/cnpj','https://www.gov.br/receitafederal/pt-br/servicos/cadastros/cnir','https://www.gov.br/receitafederal/pt-br/servicos/cadastros/cno','https://www.gov.br/receitafederal/pt-br/servicos/cadastros/cei','https://www.gov.br/receitafederal/pt-br/servicos/cadastros/cafir','https://www.gov.br/receitafederal/pt-br/servicos/cadastros/caepf',
'https://www.gov.br/receitafederal/pt-br/servicos/certidoes-e-situacao-fiscal','https://www.gov.br/receitafederal/pt-br/servicos/certidoes-e-situacao-fiscal/certidao-de-regularidade','https://www.gov.br/receitafederal/pt-br/servicos/certidoes-e-situacao-fiscal/autenticidade-e-2a-via-de-certidao',
'https://www.gov.br/receitafederal/pt-br/servicos/cobranca-e-fiscalizacao','https://www.gov.br/receitafederal/pt-br/servicos/cobranca-e-fiscalizacao/cobranca','https://www.gov.br/receitafederal/pt-br/servicos/cobranca-e-fiscalizacao/contribuinte-diferenciado','https://www.gov.br/receitafederal/pt-br/servicos/cobranca-e-fiscalizacao/entrega-de-declaracoes','https://www.gov.br/receitafederal/pt-br/servicos/cobranca-e-fiscalizacao/malha-fiscal','https://www.gov.br/receitafederal/pt-br/servicos/cobranca-e-fiscalizacao/procedimento-fiscal','https://www.gov.br/receitafederal/pt-br/servicos/cobranca-e-fiscalizacao/restituicao-e-compensacao','https://www.gov.br/receitafederal/pt-br/servicos/cobranca-e-fiscalizacao/simples-nacional',
'https://www.gov.br/receitafederal/pt-br/assuntos/processos/entrega-de-documentos-digitais','https://www.gov.br/receitafederal/pt-br/assuntos/processos/processo-digital','https://www.gov.br/receitafederal/pt-br/assuntos/processos/processo-fisico'] 


print(len(listapaginas))
for i in listapaginas:
    print(i)


#PARAMETROS: LISTA DE LINKS(string) E PROFUNDIDADE DA BUSCA(int)

def craw(lista,prof):
    paginas = (crawl(lista, prof))

#THREAD PARALELO PARA ACELERAÇÃO WEBSCRAPING
t_0 = Thread(target=craw, args=(listapaginas[0:1],4))
t_1 = Thread(target=craw, args=(listapaginas[2:3],4))
t_2 = Thread(target=craw, args=(listapaginas[4:5],4))
t_3 = Thread(target=craw, args=(listapaginas[6:7],4))
t_4 = Thread(target=craw, args=(listapaginas[8:9],4))
t_5 = Thread(target=craw, args=(listapaginas[10:11],4))
t_6 = Thread(target=craw, args=(listapaginas[12:13],4))
t_7 = Thread(target=craw, args=(listapaginas[14:15],4))
t_8 = Thread(target=craw, args=(listapaginas[16:17],4))
t_9 = Thread(target=craw, args=(listapaginas[18:19],4))
t_10 = Thread(target=craw, args=(listapaginas[20:21],4))
t_11 = Thread(target=craw, args=(listapaginas[22:23],4))
t_12 = Thread(target=craw, args=(listapaginas[24:25],4))
t_13 = Thread(target=craw, args=(listapaginas[26:27],4))
t_14 = Thread(target=craw, args=(listapaginas[28:29],4))
t_15 = Thread(target=craw, args=(listapaginas[30:31],4))
t_16 = Thread(target=craw, args=(listapaginas[32:33],4))
t_17 = Thread(target=craw, args=(listapaginas[34:35],4))
t_18 = Thread(target=craw, args=(listapaginas[36:37],4))
t_19 = Thread(target=craw, args=(listapaginas[38:39],4))
t_20 = Thread(target=craw, args=(listapaginas[40:41],4))
t_21 = Thread(target=craw, args=(listapaginas[42:43],4))
t_22 = Thread(target=craw, args=(listapaginas[44:45],4))
t_23 = Thread(target=craw, args=(listapaginas[46:47],4)) 
t_24 = Thread(target=craw, args=(listapaginas[48:49],4))
t_25 = Thread(target=craw, args=(listapaginas[50:51],4))


t_0.start()
t_1.start()
t_2.start() 
t_3.start()  
t_4.start()
t_5.start()
t_6.start()
t_7.start() 
t_8.start()  
t_9.start()
t_10.start()
t_11.start()
t_12.start() 
t_13.start()  
t_14.start()
t_15.start()
t_16.start()
t_17.start() 
t_18.start() 
t_19.start() 
t_20.start()
t_21.start()
t_22.start() 
t_23.start()  
t_24.start()
t_25.start() 


t_0.join()
t_1.join()
t_2.join() 
t_3.join() 
t_4.join()
t_5.join()
t_6.join()
t_7.join() 
t_8.join()  
t_9.join()
t_10.join()
t_11.join()
t_12.join() 
t_13.join() 
t_14.join()
t_15.join()
t_16.join()
t_17.join()
t_18.join() 
t_19.join() 
t_20.join() 
t_21.join() 
t_22.join() 
t_23.join() 
t_24.join() 
t_25.join() 