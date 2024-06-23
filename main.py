"""
-- Author:phil
-- Time: 2024/4/16 17:05  
-- Title: main.py
-- Software: PyCharm
# 1.先进行语音唤醒
    这里如何实现：
# 2.语音助手进行应答反馈
# 3.用户语音咨询，语音需要转为文本
# 4.文本告诉助手，助手调用许飞大模型
# 5.获取讯飞大模型的结果
# 6.文本转为语音反馈
"""
from Xufi_Voice import Run_Voice
import Spark_Model
import win32com.client
import pyaudio
import wave
from aip import AipSpeech
import os


class Wake_Up:

    def __init__(self,APP_ID,API_KEY,SECRET_KEY,file_path):
        self.APP_ID = APP_ID
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")  # window系统语音
        self.file_path = file_path

    def record_sound(self):
        # 获取语音 唤醒循环，只到获得唤醒词 "鸭蛋鸭蛋"或者 "鸭蛋"为止
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        RECORD_SECONDS = 5
        WAVE_OUTPUT_FILENAME = self.file_path
        pau = pyaudio.PyAudio()
        stream = pau.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK, )
        frames = []
        print("请说")
        # self.speaker.Speak("请说")
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("好的，等待您的吩咐")
        # self.speaker.Speak("好的，已经了解您的需求，请我思考一下")
        stream.stop_stream()
        stream.close()
        pau.terminate()
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pau.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def voice2text(self):
        # 语音转文本
        client = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        ret = client.asr(self.get_data(), 'pcm', 16000, {'dev_pid': 1536}, )
        # print(ret)
        if ret['err_msg'] == 'recognition error.':
            result = ''
            return result
        else:
            result = ret['result']
            return result

    def get_data(self):
        # 读取语音
        with open(self.file_path, 'rb') as fp:
            return fp.read()

    def del_file(self):

        file_name = self.file_path
        try:
            os.remove(file_name)
            print(f"Successful deleted {file_name}")
            f = open(file_name, mode="w")  # 音频-图片-视频  mode="wb"
            f.close()
            print(f"Successful maked {file_name}")

        except FileNotFoundError:
            print(f"{file_name} not found")


def Run_Talk(APP_ID,API_KEY,SECRET_KEY,file_path):

    output_pcm = './data/demo.pcm'
    output_wav = './data/demo.wav'
    # 实例化对象
    wk = Wake_Up(APP_ID,API_KEY,SECRET_KEY,file_path)

    while True:
        # 先调用录音函数
        wk.record_sound()
        # 语音转成文字的内容
        chat_message = wk.voice2text()
        print(chat_message)
        # if chat_message == '鸭蛋鸭蛋' or chat_message == '你好鸭蛋':
        if len(chat_message) > 0 and chat_message[0] == '今天':
            # 语音已唤醒
            wk.del_file()
            print('语音唤醒完毕')
            Run_Voice(output_pcm, output_wav, '我在，请问有何吩咐')
            # wk.speaker.Speak("我在，请问有何吩咐")
            print('我在，请问有何吩咐')
            wk.record_sound()
            # 唤醒后，需求调用
            chat_message = wk.voice2text()
            # wk.speaker.Speak('好的，请稍等')
            Run_Voice(output_pcm, output_wav, '好的，请稍等')
            print(chat_message)
            # 调用Spark_Xufi_Model
            if len(chat_message) > 0:
                Input = chat_message[0]
                output = Spark_Model.Api_Run(Input)
                print(output)
                # wk.speaker.Speak(output)
                Run_Voice(output_pcm, output_wav, output)
            break
        else:
            continue


if __name__ == '__main__':
    # 存放的文件名称
    file_path = "./data/chat-audio.wav"
    # 百度需要的参数
    APP_ID = '6******3'
    API_KEY = 'mNf******L8Ty'
    SECRET_KEY = '2******FxS'
    Run_Talk(APP_ID,API_KEY,SECRET_KEY,file_path)








