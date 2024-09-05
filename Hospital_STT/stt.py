import os, pathlib
import time

# Making TTS -> needs internet
import speech_recognition as sr
import pygame
import pyaudio
from gtts import gTTS
from pydub import AudioSegment
import subprocess


# Making Wav2Vec
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from datasets import load_dataset


freq = 16000    # sampling rate, 44100(CD), 16000(Naver TTS), 24000(google TTS)
bitsize = -16   # signed 16 bit. support 8,-8,16,-16
channels = 1    # 1 is mono, 2 is stereo
buffer = 2048   # number of samples (experiment to get right sound)

class SR_Hospital_Util:

    def Make_Dir(file_name):
        try:
            os.mkdir(file_name)
            return True
        except:
            return False

class SR_Hospital:

    # Set default path
    stt_path = pathlib.Path(__file__).parent.absolute()

    def __init__(self):
        '''
        Description [Setting Speech recognition & tts model]
        Output
        [
            Speech recognition 
            - recognition model [rec]
            - microphone device [mic]

            Wav2Vec model
            - processor [ps]
            - Wav2Vec model [model]
            - dataset [ds]
        ]
        '''

        rec, mic = SR_Hospital.Construct_Voice_Model(SR_Hospital.Init_System_Check())
        ps, model, ds = SR_Hospital.Construct_Wav2Vec_Model()

        gTTS(text="1", lang="ko", slow=False).save(os.path.join(SR_Hospital.stt_path,"empty.mp3"))

        # Call the first centence
        input_text = '한국대학교병원이죠'
        SR_Hospital.Make_Audio_Source_File('Input_Audioes', input_text)
        mk_source_file_path = os.path.join(SR_Hospital.stt_path, 'Input_Audioes')

        while True:
            with sr.AudioFile( os.path.join(mk_source_file_path, input_text.replace(' ','')+ '.wav')) as source:
                audio = rec.record(source)

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
                if (SR_Hospital.Speak("{} 말씀이신가요".format(data)) ):
                    time.sleep(0.2)

                    text = '네 예약좀 하려고 하는데요'
                    SR_Hospital.Make_Audio_Source_File('Input_Audioes', text)

                    with sr.AudioFile(os.path.join(mk_source_file_path, text.replace(' ','')+'.wav')) as source:
                        audio = rec.record(source)

                        data = rec.recognize_google(audio, language="ko-KR")

                        if ('예약' in data.split(' ')):
                            time.sleep(0.2)
                            SR_Hospital.Speak("네 고객님 그러면 어떻게 도와드리면 될까요")
                    
            except:
                SR_Hospital.Speak("다시 한번 말씀해주세요")
                return

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

    def Speak(text, lang="ko", speed=False, wavformat=False, path=""):
        '''
        Speech specific text
        '''

        file_path = os.path.join(path, text.replace(" ","")) + ".mp3"

        tts = gTTS(text=text, lang=lang , slow=speed)
        tts.save(file_path)
        pygame.mixer.init(freq, bitsize, channels, buffer)
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        # Check the file and remove
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.load(os.path.join(SR_Hospital.stt_path,"empty.mp3"))

        '''
        Require pydub, ffmpeg-downloader
        - ffdl install --add-path
        '''
        if(wavformat):
            src = r"{}".format(file_path.replace('\\\\', '\\'))
            sound = AudioSegment.from_mp3(src)
            sound.export(file_path.replace('mp3', 'wav'), format="wav")

        os.remove(file_path)
        return True
            
    
    def Make_Audio_Source_File(pathes, text):
        '''
        Make Audio input file with text

        Input
        - the file path [pathes]
         - Do not use special character
        - the text what we want to speech [text]
        '''
        path = os.path.join(SR_Hospital.stt_path, pathes)

        if(pathes not in os.listdir(SR_Hospital.stt_path)):
            SR_Hospital_Util.Make_Dir(path)
        
        SR_Hospital.Speak(text, path=path, wavformat=True)
        
        
    def Recognize_Voice_Wav2Vec(ps, model, ds, data):
        print("hi")

if __name__ == "__main__":
    SR_Hospital()