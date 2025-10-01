import numpy as np

def ResampleAudio(audio: np.ndarray, old_rate: int, new_rate: int) -> np.ndarray:
    if old_rate == new_rate:
        return audio
    duration = audio.shape[0] / old_rate
    new_length = int(duration * new_rate)
    old_indices = np.arange(audio.shape[0])
    new_indices = np.linspace(0, audio.shape[0]-1, new_length)
    if audio.ndim == 1:
        return np.interp(new_indices, old_indices, audio).astype(np.int16)
    else:
        resampled = []
        for c in range(audio.shape[1]):
            resampled.append(np.interp(new_indices, old_indices, audio[:, c]))
        return np.stack(resampled, axis=1).astype(np.int16)
