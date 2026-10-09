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
            
            import tempfile
            
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            # Create a writable temporary directory to hold our ffmpeg alias
            temp_bin_dir = os.path.join(tempfile.gettempdir(), "ffmpeg_bin")
            os.makedirs(temp_bin_dir, exist_ok=True)
            
            # Windows requires .exe, Linux just needs 'ffmpeg'
            alias_name = "ffmpeg.exe" if os.name == 'nt' else "ffmpeg"
            ffmpeg_alias = os.path.join(temp_bin_dir, alias_name)
            
            if not os.path.exists(ffmpeg_alias):
                shutil.copy(ffmpeg_exe, ffmpeg_alias)
                # Ensure it has execute permissions on Linux
                if os.name != 'nt':
                    os.chmod(ffmpeg_alias, 0o755)
                
            if temp_bin_dir not in os.environ["PATH"]:
                os.environ["PATH"] = temp_bin_dir + os.pathsep + os.environ["PATH"]
            
            self.model = whisper.load_model(self.model_size, device=self.device)

    def transcribe(self, audio_path: str) -> str:
        self.load_model()
        result = self.model.transcribe(audio_path)
        return result["text"].strip()
