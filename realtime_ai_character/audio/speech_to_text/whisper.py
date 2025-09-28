import io
import os
import subprocess
import types

import speech_recognition as sr
import whisper
from pydub import AudioSegment

from realtime_ai_character.audio.speech_to_text.base import SpeechToText
from realtime_ai_character.logger import get_logger
from realtime_ai_character.utils import Singleton, timed


logger = get_logger(__name__)

config = types.SimpleNamespace(
    **{
        "model": os.getenv("LOCAL_WHISPER_MODEL", "tiny"),  # 使用最小的模型
        "language": "en",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
)

# Whisper use a shorter version for language code. Provide a mapping to convert
# from the standard language code to the whisper language code.
WHISPER_LANGUAGE_CODE_MAPPING = {
    "en-US": "en",
    "es-ES": "es",
    "fr-FR": "fr",
    "de-DE": "de",
    "it-IT": "it",
    "pt-PT": "pt",
    "hi-IN": "hi",
    "pl-PL": "pl",
    "zh-CN": "zh",
    "ja-JP": "jp",
    "ko-KR": "ko",
}


class Whisper(Singleton, SpeechToText):
    def __init__(self, use="local"):
        super().__init__()
        if use == "local":
            try:
                subprocess.check_output(["nvidia-smi"])
                device = "cuda"
            except Exception:
                device = "cpu"
            logger.info(f"Loading [Local Whisper] model: [{config.model}]({device}) ...")
            self.model = whisper.load_model(config.model)
        self.recognizer = sr.Recognizer()
        self.use = use

    @timed
    def transcribe(self, audio_bytes, platform, prompt="", language="en-US", suppress_tokens=[-1]):
        logger.info("Transcribing audio...")
        if platform == "web":
            audio = self._convert_webm_to_wav(audio_bytes, self.use == "local")
        elif platform == "twilio":
            audio = self._ulaw_to_wav(audio_bytes, self.use == "local")
        else:
            audio = self._convert_bytes_to_wav(audio_bytes, self.use == "local")
        if self.use == "local":
            return self._transcribe(audio, prompt, suppress_tokens=suppress_tokens)
        elif self.use == "api":
            return self._transcribe_api(audio, prompt)

    def _transcribe(self, audio, prompt="", language="en-US", suppress_tokens=[-1]):
        language = WHISPER_LANGUAGE_CODE_MAPPING.get(language, config.language)
        
        # 预处理音频：限制长度和采样率
        import numpy as np
        import gc
        
        # 如果音频太长，截取前2秒（最小化内存使用）
        max_length = 2 * 16000  # 2秒，16kHz采样率
        if len(audio) > max_length:
            audio = audio[:max_length]
        
        # 确保音频是float32格式
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        
        # 归一化音频
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        
        # 添加内存清理
        gc.collect()
        
        try:
            logger.info(f"Starting Whisper transcription with audio shape: {audio.shape}")
            
            # 使用最简化的whisper设置
            result = self.model.transcribe(
                audio,
                language=language,
                fp16=False,  # 禁用半精度
                verbose=False,  # 减少输出
            )
            
            text = result["text"].strip()
            logger.info(f"Whisper transcription successful: '{text}'")
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            text = ""
        finally:
            # 清理内存
            del audio
            gc.collect()
        
        return text

    def _transcribe_api(self, audio, prompt=""):
        text = self.recognizer.recognize_whisper_api(
            audio,
            api_key=config.api_key,
        )
        return text

    def _convert_webm_to_wav(self, webm_data, local=True):
        import gc
        
        # 限制音频长度，减少内存使用
        webm_audio = AudioSegment.from_file(io.BytesIO(webm_data))
        
        # 如果音频太长，截取前5秒
        if len(webm_audio) > 5000:  # 5秒 = 5000毫秒
            webm_audio = webm_audio[:5000]
        
        # 降低采样率到16kHz，减少内存使用
        webm_audio = webm_audio.set_frame_rate(16000)
        
        wav_data = io.BytesIO()
        webm_audio.export(wav_data, format="wav")
        
        if local:
            # 对于标准 whisper，需要返回音频数据作为 numpy 数组
            wav_data.seek(0)
            import numpy as np
            import soundfile as sf
            audio_array, sample_rate = sf.read(wav_data)
            
            # 处理立体声音频 - 转换为单声道
            if len(audio_array.shape) > 1 and audio_array.shape[1] > 1:
                logger.info(f"Converting stereo to mono in webm conversion: {audio_array.shape}")
                audio_array = np.mean(audio_array, axis=1)
            
            # 清理临时数据
            del webm_audio, wav_data
            gc.collect()
            
            return audio_array
        
        with sr.AudioFile(wav_data) as source:
            audio = self.recognizer.record(source)
        return audio

    def _convert_bytes_to_wav(self, audio_bytes, local=True):
        if local:
            # 对于标准 whisper，需要返回音频数据作为 numpy 数组
            import numpy as np
            import soundfile as sf
            audio_data = sr.AudioData(audio_bytes, 44100, 2).get_wav_data()
            audio_array, sample_rate = sf.read(io.BytesIO(audio_data))
            return audio_array
        return sr.AudioData(audio_bytes, 44100, 2)

    def _ulaw_to_wav(self, audio_bytes, local=True):
        sound = AudioSegment(data=audio_bytes, sample_width=1, frame_rate=8000, channels=1)

        audio = io.BytesIO()
        sound.export(audio, format="wav")
        if local:
            # 对于标准 whisper，需要返回音频数据作为 numpy 数组
            import numpy as np
            import soundfile as sf
            audio.seek(0)
            audio_array, sample_rate = sf.read(audio)
            return audio_array

        return sr.AudioData(audio_bytes, 8000, 1)
