from app.io.io import Reader, Writer
from app.tts import TTS


class TTSManager():
    def __init__(self, tts: TTS, inputer: Reader, outputer: Writer) -> None:
        self.tts = tts
        self.inputer = inputer
        self.outputer = outputer
        pass

    def start(self) -> None:
        self.inputer.configure()
        self.outputer.configure(self.tts.config.sample_rate)
        self.tts.configure()
        print('All tts modules are ready')

        try:
            for sample, speaker in self.inputer.read():
                try:
                    audio = self.tts.do_tts(
                        sample, speaker
                    )
                except ValueError as e:
                    print('Wrong ssml syntax')
                    continue

                except AssertionError as e:
                    if "Invalid <prosody> tag" in str(e):
                        print('Wrong ssml syntax: invalid prosody tag')
                        continue
                    if "Empty <prosody> tag" in str(e):
                        print("Wrong ssml syntax: empty <prosody> tag")
                        continue
                    print('Unknown error')
                    print(e)
                    continue
                    # raise e

                self.outputer.write(audio)
        except KeyboardInterrupt:
            print('Exit by KeyboardInterrupt')
            pass

        self.inputer.close()
        self.outputer.close()
    pass
