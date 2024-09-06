import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from  io import BytesIO
import aiofiles
class S3Storage:
    def __init__(self) -> None:
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'diagrams-bucket2024'
        self.prefix = 'code/'
        
    async def write(self,image,file_path):
        prefixed_path = f'{self.prefix}{file_path}'
        await self.s3_client.upload_fileobj(BytesIO(image), self.bucket_name,prefixed_path)
    
    async def read(self,user_id:str):
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': f'{self.prefix}{user_id}.png'},
                ExpiresIn=259200)
            return response
        except Exception as e:
            print(str(e))
    async def write_file(self,user_id, file_path):
        try:
            async with aiofiles.open(file_path, 'rb') as file:
                file_data = await file.read()
                await self.s3_client.put_object(Bucket=self.bucket_name, Key=f'{self.prefix}{user_id}.png', Body=file_data)
                
        except FileNotFoundError:
            print(f"The file {file_path} was not found")
        except NoCredentialsError:
            print("Credentials not available")
        except PartialCredentialsError:
            print("Incomplete credentials provided")
        except Exception as e:
            print(f"An error occurred: {str(e)}")