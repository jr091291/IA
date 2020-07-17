# -*- coding: utf-8 -*-

import argparse
from urllib.parse import urlparse
import hashlib
import requests
import json
import math
import re

from sspipe import p, px

import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords

from web_scraper import Scraper
from colors import Colors

import logging
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


def main(filename):
    logger.info('Starting cleaning process')

    df = _read_data(filename)
    df = _extract_info(df, 'price', '(\d{1,3}[.,\']?){1,4}', lambda e: _tryconvert (str(e).replace('.','').replace(',','.'), 0, float))
    df = _extract_info(df, 'opinions', '\d+', lambda e: _tryconvert ( str(e), 0, float))
    df = _extract_info(df, 'average_opinions', '\d+[\,\.]{1}\d+', lambda e: _tryconvert ( str(e), 0, float))
    df = _extract_info(df, 'seller', '[^\/]+$',  default='UNKNOW')
    df = _extract_color(df, _capture_colors(), default='UNKNOW')

    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    #df = _extract_host(df)
    df = _generate_uids_for_rows(df)
    df = _tokenize_column(df, 'title')
    df = _tokenize_column(df, 'raw_description')
    df = _remove_duplicate_entries(df, 'url')
    df = _drop_rows_with_missing_values(df)
    _save_data(df, filename)

    return df

def _extract_info(df, label: str, regex = '', func= lambda x: x, default= None):
  try:
    df[label]= (df[label]
        .apply(lambda e: str(e))
        .str.extract(r'(?P<extract>{})'.format(regex))
        .loc[:, ['extract']]
        .applymap(func)
    )
  except  Exception as e:
    print('Error extract info: {}'.format(e))
  finally:
    if default:
        df=_set_default_value(df, label, default)
    return df


def _tryconvert(value, default, *types):
    for t in types:
        try:
            val = t(value)
            if t == float or t== int:
                return default if math.isnan(val)  else val
            return val
        except (ValueError, TypeError): 
            continue
    return default

def _set_default_value(df, label, value):
    mask = df[label].isna()
    df.loc[mask,[label]] = value
    return df

def _extract_color(df, c: Colors, default=None):  
    df.loc[:,['color']] =df[['color']].applymap( lambda e: e if c.validate_color(str(e)) else None)     
    
    mask = df['color'].isna()
    df.loc[mask,['color']] = df[mask]['url'].apply( lambda e : c.extract_color(e) )
    
    if default:
        df=_set_default_value(df, 'color', default)
    return df


def _read_data(filename):
    logger.info('Reading file {}'.format(filename))

    return pd.read_csv(filename, encoding='utf-8')


def _extract_newspaper_uid(filename):
    logger.info('Extracting newspaper uid')
    newspaper_uid = filename.split('_')[0]

    logger.info('Newspaper uid detected: {}'.format(newspaper_uid))
    return newspaper_uid


def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info('Filling newspaper_uid column with {}'.format(newspaper_uid))
    df['newspaper_uid'] = newspaper_uid

    return df


def _extract_host(df):
    logger.info('Extracting host from urls')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)

    return df


def _generate_uids_for_rows(df):
    logger.info('Generating uids for each row')
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(str(row['url']).encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest())
            )

    df['uid'] = uids

    return df.set_index('uid')


def _tokenize_column(df, column_name):
    logger.info('Calculating the number of unique tokens in {}'.format(column_name))
    stop_words = set(stopwords.words('spanish'))

    n_tokens =  (df
                 .dropna()
                 .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
                 .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
                 .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
                 .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
                 .apply(lambda valid_word_list: len(valid_word_list))
            )

    df['n_tokens_' + column_name] = n_tokens

    return df


def _remove_duplicate_entries(df, column_name):
    logger.info('Removing duplicate entries')
    df.drop_duplicates(subset=[column_name], keep='first', inplace=True)

    return df


def _drop_rows_with_missing_values(df):
    logger.info('Dropping rows with missing values')
    return df.dropna()


def _save_data(df, filename):
    clean_filename = 'cleaned_{}'.format(filename)
    logger.info('Saving data at location: {}'.format(clean_filename))
    df.to_csv(clean_filename)


def _format_results_colors(resuts_colors):
    try:
        colors = ['dorado', 'plateado', 'cafe', 'azul', 'blanco','rosado', 'negro']
        for c in resuts_colors:
          color = c['title']
          if color.find(':') < 0:
            color = color.replace(' (color)','').lower().rstrip().replace(' de ','')
            colors.append(color)
        colors.sort()
        return list(set(colors))
    except:
        return colors 


def _get_watson_translate(words: list, languaje_from, languaje_to): 
    try:
        url = "https://api.us-south.language-translator.watson.cloud.ibm.com/instances/ae02dcf6-a415-48d7-9955-ef1a0c38a12b/v3/translate?version=2018-05-01"
  
        body ={
            "text": words,
            "model_id": "{}-{}".format(languaje_from, languaje_to)
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic YXBpa2V5Om5XUWFrRTM4N01seHNoSDNOSmRhWmlyMGlvdGJ0SEdKc3BwWUVDX08tRmhI'
        }

        response = requests.request("POST", url, headers=headers, json = body)

        res = response.text.encode('utf8')
        return json.loads(res)
    
    except Exception as e:
        logger.error(e)
        return []


def _capture_colors():
    return Colors(['cobre','escarlata','amarillo nápoles','almagre','blanco navajo','bronceado','gris frío','rojo naranja','menta','rosa shocking','añil','blancocinc','herrumbre','violeta','marron','bistre','negrohumo','turquí','hígado','caqui','azul klein','amaranto','rufo','rosa naranja','rojo persa','azul maya','color caramelo (colorante)','azul majorelle','oro','azulprusia','celeste','amatista','rojo toscano','zafiro','anaranjado','azul alicia','violín','carne','coral','calabaza','verde ceniza','verdeparís','cafe','ocaso','malva','junquillo','amarillo cadmio','gutagamba','wengué','caoba','borgoña','blanco','púrpuratiro','verde veronese','cardo','gris ceniza','marrón','azul cobalto','viridián','lava','esmeralda','bígaro','carmín','cardenal','plateado','melón','león','verde cian','fucsia','amarillo selectivo','gris','rojo','granate','azul acero','azul eton','burdeos','rosa','amarillo hansa','amarillo indio','lavanda','naranjaportland','guinda','crema','gris acorazado','rojo púrpura','carmínalizarina','azul ultramar','encaje antiguo','gris cadete','amarillo monoazo','bermejo','lino','azul marino','trigo','lila','aureolina','negro','arena','concha','llama','esmalte (heráldica)','grispayne','gestión del color','lapislázuli','ante','carmesí','pizarra','rojo anaranjado','rosa mountbatten','amarillo tráfico','siena','cordobán','malaquita','camello','azul columbia','beis','azul verde','grisdavy','jazmín','bermellón','vino','verde','carbón','rojo veneciano','amarillo','azul púrpura','café con leche cósmico','verde amarillo','cardenillo','rojo indio','oliva','gamuza','rojofalun','rojo upsdell','secuoya','rojo ferrari','salmón','cian','naranja persa','lima','azul aciano','púrpura','amarillo naranja','azul','azul horizonte','chartreuse','azur','barbecho','ámbar','ftalocianina','turquesa','verde primavera','ocre','verde hooker','verde oliva','magenta','maíz','amarillocobalto','sepia','lirio','plomo','cerúleo','morado','xántico','azul tiffany','aguamarina','kermes (pigmento)','dorado','verde esmeralda','tomate','british racing green','naranja','feldgrau','durazno','rosa mexicano','plata','limón','frambuesa','amarillocromo','copper','scarlet','yellow napoles','alcatfish','white navgarlic','tan','cold grey','orange red','mint','pink shocking','anil','white','black','brown','bistro','black','turqui','liver','khaki','blue klein','red Persian','blue majorelle','orange','blue','blue','brown','orange','blue','brown','green','brown','orange','blue','brown','brown','green','brown','brown','brown','green','brown','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','white','brown','green','green','green','green','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green','brown','green veronese','thistle','grey ash','brown','cobalt blue','viridian','lava','emerald','bigarian','carmine','cardinal','silver','melon','lion','green cyan','fuchsia','yellow selective','gray','red','maroon','blue steel','blue ethon','burgundy','pink','orange','red','purple','cream','blue','orange','red','white','black','white','red','white','blue','white','red','white','blue','white','blue','white','blue','white','blue','white','blue','white','blue','white','blue','white','blue','white','blue','white','black','white','black','white','black','white','black','white','black','white','white','blue','white','black','white','black','white','black','white','black','white','black','white','black','white','black','white','black','white','black','white','black','white','black','white','black','white','black','white','black','white','black','white','black','white','white colour','lapislazi','ante','crimson','slate','orange red','pink mountbatten','yellow traffic','siena','cordoban','malachite','camel','blue columbia','beis','green blue','grisdavy','jasmine','vermilion','wine','green','charcoal','red Venetian','yellow','blue','red','brown','green','red','green','red','brown','green','red','red','red','green','yellow','red','red','red','green','yellow','red','red','red','green','yellow','red','red','red','green','yellow','red','red','red','green','yellow','red','red','red','yellow','blue','blue','blue','blue','white','blue','white','blue','white','blue','blue','white','blue','blue','white','blue','blue','white','blue','blue','white','blue','blue','white','blue','blue','white','blue','blue','white','blue','blue','white','blue','blue','white','blue','blue','white','blue','blue','white','blue','blue','white','spring','ochre','green hooker','olive green','magenta','corn','yellowish','sepia','lily','lead','cerulean','purple','xantico','tiffany blue','aquamarine','kermes (pigment)','golden','emerald green','tomato','british racing green','orange','feldgrau','peach','Mexican rose','silver','lemon','raspberry','yellowish'])
    url_colors = 'https://es.wikipedia.org/wiki/Anexo:Colores_por_orden_alfab%C3%A9tico'
    selector_colors = "#mw-content-text > div > p > a[title]"
    
    sc = Scraper(url_colors)
    c  = Colors( _format_results_colors(sc.query(selector_colors)) ) 
    
    response_transtation = _get_watson_translate(c.colors, 'es','en')
    
    if response_transtation['word_count']:
        english_colors = [color['translation'] for color in response_transtation['translations']]
        c.colors = c.colors + english_colors
    return c


if __name__ == '__main__':
    # df = main('linio_06_11_2020_items.csv')
    # df = main('Mercadolibre.csv')
    # df = main('Alkosto_06_11_2020_items.csv')
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='The path to the dirty data',
                        type=str)

    args = parser.parse_args()
    main(args.filename)
