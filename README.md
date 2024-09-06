
### Architecture Generation Bot

## Prerequisite
1. python 3
2. graphviz (sudo apt update && sudo apt install graphviz)


## How to run the api
1. pip install -r requirements.txt
2. fastapi dev server.py / ./start.sh


## Frontend Integration

# Inputs
for text prompt
sendMessage({
    text:string
})

for image prompt
sendMessage({
    img:byte[]
})



# Outputs
1. for text result:
    sends json to frontend with {
        text:str,
        completed:bool
        greet:bool
    }

2. for image result {
        img:byte[],
        completed:bool
        greet:bool
    }

