
# coding: utf-8

# - このコードは、ストリーミングで動作することを目的としているため、ジェネレータやクセの強いライブラリが多用されており、読みづらくなっています。
# - [非ストリーミング音声認識](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/speech/cloud-client)(transcribe.pyなど)や、[感情推定のソースコード](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/language/sentiment)に目を通してから読むことをお勧めします。

# In[ ]:





# In[ ]:


from __future__ import division

import re
import json
import sys
import argparse

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import googleapiclient.discovery

import pyaudio
from six.moves import queue


# In[ ]:


# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "C:/Users/USER02/Documents/Voice2Text.json"


# ### 🐍感情推定用の関数を定義
# - get_native_encoding_type()は、利用しているpythonの文字列のタイプがutf-16かutf-32かを返す
# - analyze_sentimentは、テキストを引数として渡すと感情認識の結果（辞書型）を返す

# In[ ]:


def get_native_encoding_type():
    """Returns the encoding type that matches Python's native strings."""
    if sys.maxunicode == 65535:
        return 'UTF16'
    else:
        return 'UTF32'
    


def analyze_sentiment(text, encoding='utf-8'):
    body = {
        'document': {
            'type': 'PLAIN_TEXT',
            'content': text,
        },
        'encoding_type': encoding
    }

    service = googleapiclient.discovery.build('language', 'v1')

    request = service.documents().analyzeSentiment(body=body)
    response = request.execute()

    return response


# ### 🐍Pyaudioを用いてマイクから音声を取得する

# In[ ]:


class MicrophoneStream(object):
    """
    Opens a recording stream as a generator yielding the audio chunks.
    音声のチャンクをyieldする録音のストリームをオープンする（？？？）
    """
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        # オーディオデータの「スレッドセーフバッファ」？？？を作成する。
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            
            # このAPIは、現在のところモノラル音声にしか対応してない。
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            
            # オーディオストリームを、バッファを埋めるために非同期で動かそう。
            # これは、呼び出しているスレッドがネットワークにリクエストをしている間などであっても
            # 入力デバイスのバッファがオーバーフロウを起こさないようにするため、必要である。
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        # ジェネレータに終了の信号を伝える。
        # じゃないと、ストリーミング認識のメソッドが、プロセスの終了を阻害してしまう。
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            # （日訳）get()を用いて、少なくともデータが1チャンク以上あるかを確認してください。
            # データのチャンク数がNoneを示すとき、音声ストリームは終了しています。
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            # （日訳）？？？
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            # b''は、バイト型で文字列を送信するという記号
            yield b''.join(data)


# ### 🐍マイクから音声を取得し、サーバに送信する処理を繰り返す関数

# In[ ]:


def listen_print_loop(responses, sentiment):
    
    """
    Iterates through server responses and prints them.
    # サーバの応答を繰り返して、それらを印刷します。

    The responses passed is a generator that will block until a response
    is provided by the server.
    渡される応答は、応答があるまでブロックされるジェネレータです。
    サーバーによって提供されます。

    """
    
    num_chars_printed = 0
    
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        
        # 'sesults'のリストは、連続している(おそらく、たくさんの要素が含まれるということ)
        # ストリーミング認識の場合は、最初の結果のみ考慮する。
        # なぜなら、いったん'is_final'になったら、次の発話の処理に移るからである。
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        # トップの代替案を表示する
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        
        # 暫定の結果を表示する。ただし、行末にキャリッジリターン？？？があるので
        # 後続の行はこれらを上書きします。
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        
        # もし一個前の結果が今回のものよりも長かったら、我々は追加のスペースを
        # 前回の結果を上書きするために追加しなければならない。
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print_str = transcript + overwrite_chars
            
            if sentiment:
                
                mag, score = analyze_sentiment(transcript + overwrite_chars, get_native_encoding_type())['documentSentiment'].values()
                print_str += '\n感情の正負:{} 感情の強さ:{}\n'.format(score, mag)
                
            yield print_str
            

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            
            # 転記されたフレーズのいずれかがGoogleのキーワードの1つになる可能性がある場合は
            # 認識を終了してください。
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break

            num_chars_printed = 0


# ### 🐍メイン関数
# - 言語コード（[詳細](https://cloud.google.com/speech-to-text/docs/languages)）と、感情推定するか否を引数にとる
# - これ呼び出すべし

# In[ ]:


def mic_recog(lang='ja-JP', sentiment=False):
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = lang  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)
        
        loopitr = listen_print_loop(responses, sentiment)
        
        try:
            while True:
                # Now, put the transcription responses to use.
                print(next(loopitr))
        except KeyboardInterrupt:
            print('\n🌸🌸🌸Interrupted!!!🌸🌸🌸')
            return 0
        except :
            return -1


# ### 🐍実行部分
# - main（言語コード, 感情推定OnOff）
# - もし65秒のタイムアウトで中断してしまった場合は、もう一度実行するように無限ループ

# In[ ]:


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-lang', help='Language code ex.en-US, zh, etc...(default:ja-JP)', default='ja-JP')
    parser.add_argument(
        '-sentiment', help='If you want to analyze sentiment, enter "True"', default=False)
    args = parser.parse_args()

    while True:
        result = mic_recog(args.lang, args.sentiment)
        if result == 0:
            break


