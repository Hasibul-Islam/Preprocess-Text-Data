from django.shortcuts import render,redirect
from django.http import JsonResponse, HttpResponse, Http404
import string
from nltk.corpus import stopwords
import pandas as pd
import nltk
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
def home(request):
    if request.method=='POST':
        text = request.POST.get('comment','')
        excelfile = request.POST.get('filename')
        if not excelfile:
            text = preprocess(text.lower())
            context = {
                'text':text,
            }
            
            return render(request, 'main/home.html', context)
        else:
            df = pd.read_excel(excelfile)
            context = {
                'text':text,
            }
            return render(request, 'main/home.html', context)
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