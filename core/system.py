import asyncio


async def execute(command: str) -> str:
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        return str(stdout.decode()).strip()
    else:
        raise Exception(str(stderr.decode()).strip())
