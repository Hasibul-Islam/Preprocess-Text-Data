from django.shortcuts import render,redirect
from django.http import JsonResponse, HttpResponse, Http404
import string
from nltk.corpus import stopwords
import pandas as pd
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
import openpyxl
import xlsxwriter
from io import BytesIO
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
def home(request):
    if request.method=='POST':
        try:
            lem=request.POST.get('lemmetization','')
        except:
            lem=None
        try:
            stem=request.POST.get('stemming','')
        except:
            stem=None
        try:
            text = request.POST.get('comment','')
        except:
            text = 'Example Text'
        
        try:
            excelfile = request.FILES["filename"]
        except:
            excelfile = None
        if not excelfile:
            text = text.replace("\\n",'').replace("\\t",' ')
            text = preprocess(text.lower())
            if lem:
                text = lemmetize(text)
            if stem:
                text = stemming(text)
            
            context = {
                'text':text,
            }
            return render(request, 'main/home.html', context)
        else:
            df = pd.read_excel(excelfile)
            df.dropna(inplace=True)
            columns = ['text']
            for i in range(1,len(df.columns)):
                columns.append(df.columns[i])
            df.columns = columns
            df=df.loc[:,df.columns =="text"]
            
            # print(df.columns)
            for ind in df.index:
                df['text'][ind] = df['text'][ind].replace("\\n",'').replace("\\t",' ')
                df['text'][ind] = preprocess(df['text'][ind].lower())
                if lem:
                    df['text'][ind] = lemmetize(df['text'][ind])
                if stem:
                    df['text'][ind] = stemming(df['text'][ind])
                if df['text'][ind].isspace():
                    df['text'][ind] = 'NaN'
            df = df[df.text != 'NaN']
            
            response = download(request, df)
            return response
    else:
        return render(request, 'main/home.html')


def preprocess(text):
    temp_text = ''

    punctuations = string.punctuation 
    for ch in text:
        if ch not in punctuations:
            if ch==' ':
                temp_text+=ch
                
            elif ch.isalnum()==False:
                continue
            else:
                temp_text+=ch
    text = temp_text
    text_tokens = word_tokenize(text)
    tokens_without_sw = [word for word in text_tokens if not word in stopwords.words('english')]
    return ' '.join(tokens_without_sw)


def lemmetize(text):
    lemmatizer = WordNetLemmatizer()
    tmp_text = ""
    for word in text.split():
        # print(word)
        tmp_text+=lemmatizer.lemmatize(word)+' '
    return tmp_text.strip()

def stemming(text):
    stemmer = PorterStemmer()
    tmp_text = ""
    for word in text.split():
        tmp_text+=stemmer.stem(word)+' '
    return tmp_text.strip()

def download(request,df):
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        # Set up the Http response.
        filename = 'processed_text.xlsx'
        response = HttpResponse(
            b.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response