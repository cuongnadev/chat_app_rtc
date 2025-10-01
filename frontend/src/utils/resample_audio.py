import numpy as np
from scipy.signal import resample

def ResampleAudio(audio_data: np.ndarray, orig_sample_rate: int, target_sample_rate: int) -> np.ndarray:
    """
    Resample audio data from original sample rate to target sample rate.
    
    Args:
        audio_data: Input audio as numpy array. Supports:
            - Mono: 1D (samples,)
            - Stereo/planar: 2D (channels, samples)
            - Interleaved: 2D (samples, channels) - will auto-detect and convert
        orig_sample_rate: Original sample rate (Hz)
        target_sample_rate: Target sample rate (Hz)
    
    Returns:
        Resampled audio as numpy array with same format as input.
    
    Notes:
        - For multi-channel, resamples each channel independently.
        - Uses float32 for resample accuracy, then clips/scales back to int16.
        - Assumes uniform resampling (no phase issues for short frames).
    """
    if orig_sample_rate == target_sample_rate:
        return audio_data
    
    # Calculate number of output samples
    if audio_data.ndim == 1:
        # Mono: (samples,)
        num_samples_in = len(audio_data)
        num_samples_out = int(round(num_samples_in * target_sample_rate / orig_sample_rate))
        resampled_float = resample(audio_data.astype(np.float32) / 32768.0, num_samples_out)
        resampled = np.clip(resampled_float * 32767, -32768, 32767).astype(np.int16)
        return resampled
    
    elif audio_data.ndim == 2:
        if audio_data.shape[0] < audio_data.shape[1]:
            # Likely interleaved: (samples, channels) -> transpose to planar (ch, samples)
            is_interleaved = True
            audio_planar = audio_data.T  # Now (ch, samples)
        else:
            # Planar: (ch, samples)
            is_interleaved = False
            audio_planar = audio_data
        
        num_channels = audio_planar.shape[0]
        num_samples_in = audio_planar.shape[1]
        num_samples_out = int(round(num_samples_in * target_sample_rate / orig_sample_rate))
        
        resampled_planar = np.zeros((num_channels, num_samples_out), dtype=np.float32)
        for ch in range(num_channels):
            resampled_planar[ch] = resample(audio_planar[ch].astype(np.float32) / 32768.0, num_samples_out)
        
        resampled_float = np.clip(resampled_planar * 32767, -32768, 32767).astype(np.int16)
        
        if is_interleaved:
            resampled = resampled_float.T  # Back to (samples, ch)
        else:
            resampled = resampled_float  # Keep planar (ch, samples)
        
        return resampled
    
    else:
        raise ValueError(f"Unsupported audio_data shape: {audio_data.shape}. Expected 1D or 2D.")