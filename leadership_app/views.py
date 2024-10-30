import json
import os
import re
from django.http import JsonResponse
from django.shortcuts import render
from openai import AzureOpenAI
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Create your views here.
def home(request):
    return render(request, 'leadership_app/home.html')

def remove_references(response):
    # This regex will match patterns like [doc1], [doc2], etc.
    cleaned_response = re.sub(r'\[doc\d+\]', '', response)
    return cleaned_response

def bold_text(text):
    # Replace ** with <b> and </b>
    formatted_text = text.replace("**", "<b>", 1)
    while "**" in formatted_text:
        formatted_text = formatted_text.replace("**", "</b>", 1).replace("**", "<b>", 1)
    return formatted_text

def prompt_completion(message):
    load_dotenv()
    http_proxy = os.getenv('proxy')
    https_proxy = os.getenv('proxy')
    
    # if http_proxy:
    #     os.environ['http_proxy'] = http_proxy
    # if https_proxy:
    #     os.environ['https_proxy'] = https_proxy

    try: 
        endpoint = os.getenv('ENDPOINT_URL')
        deployment = os.getenv('DEPLOYMENT_NAME')
        search_endpoint = os.getenv('SEARCH_ENDPOINT')
        subscription_key = os.getenv('AZURE_OPENAI_API_KEY')

        # Initialize Azure OpenAI client with key-based authentication
        client = AzureOpenAI(  
            azure_endpoint=endpoint,  
            api_key=subscription_key,  
            api_version="2024-05-01-preview",  
        )                   
                                                                            
        personalized_message = "Y'ello! It seems I couldn't find this information. Could you please try rephrasing your query or ask about a different topic? I'm here to help!"
                
        # Prepare the chat prompt  
        chat_prompt = [
            {"role": "system", "content": "You are the chat bot that help individuals that get information from the leadership conference organized by MTN Cameroon."},
            {"role": "system", "content": "In MTN we use Y'ello instead of hello it helps rehenforce our mark and presence and consolidate our collaboration in MTN Cameroon. But say \"Y'ello my name is Leadership Conference(LC) GPT, I am here to assist you for information about the 2024 leadership conference of MTN Cameroon\" only at the begining of a conversion or when you are been asked."},
            {"role": "user", "content": message}
            ]
               
        # Generate the completion  
        completion = client.chat.completions.create(  
            model=deployment,  
            messages=chat_prompt,    
            max_tokens=1000,  
            temperature=0.1,  
            top_p=0.95,  
            frequency_penalty=0,  
            presence_penalty=0,  
            stop=None,  
            stream=False,
            extra_body={
            "data_sources": [{
                "type": "azure_search",
                "parameters": {
                "endpoint": f"{search_endpoint}",
                "index_name": "clc2024",
                "semantic_configuration": "default",
                "query_type": "semantic",
                "fields_mapping": {},
                "in_scope": True,
                "role_information": f"""
                You are the chat bot that help individuals that get information from the leadership conference organized by MTN Cameroon.
                In MTN we use Y'ello instead of hello it helps rehenforce our mark and presence and consolidate our collaboration in MTN Cameroon. But say \"Y'ello my name is Leadership Conference(LC) GPT, I am here to assist you for information about the 2024 leadership conference of MTN Cameroon\" only at the begining of a conversion or when you are been asked.
                When ever you have a question that is not found in you dataset, say the following : {personalized_message}
                """,
                "filter": None,
                "strictness": 3,
                "top_n_documents": 5,
                "authentication": {
                    "type": "api_key",
                    "key": f"{search_key}"
                }
                }
            }]
            }   
        )
        response = remove_references(completion.choices[0].message.content)
        print ("+"*100)
        print(completion.choices[0].message.content+"\n")
        print("-"*100)
        print(response)
        
        return response

    except Exception as e: 

        return f"An unexpected error occurred: {str(e)}"        


@csrf_exempt
def prompt_chat(request):
    
    load_dotenv()

    http_proxy = os.getenv('proxy')
    https_proxy = os.getenv('proxy')
    
    # if http_proxy:
    #     os.environ['http_proxy'] = http_proxy
    # if https_proxy:
    #     os.environ['https_proxy'] = https_proxy
        
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        # input = data.get('question', '')
        conversions = data.get('conversation')

        try: 
            endpoint = os.getenv('ENDPOINT_URL')
            deployment = os.getenv('DEPLOYMENT_NAME') 
            search_endpoint = os.getenv('SEARCH_ENDPOINT') 
            search_key = os.getenv('SEARCH_KEY')
            subscription_key = os.getenv('AZURE_OPENAI_API_KEY')


            print(f"API Key: {os.getenv('AZURE_OPENAI_API_KEY')}")
            print(f"Endpoint URL: {os.getenv('ENDPOINT_URL')}")

            # Initialize Azure OpenAI client with key-based authentication
            client = AzureOpenAI(  
                azure_endpoint=endpoint,  
                api_key=subscription_key,  
                api_version="2024-05-01-preview",  
            )                   
                                                                                
            personalized_message = "Y'ello! It seems I couldn't find this information. Could you please try rephrasing your query or ask about a different topic? I'm here to help!"
                    
            # Prepare the chat prompt  
            chat_prompt = [
                {"role": "system", "content": "You are the chat bot that help individuals that get information from the leadership conference organized by MTN Cameroon."},
                {"role": "system", "content": "In MTN we use Y'ello instead of hello it helps rehenforce our mark and presence and consolidate our collaboration in MTN Cameroon. But say \"Y'ello my name is Leadership Conference(LC) GPT, I am here to assist you for information about the 2024 leadership conference of MTN Cameroon\" only at the begining of a conversion or when you are been asked."},

                ]

            for conversion in conversions:
                chat_prompt.append(conversion)
                            
            # Generate the completion  
            completion = client.chat.completions.create(  
                model=deployment,  
                messages=chat_prompt,    
                max_tokens=1000,  
                temperature=0.1,  
                top_p=0.95,  
                frequency_penalty=0,  
                presence_penalty=0,  
                stop=None,  
                stream=False,
                extra_body={
                "data_sources": [{
                    "type": "azure_search",
                    "parameters": {
                    "endpoint": f"{search_endpoint}",
                    "index_name": "clc2024",
                    "semantic_configuration": "default",
                    "query_type": "semantic",
                    "fields_mapping": {},
                    "in_scope": True,
                    "role_information": f"""
                   You are the chat bot that help individuals that get information from the leadership conference organized by MTN Cameroon.
                    In MTN we use Y'ello instead of hello it helps rehenforce our mark and presence and consolidate our collaboration in MTN Cameroon. But say \"Y'ello my name is Leadership Conference(LC) GPT, I am here to assist you for information about the 2024 leadership conference of MTN Cameroon\" only at the begining of a conversion or when you are been asked.
                    When ever you have a question that is not found in you dataset, say the following : {personalized_message}
                    """,
                    "filter": None,
                    "strictness": 3,
                    "top_n_documents": 5,
                    "authentication": {
                        "type": "api_key",
                        "key": f"{search_key}"
                    }
                    }
                }]
                }   
            )
            response = bold_text(remove_references(completion.choices[0].message.content))
            print ("+"*100)
            print(completion.choices[0].message.content+"\n")
            print("-"*100)
            print(response)
            
            return JsonResponse({'response': response})

        except Exception as e: 

            return JsonResponse({'response': f"An unexpected error occurred: {str(e)}"})           
  
@csrf_exempt        
def test_completion(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        question = data.get('question')
        try:
            response = prompt_completion(question)
            return JsonResponse({'answer': response})
        except Exception as e:
            return JsonResponse({'error': e})
        
@csrf_exempt
def whatsapp_reply(request):
    if request.method == 'POST':
        incoming_msg = request.POST.get('Body', '').lower()
        resp = MessagingResponse()
        msg = resp.message()
        msg.body(f"You said: {incoming_msg}")
        return HttpResponse(str(resp), content_type='application/xml')
    return HttpResponse(status=405)