import whisper
import os
import torch
import warnings

warnings.filterwarnings("ignore")

class WhisperTranscriber:
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None

    def load_model(self):
        if self.model is None:
            import imageio_ffmpeg
            import shutil
            
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            ffmpeg_dir = os.path.dirname(ffmpeg_exe)
            ffmpeg_alias = os.path.join(ffmpeg_dir, "ffmpeg.exe")
            
            if not os.path.exists(ffmpeg_alias):
                shutil.copy(ffmpeg_exe, ffmpeg_alias)
                
            if ffmpeg_dir not in os.environ["PATH"]:
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
            
            self.model = whisper.load_model(self.model_size, device=self.device)

    def transcribe(self, audio_path: str) -> str:
        self.load_model()
        result = self.model.transcribe(audio_path)
        return result["text"].strip()
