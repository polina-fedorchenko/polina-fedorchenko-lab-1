"""Audio engine module handling microphone recording and file persistence."""

import logging
import numpy as np
import sounddevice as sd
from pathlib import Path
from scipy.io.wavfile import write

from config import AudioConfig

logger = logging.getLogger(__name__)


class AudioEngineError(Exception):
    """Base exception for AudioEngine errors."""


class AudioRecordingError(AudioEngineError):
    """Raised when recording fails or is interrupted."""


class AudioSaveError(AudioEngineError):
    """Raised when saving audio data to disk fails."""


class AudioEngine:
    """High-level audio recording and persistence engine.

    Args:
        config: Configuration instance defining sampling rate, duration, and output target.
    """

    def __init__(self, config: AudioConfig) -> None:
        self.config = config

    def record(self) -> np.ndarray:
        """Record audio from the default system input device.

        Returns:
            np.ndarray: Recorded audio samples as a 2D numpy array (samples x channels).

        Raises:
            AudioRecordingError: If sounddevice fails to access mic or record.
        """
        num_samples = int(self.config.duration * self.config.sample_rate)

        logger.info(
            "Starting audio recording (%d seconds, %d Hz)...",
            self.config.duration,
            self.config.sample_rate,
        )

        try:
            audio_data: np.ndarray = sd.rec(
                frames=num_samples,
                samplerate=self.config.sample_rate,
                channels=1,
                dtype="float32",
            )
            sd.wait()

            logger.info("Recording completed successfully.")

            return audio_data
        except sd.PortAudioError as err:
            logger.error("Audio recording hardware error: %s", err)
            raise AudioRecordingError(f"Failed to record audio: {err}") from err
        except Exception as err:
            logger.error("Unexpected error during audio recording: %s", err)
            raise AudioRecordingError(f"Unexpected error during recording: {err}") from err

    def save(self, audio_data: np.ndarray, target_path: Path | None = None) -> Path:
        """Save recorded NumPy audio buffer to a WAV file.
        Args:
            audio_data: Numpy array containing audio sample data.
        Returns:
            Path: The resolved absolute file path where audio was written.
        Raises:
            AudioSaveError: If saving the WAV file to disk fails.
        """
        target_path = target_path or self.config.file_path

        try:
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info("Saving audio recording to %s...", target_path)
            write(target_path, self.config.sample_rate, audio_data)
            
            resolved_path = target_path.resolve()
            logger.info("Audio file successfully saved at: %s", resolved_path)

            return resolved_path
        except Exception as err:
            logger.error("Failed to write WAV file to %s: %s", target_path, err)
            raise AudioSaveError(f"Could not save file to {target_path}: {err}") from err