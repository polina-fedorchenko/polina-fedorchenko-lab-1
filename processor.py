"""Signal processing module: threshold-based trimming of silence."""

import logging
import numpy as np
logger = logging.getLogger(__name__)


class ProcessorError(Exception):
    """Raised when audio processing fails."""


class AudioProcessor:
    """Threshold-based audio processor.
    Args:
        threshold: Amplitude threshold in range (0, 1).
    Raises:
        ValueError: If threshold is outside of (0, 1).
    """

    def __init__(self, threshold: float = 0.01) -> None:
        if not 0 < threshold < 1:
            raise ValueError(f"Threshold must be in range (0, 1), got {threshold}")
        self.threshold = threshold

    def trim_silence(self, audio_data: np.ndarray) -> np.ndarray:
        """Trim the beginning and the end of a recording using a threshold.
        Args:
            audio_data: Audio samples (samples x channels or 1D).
        Returns:
            np.ndarray: Trimmed audio. If no sample exceeds the threshold,
            the original data is returned unchanged.
        Raises:
            ProcessorError: If the input is empty.
        """
        if audio_data is None or audio_data.size == 0:
            raise ProcessorError("Cannot process empty audio data.")

        amplitude = np.abs(audio_data)
        if amplitude.ndim > 1:
            amplitude = amplitude.max(axis=1)

        above_threshold = np.where(amplitude > self.threshold)[0]

        if above_threshold.size == 0:
            logger.warning("No signal above the threshold %.4f.", self.threshold)
            return audio_data

        start_idx = int(above_threshold[0])
        end_idx = int(above_threshold[-1]) + 1
        trimmed = audio_data[start_idx:end_idx]

        logger.info(
            "Audio trimmed. Samples: %d -> %d (start=%d, end=%d)",
            len(audio_data), len(trimmed), start_idx, end_idx,
        )
        return trimmed