from anthropic import AnthropicBedrock
import asyncio
class BedrockAI:
   def __init__(self,model='anthropic.claude-3-5-sonnet-20240620-v1:0') -> None:
      self.model = model
      self.client = AnthropicBedrock() 
      self.MAX_TOKENS = 4096  
   async def inference(self,prompt):
      message = await asyncio.to_thread(self._inference,prompt)
      return  message.content[0].text
      
   def _inference(self,prompt):
      message = self.client.messages.create(
         model=self.model,
         max_tokens=self.MAX_TOKENS,
         messages=[{"role": "user", "content": prompt}]
      )
      return message
   
   def _send_image(self,image:str)-> str:
        base64_image = image
        response = self.client.messages.create(
         model=self.model,
         max_tokens=self.MAX_TOKENS,
         messages=[
                  {
                        "role": "user",
                        "content": [
                           {
                              "type": "image",
                              "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": self._extract_base64_data(base64_image)
                              }
                           },
                           {
                              "type": "text",
                              "text": "Explain this AWS architecture diagram."
                           }
                        ]
                  }
               ]
        )
        
        return response
   async def send_image(self,image:bytes):
      message = await asyncio.to_thread(self._send_image,image)
      return  message.content[0].text
   def _extract_base64_data(self,data_url):
      if data_url.startswith("data:image/png;base64,"):
         return data_url.split(",")[1]
      else:
         raise ValueError("Invalid data URL format")