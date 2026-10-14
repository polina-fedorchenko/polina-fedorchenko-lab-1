"""Command Line Interface (CLI) module for parsing application arguments."""

import argparse
from pathlib import Path
from config import AppConfig, AudioConfig, PlotConfig, ProcessingConfig

def parse_args(args: None | list[str] = None) -> AppConfig:
    """Parse command line arguments and return a validated AppConfig instance.

    Args:
        args: Optional list of command-line argument strings (useful for testing).

    Returns:
        AppConfig: Aggregate configuration object containing AudioConfig and PlotConfig.
    """
    default_audio = AudioConfig()
    default_plot = PlotConfig()
    default_processing = ProcessingConfig()

    parser = argparse.ArgumentParser(
        prog="audio-recorder",
        description="Cross-platform command line utility to record audio from microphone.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Audio recording options
    audio_group = parser.add_argument_group("Audio Settings")
    audio_group.add_argument(
        "-d",
        "--duration",
        type=int,
        default=default_audio.duration,
        help="Duration of recording in seconds",
    )
    audio_group.add_argument(
        "-n",
        "--name",
        type=str,
        default=default_audio.output_filename,
        dest="output_filename",
        help="Name of the output file (without extension)",
    )
    audio_group.add_argument(
        "-e",
        "--ext",
        type=str,
        default=default_audio.output_extension,
        dest="output_extension",
        help="File extension / audio container format",
    )
    audio_group.add_argument(
        "-sr",
        "--sample-rate",
        type=int,
        default=default_audio.sample_rate,
        dest="sample_rate",
        help="Sampling rate in Hz",
    )
    audio_group.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=default_audio.output_dir,
        dest="output_dir",
        help="Output directory path for audio recordings",
    )

    # Plotting options
    plot_group = parser.add_argument_group("Visualization Settings")
    plot_group.add_argument(
        "-fig",
        "--figures-dir",
        type=Path,
        default=default_plot.figures_dir,
        dest="figures_dir",
        help="Output directory path for plot figures",
    )
    plot_group.add_argument(
        "--no-plot",
        action="store_false",
        dest="plot_enabled",
        default=default_plot.enabled,
        help="Disable waveform signal plotting",
    )
    plot_group.add_argument(
        "--no-show",
        action="store_false",
        dest="plot_show",
        default=default_plot.show,
        help="Disable interactive GUI window display of the plot",
    )

    # Processing options
    proc_group = parser.add_argument_group("Processing Settings")
    proc_group.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=default_processing.threshold,
        help="Amplitude threshold (0-1) for trimming silence",
    )

    parsed = parser.parse_args(args)

    audio_config = AudioConfig(
        sample_rate=parsed.sample_rate,
        duration=parsed.duration,
        output_filename=parsed.output_filename,
        output_extension=parsed.output_extension,
        output_dir=parsed.output_dir,
    )

    plot_config = PlotConfig(
        figures_dir=parsed.figures_dir,
        enabled=parsed.plot_enabled,
        show=parsed.plot_show,
    )

    processing_config = ProcessingConfig(threshold=parsed.threshold)

    return AppConfig(audio=audio_config, plot=plot_config, processing=processing_config)