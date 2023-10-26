import ffmpeg

origin_transparent_processes = {}


def get_transparent_process(
    resolution_text: str,
):
    global origin_transparent_process
    origin_transparent_process = origin_transparent_processes.get(
        resolution_text
    )
    if origin_transparent_process is None:
        origin_transparent_process = ffmpeg.input(
            "rgbtestsrc=s={}".format(resolution_text),
            f="lavfi",
        ).filter("geq", a=0, r=0, g=0, b=0)
    transparent_processes = origin_transparent_process.sprit()
    origin_transparent_processes[resolution_text] = transparent_processes[1]
    return transparent_processes[0]
