from app.io.io import Reader, Writer
from app.tts import TTS


class TTSManager():
    def __init__(self, tts: TTS, inputer: Reader, outputer: Writer) -> None:
        self.tts = tts
        self.inputer = inputer
        self.outputer = outputer
        pass

    def start(self):
        self.inputer.configure()
        self.outputer.configure(self.tts.config.sample_rate)
        self.tts.configure()

        for (sample, speaker) in self.inputer.read():
            audio = self.tts.do_tts(
                sample, speaker
            )
            self.outputer.write(audio)

        self.inputer.close()
        self.outputer.close()
    pass
