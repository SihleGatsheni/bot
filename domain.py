from langchain.prompts import PromptTemplate
from bedrock_ai import BedrockAI
from s3_storage import S3Storage
import os
import aiofiles
import asyncio
import json
from config import  software_design_diagram_code_prompt_template_test, software_design_requirements_prompt_template, software_design_diagram_dot_language, modify_code_prompt


bedrock_ai = BedrockAI()
storage = S3Storage()
class Domain:
    def __init__(self) -> None:
        pass
    
    async def generate_software_requirements_prompt(self,user_summary):
        prompt = PromptTemplate(template=software_design_requirements_prompt_template, input_variables=['user_summary'])
        summary = json.loads(user_summary)
        if summary.get('img'):
            print("processing image")
            text = await bedrock_ai.send_image(summary.get('img'))
            img = 1
            print("Done Processing Image...")
        else:
            text = summary.get('text') 
            print(f"User Summary:-> ",text)
            img = -1
        prompt_formatted_str = prompt.format(user_summary=text)
        generated_output =await bedrock_ai.inference(prompt_formatted_str)
        return generated_output, img

    async def generate_dot_language(self,generated_design_requirement):
        prompt = PromptTemplate(template=software_design_diagram_dot_language, input_variables=['generated_design_requirement'])
        prompt_formatted_str = prompt.format(generated_design_requirement=generated_design_requirement)
        generated_dot_output =await bedrock_ai.inference(prompt_formatted_str)
        generated_dot_code = generated_dot_output.replace("dot", "")
        generated_dot_code = generated_dot_code.replace("```", "")
        return generated_dot_output

    async def generate_diagram_code_prompt(self,generated_dot_diagram, output_template):
        prompt = PromptTemplate(template=software_design_diagram_code_prompt_template_test, input_variables=['generated_dot_diagram', 'output_template'])
        prompt_formatted_str = prompt.format(generated_dot_diagram=generated_dot_diagram, output_template=output_template)
        generated_diagram_code =await bedrock_ai.inference(prompt_formatted_str)
        generated_diagram_code = generated_diagram_code.replace("python", "")
        generated_diagram_code = generated_diagram_code.replace("```", "")
        return generated_diagram_code

    async def modify_code(self,code, error_message):
        prompt = PromptTemplate(template=modify_code_prompt, input_variables=['code', 'error_message'])
        prompt_formatted_str = prompt.format(code=code, error_message=error_message)
        generated_diagram_code =await bedrock_ai.inference(prompt_formatted_str)
        generated_diagram_code = generated_diagram_code.replace("python", "")
        generated_diagram_code = generated_diagram_code.replace("```", "")
        return generated_diagram_code

    async def execute_generated_python_diagram_code(self,code, user_id:str):
        try:
            temp_code_file_path = f"{user_id}_ai_generated_diagram_code.py"
            async with aiofiles.open(temp_code_file_path, "w") as temp_code_file:
                await temp_code_file.write(code)
                
            result = await asyncio.create_subprocess_exec( 
                'python3', temp_code_file_path,
                 stdout= asyncio.subprocess.PIPE,
                 stderr=asyncio.subprocess.PIPE
            )
            
            
            stdout, stderr = await result.communicate()
            stdout = stdout.decode().strip()
            stderr = stderr.decode().strip()
            statuscode = None
            if result.returncode == 0:
                statuscode = result.returncode
                await storage.write_file(user_id=user_id,file_path='static/gpt_generated_diagram.png')
            else:
                stderr_output = stderr.decode().strip()
                print(stderr_output)
        except Exception as e:
            output = f"An unexpected error occurred: {e}"
            status = "incorrect"
        finally:
             if os.path.exists(temp_code_file_path):
                os.remove(temp_code_file_path)
        return statuscode
