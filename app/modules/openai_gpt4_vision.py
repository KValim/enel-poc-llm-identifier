import base64
import os
import time
import requests

from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv(override=True)

# Chave de API e ID do assistente
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ENEL_ASSISTANT_ID = os.getenv('ENEL_ASSISTANT_ID')

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<your OpenAI API key if not set as env var>"))

def encode_image(image_path):
    """
    Codifica uma imagem em base64.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# def submit_image(assistant_id, thread, image_path):
#     """
#     Submete uma imagem para análise utilizando o assistente, agora usando a API de chat.
#     """
#     base64_image = encode_image(image_path)
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {OPENAI_API_KEY}"
#     }
#     payload = {
#         "model": "gpt-4-turbo",
#         "messages": [
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": "What’s in this image?"
#                     },
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     }
#                 ]
#             }
#         ],
#         "max_tokens": 300
#     }
#     response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
#     return response.json()

# def create_thread_and_run(image_path):
#     """
#     Cria um novo thread e submete uma imagem para análise.
#     """
#     thread = client.beta.threads.create()
#     response = submit_image(ENEL_ASSISTANT_ID, thread, image_path)
#     return thread, response

# # Exemplo de uso com imagem
# thread1, response1 = create_thread_and_run(r"C:\Users\KAIQUEHENRIQUEVALIM\Documents\GitHub\home-work\enel-poc-llm-identifier\Photos-001\poste 1.jpg")

# print(response1)


import openai
def create_thread(ass_id,prompt):

    #create a thread
    thread = openai.beta.threads.create()
    my_thread_id = thread.id


    #create a message
    message = openai.beta.threads.messages.create(
        thread_id=my_thread_id,
        role="user",
        content=prompt
    )

    #run
    run = openai.beta.threads.runs.create(
        thread_id=my_thread_id,
        assistant_id=ass_id,
    ) 

    return run.id, thread.id


def check_status(run_id,thread_id):
    run = openai.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id,
    )
    return run.status


base64_image = encode_image(r"C:\Users\KAIQUEHENRIQUEVALIM\Documents\GitHub\home-work\enel-poc-llm-identifier\Photos-001\poste 8.jpg")
my_run_id, my_thread_id = create_thread(ENEL_ASSISTANT_ID,base64_image)

status = check_status(my_run_id,my_thread_id)

while (status != "completed"):
    status = check_status(my_run_id,my_thread_id)
    time.sleep(2)


response = openai.beta.threads.messages.list(
  thread_id=my_thread_id
)


if response.data:
    print(response.data[0].content[0].text.value)