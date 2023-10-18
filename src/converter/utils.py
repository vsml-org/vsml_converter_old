import ffmpeg

origin_transparent_process = None


def get_transparent_process(resolution_text: str):
    global origin_transparent_process
    if origin_transparent_process is None:
        origin_transparent_process = ffmpeg.input(
            f"rgbtestsrc=s={resolution_text}", f="lavfi"
        ).filter("geq", a=0, r=0, g=0, b=0)
    transparent_process = origin_transparent_process.split()
    origin_transparent_process = transparent_process[1]
    return transparent_process[0]
