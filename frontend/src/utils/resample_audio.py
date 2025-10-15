# This file contains a helper function for resampling audio data from one
# sample rate to another using scipy. It supports both mono and stereo audio.
import numpy as np
from scipy.signal import resample


def ResampleAudio(
    audio_data: np.ndarray, orig_sample_rate: int, target_sample_rate: int
) -> np.ndarray:
    if orig_sample_rate == target_sample_rate:
        return audio_data

    if audio_data.ndim == 1:
        num_samples_in = len(audio_data)
        num_samples_out = int(
            round(num_samples_in * target_sample_rate / orig_sample_rate)
        )
        resampled_float = resample(
            audio_data.astype(np.float32) / 32768.0, num_samples_out
        )
        resampled = np.clip(resampled_float * 32767, -32768, 32767).astype(np.int16)
        return resampled

    elif audio_data.ndim == 2:
        if audio_data.shape[0] < audio_data.shape[1]:
            is_interleaved = True
            audio_planar = audio_data.T
        else:
            is_interleaved = False
            audio_planar = audio_data

        num_channels = audio_planar.shape[0]
        num_samples_in = audio_planar.shape[1]
        num_samples_out = int(
            round(num_samples_in * target_sample_rate / orig_sample_rate)
        )

        resampled_planar = np.zeros((num_channels, num_samples_out), dtype=np.float32)
        for ch in range(num_channels):
            resampled_planar[ch] = resample(
                audio_planar[ch].astype(np.float32) / 32768.0, num_samples_out
            )

        resampled_float = np.clip(resampled_planar * 32767, -32768, 32767).astype(
            np.int16
        )

        if is_interleaved:
            resampled = resampled_float.T
        else:
            resampled = resampled_float

        return resampled

    else:
        raise ValueError(
            f"Unsupported audio_data shape: {audio_data.shape}. Expected 1D or 2D."
        )
