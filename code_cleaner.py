import aiofiles
class Clean:
    def __init__(self) -> None:
        pass
    async def delete_first_line(self,filename):
        async with  aiofiles.open(filename, 'r') as f:
            lines = await f.readlines()
            lines = lines[1:-1]
        async with aiofiles.open(filename, 'w') as f:
            await f.writelines(lines)
            
    async def clean_in_place(self, code):
        lines = code.splitlines()
        cleaned_lines = lines[1:-1]
        cleaned_code = '\n'.join(cleaned_lines)
        return cleaned_code