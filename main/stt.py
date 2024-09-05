import speech_recognition as sr
import os

# Making TTS -> needs internet
import pygame
import pyaudio
from gtts import gTTS

# Making Wav2Vec
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from datasets import load_dataset


freq = 16000    # sampling rate, 44100(CD), 16000(Naver TTS), 24000(google TTS)
bitsize = -16   # signed 16 bit. support 8,-8,16,-16
channels = 1    # 1 is mono, 2 is stereo
buffer = 2048   # number of samples (experiment to get right sound)

class SR_Hospital:

    def __init__(self):
        rec, mic = SR_Hospital.Construct_Voice_Model(SR_Hospital.Init_System_Check())
        ps, model, ds = SR_Hospital.Construct_Wav2Vec_Model()

        gTTS(text="1", lang="ko", slow=False).save("./empty.mp3")

        while True:    
            with sr.AudioFile('건국대학교병원.wav') as source:
                audio = rec.record(source)
                data = rec.recognize_google(audio, language="ko-KR")
                SR_Hospital.Speak("{}_말씀이신가요?".format(data))
                return

            '''
            Temporarily disabled 
            with mic as source:
                print("Listening...")
                audio = rec.listen(source)
            '''

            try:
#                inputs = ps(ps, sampling_rate=16000, return_tensors="pt", padding="longest")
#                input_values = inputs.input_values.to("cpu")
                data = rec.recognize_google(audio, language="ko-KR")

#                logits = model(input_values).logits[0]
#                print("{} versus {}".format(input_values, data))
                #SR_Hospital.Recognize_Voice_Wav2Vec(ps, model, ds, data)
                SR_Hospital.Speak("{} 말씀이신가요?".format(data))
            except:
                SR_Hospital.Speak("다시 한번 말씀해주세요")

    def Init_System_Check():
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        find_device = '마이크(Realtek(R) Audio)'
        

        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                #print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

                # If you not use airpods, change it to another one
                if (find_device in p.get_device_info_by_host_api_device_index(0, i).get('name')):
                    return i
                    break
                

    def Construct_Voice_Model(indexes):
        return sr.Recognizer(), sr.Microphone(device_index=indexes)
    
    def Construct_Wav2Vec_Model():
        return Wav2Vec2Processor.from_pretrained("kresnik/wav2vec2-large-xlsr-korean"), Wav2Vec2ForCTC.from_pretrained("kresnik/wav2vec2-large-xlsr-korean"), load_dataset("bingsu/zeroth-korean")

    def Speak(text ,lang="ko", speed=False):
        '''
        해당 단어 출력
        '''
        tts = gTTS(text=text, lang=lang , slow=speed)
        tts.save("./"+text+".mp3")
        pygame.mixer.init(freq, bitsize, channels, buffer)
        pygame.mixer.music.load("./"+text+".mp3")
        pygame.mixer.music.play()

        # Check the file and remove
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.load("./empty.mp3")
        os.remove("./"+text+".mp3")
        
    def Recognize_Voice_Wav2Vec(ps, model, ds, data):
        print("hi")

if __name__ == "__main__":
    SR_Hospital()