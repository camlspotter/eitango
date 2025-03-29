import flet_audio

class Audio(flet_audio.Audio):
    def __init__(self, src : str):
        super().__init__(src)

    def play(self) -> None:
        # Dynamic web on Chrome requires this release() before play()      
        super().release() # type: ignore
        super().play() # type: ignore
