import librosa
import numpy as np
import scipy

class AudioFeatureExtractor:
    def __init__(self):
        pass

    def extract_features(self, file_path):
        try:
            y, sr = librosa.load(file_path)
        except Exception as e:
            print(f"Error loading file: {e}")
            return None
        
        # 1. Energy
        rms = librosa.feature.rms(y=y)
        spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        energy = self._normalize_energy(rms, spec_cent)
        
        # 2. Danceability
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        danceability = self._calculate_danceability(onset_env, beat_frames)
        
        # 3. Tempo
        if isinstance(tempo, np.ndarray):
            tempo = tempo[0]
            
        # 4. Acousticness
        flatness = librosa.feature.spectral_flatness(y=y)
        acousticness = self._calculate_acousticness(flatness)
        
        # 5. Valence
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        valence = self._calculate_valence(chroma, energy)
        
        return {
            "energy": float(energy),
            "danceability": float(danceability),
            "tempo": float(tempo),
            "acousticness": float(acousticness),
            "valence": float(valence)
        }

    def _normalize_energy(self, rms, spec_cent):
        # Heuristic: RMS is loudness, Centroid is brightness.
        # Normalize RMS roughly 0-0.25 (typical) to 0-1
        # Normalize Centroid roughly 0-5000Hz to 0-1
        norm_rms = np.mean(rms) * 4 
        norm_cent = np.mean(spec_cent) / 5000
        energy = (norm_rms * 0.7) + (norm_cent * 0.3)
        return np.clip(energy, 0, 1)

    def _calculate_danceability(self, onset_env, beat_frames):
        # Heuristic: Low variance in beat intervals = High Danceability
        if len(beat_frames) < 2:
            return 0.0
            
        intervals = np.diff(beat_frames)
        var_intervals = np.var(intervals)
        # Normalize: if variance is 0, danceability is 1.
        # If variance is high, danceability is low.
        # Heuristic scaling: variance of 10 is "high" for beat intervals?
        # Beat intervals are in frames. 512 samples per frame.
        # At 22050Hz, 512 samples is ~23ms.
        # Variance of intervals...
        # Let's use a simple inverse mapping.
        danceability = 1.0 / (1.0 + var_intervals / 10.0) 
        return np.clip(danceability, 0, 1)

    def _calculate_acousticness(self, flatness):
        # High flatness = noise = electric. Low flatness = harmonic = acoustic.
        # Invert flatness.
        mean_flatness = np.mean(flatness)
        acousticness = 1.0 - mean_flatness
        return np.clip(acousticness, 0, 1)

    def _calculate_valence(self, chroma, energy):
        # Sum vectors to estimate Key/Mode.
        chroma_sum = np.sum(chroma, axis=1)
        tonic_idx = np.argmax(chroma_sum)
        chroma_rotated = np.roll(chroma_sum, -tonic_idx)
        
        # Check Major (0, 4, 7) vs Minor (0, 3, 7) strength
        major_score = chroma_rotated[4]
        minor_score = chroma_rotated[3]
        
        if major_score > minor_score:
            base_valence = 0.75
        else:
            base_valence = 0.35
            
        # Adjust based on Energy
        valence = base_valence + (energy - 0.5) * 0.2
        return np.clip(valence, 0, 1)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        extractor = AudioFeatureExtractor()
        print(extractor.extract_features(sys.argv[1]))
    else:
        print("Usage: python features.py <audio_file>")
