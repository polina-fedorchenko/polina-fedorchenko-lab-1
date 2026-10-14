"""Main application entry point for the Audio Recorder CLI tool."""

import logging
import sys
from enum import IntEnum

from audio_engine import AudioEngine, AudioEngineError
from cli import parse_args
from logger import setup_logging
from plotter import Plotter, PlotterError
from processor import AudioProcessor, ProcessorError

class ExitCode(IntEnum):
    """Standardized application exit codes."""

    SUCCESS = 0
    FAILURE = 1
    INVALID_CONFIG = 2
    INTERRUPTED = 130


def main() -> int:
    """Run the audio recorder application pipeline.

    Returns:
        int: Process exit code.
    """
    setup_logging()
    logger = logging.getLogger("main")

    try:
        app_config = parse_args()
        engine = AudioEngine(app_config.audio)
        plotter = Plotter(app_config.plot)

        processor = AudioProcessor(app_config.processing.threshold)
        suffix = app_config.processing.suffix
        name = app_config.audio.output_filename
        fs = app_config.audio.sample_rate

        # 1. Запис і збереження оригіналу
        audio_data = engine.record()
        saved_original = engine.save(audio_data)

        # 2. Обробка (обрізання початку та кінця за порогом)
        processed_data = processor.trim_silence(audio_data)
        saved_processed = engine.save(
            processed_data, app_config.audio.file_path_with_suffix(suffix)
        )

        # 3. Графіки обох сигналів
        plot_original = plotter.plot_signal(audio_data, fs, name)
        plot_processed = plotter.plot_signal(processed_data, fs, f"{name}{suffix}")

        logger.info("Original audio saved to: %s", saved_original)
        logger.info("Processed audio saved to: %s", saved_processed)
        if plot_original:
            logger.info("Original plot saved to: %s", plot_original)
        if plot_processed:
            logger.info("Processed plot saved to: %s", plot_processed)
        return ExitCode.SUCCESS

    except KeyboardInterrupt:
        logger.warning("\nRecording process aborted by user.")
        return ExitCode.INTERRUPTED
    except ValueError as err:
        logger.error("Configuration error: %s", err)
        return ExitCode.INVALID_CONFIG
    except (AudioEngineError, PlotterError, ProcessorError) as err:
        logger.error("Application error: %s", err)
        return ExitCode.FAILURE
    except Exception as err:
        logger.critical("Unexpected failure: %s", err, exc_info=True)
        return ExitCode.FAILURE

if __name__ == "__main__":
    sys.exit(main())