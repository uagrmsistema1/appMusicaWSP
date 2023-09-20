# Third-party imports
import json
import openai
import streamlit as st
import requests
from dotenv import load_dotenv
import os
import time
from fastapi import FastAPI, Form, Depends
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Internal imports
from models import Conversation, SessionLocal
from utils import send_message, logger


app = FastAPI()
# Set up the OpenAI API client
openai.api_key = config("OPENAI_API_KEY")
whatsapp_number = config("TO_NUMBER")

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

#d-id
def generate_video(prompt, avatar_url, gender):
    url = "https://api.d-id.com/talks"
    headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Basic ZDJsdVpHUnlZVzVuWlhKcWFHOXlaR0Z1UUdkdFlXbHNMbU52YlE6VmF4bHNGWG5Qa1UtSnZ0VVU0eVgzOmQybHVaR1J5WVc1blpYSnFhRzl5WkdGdVFHZHRZV2xzTG1OdmJROlZheGxzRlhuUGtVLUp2dFVVNHlYMw=="
}
    if gender == "Female":
        payload = {
            "script": {
                "type": "text",
                "subtitles": "false",
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-ChristopherNeural"
                },
                "ssml": "false",
                "input":prompt
            },
            "config": {
                "fluent": "false",
                "pad_audio": "0.0"
            },
            "source_url": "https://clips-presenters.d-id.com/matt/9C51DD6lgH/mBHOFBuOHq/image.png"
        }

    if gender == "Male":
        payload = {
            "script": {
                "type": "text",
                "subtitles": "false",
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-ChristopherNeural"
                },
                "ssml": "false",
                "input":prompt
            },
            "config": {
                "fluent": "false",
                "pad_audio": "0.0"
            },
            "source_url": "https://clips-presenters.d-id.com/matt/9C51DD6lgH/mBHOFBuOHq/image.png"
        }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print(response.text)
            res = response.json()
            id = res["id"]
            status = "created"
            while status == "created":
                getresponse =  requests.get(f"{url}/{id}", headers=headers)
                print(getresponse)
                if getresponse.status_code == 200:
                    status = res["status"]
                    res = getresponse.json()
                    print(res)
                    if res["status"] == "done":
                        video_url =  res["result_url"]
                    else:
                        time.sleep(10)
                else:
                    status = "error"
                    video_url = "error"
        else:
            video_url = "error"   
    except Exception as e:
        print(e)      
        video_url = e      
        
    return video_url

#musica
def search_music(querymusic):
    headers = {
        'Accept': 'application/json'
    }


    url = 'https://audius-discovery-2.theblueprint.xyz/v1/tracks/search'

    params = {
        'query': querymusic,
        'app_name': 'EXAMPLEAPP'
    }

    music_list = []

    response = requests.get(url, params=params, headers=headers)
    musics=""
# Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        data = response.json()
        
        # Itera sobre las pistas encontradas
        for track in data.get('data', []):
            music_dict = {
            'id': track.get('id', 'Id no disponible'),
            'stream_url': f"https://audius-discovery-2.theblueprint.xyz/v1/tracks/{track.get('id', 'Id no disponible')}/stream",
            'title': track.get('title', 'Título no disponible'),
            'artist': track.get('user', {}).get('name', 'Artista no disponible')
        }
            # print(music_dict)
            music_list.append(music_dict)
        # for track in data.get('data', []):
        #     musics = musics + " " + track.get('id', 'Id no disponible')
        #     musics = musics + " " + "https://audius-discovery-2.theblueprint.xyz/v1/tracks/"+track.get('id', 'Id no disponible')+"/stream"
        #     musics = musics + " " + track.get('title', 'Título no disponible')
        #     musics = musics + " " + track.get('user', {}).get('name', 'Artista no disponible')+ "\n"
            #la linea de aqui devuelve un enlace para la pagina donde esta el audio, no devuelve el enlace para hacer stream
            # musics = musics + " " + "https://audius.co"+track.get('permalink', 'URL no disponible') + "\n"
            # print(f"Nombre de la pista: {title}")
            # print(f"Artista: {artist}")
            # print(f"Enlace para descargar: {url}")
            # print("\n")
    else:
        print(f"Error al buscar música. Código de estado: {response.status_code}")

    
    return music_list


@app.post("/message")
async def reply(Body: str = Form(), db: Session = Depends(get_db)):
    #Descomentar codigo para que funcione chatgpt
    # # Call the OpenAI API to generate text with GPT-3.5
    # response = openai.Completion.create(
    #     engine="text-davinci-002",
    #     prompt=Body,
    #     max_tokens=200,
    #     n=1,
    #     stop=None,
    #     temperature=0.5,
    # )

#Descomentar codigo para que funcione lo de crear video con lo que responde el chat
    # # The generated text
    # chat_response = response.choices[0].text.strip()
    # avatar_url="https://www.thesun.co.uk/wp-content/uploads/2021/10/2394f46a-c64f-4019-80bd-445dacda2880.jpg?w=670"
    # avatar_selection="Male"
    # videourl=generate_video(chat_response, avatar_url, avatar_selection)
    # print(videourl)

    # try:
    #         videourl=generate_video(chat_response, avatar_url, avatar_selection)  # Call your video generation function here
    #         if videourl!= "error":
    #            videourl=videourl
    #         else:
    #             videourl=("Sorry... Try again")
    # except Exception as e:
    #         print(e)
    #         videourl=generate_video(chat_response, avatar_url, avatar_selection)

    query = Body
    music = search_music(query)
    musics = ""
    # for track in music:
    #     musicM=musicM+ " "+track["title"] + " "+ track["artist"] + " " + track["url"] +"\n"
    info = ""
    longitud_maxima = 1600
    # Store the conversation in the database
    # try:
    #     conversation = Conversation(
    #         sender=whatsapp_number,
    #         message=Body,
    #         response=videourl
    #         )
    #     db.add(conversation)
    #     db.commit()
    #     logger.info(f"Conversation #{conversation.id} stored in database")
    # except SQLAlchemyError as e:
    #     db.rollback()
    #     logger.error(f"Error storing conversation in database: {e}")
    # print(f"print {videourl}")
    # print(music)
    # for musicitem in music:
    #     musics = musics + " " + f"ID: {musicitem['id']}"
    #     musics = musics + " " + f"Título: {musicitem['title']}"
    #     musics = musics + " " + f"Artista: {musicitem['artist']}"
    #     musics = musics + " " + f"URL de transmisión: {musicitem['stream_url']}"+"\n" 
    print(music)
    for musicitem in music:
    # Crear una cadena que representa la información del elemento actual
        info = info + " " + f"ID: {musicitem['id']}"
        info = info + " " + f"Título: {musicitem['title']}"
        info = info + " " + f"Artista: {musicitem['artist']}"
        info = info + " " + f"URL de transmisión: {musicitem['stream_url']}"+"\n" 
   
    # Verificar si agregar la información actual superaría la longitud máxima
        if len(musics) + len(info) <  longitud_maxima:
        # Si agregarlo superaría la longitud máxima, rompe el bucle para evitar excederla
           musics=info 
    # Si no supera la longitud máxima, agrega la información al resultado
             
        # send_message(whatsapp_number,musics,musicitem['stream_url'])
        

    # print(musics)
 # for track in data.get('data', []):
        #     musics = musics + " " + track.get('id', 'Id no disponible')
        #     musics = musics + " " + "https://audius-discovery-2.theblueprint.xyz/v1/tracks/"+track.get('id', 'Id no disponible')+"/stream"
        #     musics = musics + " " + track.get('title', 'Título no disponible')
        #     musics = musics + " " + track.get('user', {}).get('name', 'Artista no disponible')+ "\n"

    send_message(whatsapp_number,musics)
    return ""
