import numpy as np
from scipy.io import wavfile

# Generate a 5-second sine wave at 440 Hz
fs = 44100
t = np.linspace(0, 5, 5 * fs, endpoint=False)
y = 0.5 * np.sin(2 * np.pi * 440 * t)

# Add some noise for spectral flatness
noise = np.random.normal(0, 0.01, len(y))
y = y + noise

# Add some beats (amplitude modulation)
beat_freq = 2 # 120 BPM
beat_env = 0.5 * (1 + np.sin(2 * np.pi * beat_freq * t))
y = y * beat_env

wavfile.write('test.wav', fs, (y * 32767).astype(np.int16))
print("Generated test.wav")
