from urllib.parse import urlparse
import pandas as pd
import os
from fastapi import FastAPI,WebSocket,WebSocketDisconnect,WebSocketException
from starlette.middleware.cors import CORSMiddleware
from typing import Dict
from s3_storage import S3Storage
from code_cleaner import Clean
from domain import Domain
from config import  output_template
from socket_manager import SocketConnectionManager

app = FastAPI()

#cors setup
origins =["*"]
app.add_middleware(
     CORSMiddleware,
     allow_origins=origins,
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
)
storage = S3Storage()
domain = Domain()
connection_manager = SocketConnectionManager()
clients:Dict[str, WebSocket]={}
df = pd.DataFrame(columns=['user_input', 'generated_software_details', 'generated_diagram_code', 'status'])

def append_dict_to_df(df, dict_to_append):
    df = pd.concat([df, pd.DataFrame.from_records([dict_to_append])])
    return df

@app.get('/')
async def health():
    server_url = os.environ.get('SERVER_URL')
    if not server_url:
        server_url = 'http://localhost:8000'
    
    parsed_url = urlparse(server_url)
    hostname = parsed_url.hostname
    port = parsed_url.port or 80 

    return {
        "server": "active",
        "status": "200",
        "url": f"{hostname}:{port}",
    }
    

@app.websocket('/ws/{client_id}')
async def websocket_endpoint(websocket:WebSocket,client_id:str):
    await connection_manager.connect(websocket=websocket, client_id=client_id)
    try:
        greeting_message = (
            "Hello! 👋\n\n"
            "I’m an AI Architect, powered by Cloudza. 🌟 I’m here to assist you in converting your technical specifications into AWS infrastructure.\n\n"
            "Feel free to explore our services and learn more about how we can help you at our website:  <a href='https://cloudza.io/' target='_blank' rel='noopener noreferrer'>www://cloudza.io</a>.\n\n"
            "Let’s get started on your infrastructure journey! 🚀\n\n"
            "Describe your software specifications and how you would like it to be deployed"
        )
    
        await connection_manager.send_message_json(client_id,{"text":greeting_message, "completed":False, "greet":True})
        while True:
            user_summary = await connection_manager.receive_message(client_id=client_id)
            
            if not user_summary:
                break
            # Step 1: Generate Software Requirements Prompt
            generated_design_requirement, img = await domain.generate_software_requirements_prompt(user_summary)
            if img ==1: 
                await connection_manager.send_message_json(client_id,{"text":generated_design_requirement, "completed":True,"greet":False})
                print('software specifications from image generated')
            else:
                await connection_manager.send_message_json(client_id,{"text":generated_design_requirement,"completed":False,"greet":False})
                print('software specifications from text prompt generated')
                generated_dot_diagram = await domain.generate_dot_language(generated_design_requirement)
                
                # Step 2: Generate Diagram Code Prompt
                while True:
                    generated_diagram_code = await domain.generate_diagram_code_prompt(generated_dot_diagram, output_template)
                    clean_code = await Clean().clean_in_place(generated_diagram_code)
                    statuscode = await domain.execute_generated_python_diagram_code(clean_code,client_id)
                    if statuscode == 0:
                        print('processing done')
                        break
                await connection_manager.send_message_json(client_id,{'img':await storage.read(client_id), "completed":True,"greet":False})
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
        print(f"Client  with id:{client_id} disconnected")
    except WebSocketException as e:
        await connection_manager.send_message(client_id,f'Unable to communicate with server becuase of the following error: {str(e)} I will close connection bye!!')
        await connection_manager.close()

async def reconnect(websocket:WebSocket,client_id:str):
        socket = connection_manager.active_connections(client_id)
        if socket not in connection_manager.active_connections():
            await connection_manager.connect(websocket, client_id)