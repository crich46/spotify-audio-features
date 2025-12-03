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
        
        # --- Pre-computation ---
        # 1. Onset Strength (Activity)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        # 2. Rhythm / Beats
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, onset_envelope=onset_env)
        if isinstance(tempo, np.ndarray):
            tempo = tempo[0]
            
        # 3. Spectral Features
        rms = librosa.feature.rms(y=y)
        spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        spec_flat = librosa.feature.spectral_flatness(y=y)
        spec_roll = librosa.feature.spectral_rolloff(y=y, sr=sr)
        
        # 4. Harmonic / Percussive Separation
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        # --- Feature Calculation ---
        
        # 1. Energy
        # Combination of Loudness (RMS), Brightness (Centroid), and Activity (Onset)
        energy = self._calculate_energy(rms, spec_cent, onset_env)
        
        # 2. Danceability
        # Combination of Beat Strength and Rhythm Regularity
        danceability = self._calculate_danceability(onset_env, beat_frames, tempo)
        
        # 3. Acousticness
        # Combination of Flatness (Tonality) and Rolloff (High-freq content)
        acousticness = self._calculate_acousticness(spec_flat, spec_roll)
        
        # 4. Valence
        # Key/Mode + Harmonic/Percussive Ratio
        valence = self._calculate_valence(y, sr, y_harmonic, y_percussive)
        
        return {
            "energy": float(energy),
            "danceability": float(danceability),
            "tempo": float(tempo),
            "acousticness": float(acousticness),
            "valence": float(valence)
        }

    def _normalize(self, value, min_val, max_val):
        return np.clip((value - min_val) / (max_val - min_val), 0, 1)

    def _calculate_energy(self, rms, spec_cent, onset_env):
        # 1. Loudness (RMS) - Typical range 0.0 to 0.4
        norm_rms = self._normalize(np.mean(rms), 0.0, 0.3)
        
        # 2. Brightness (Centroid) - Typical range 500 to 5000Hz
        norm_cent = self._normalize(np.mean(spec_cent), 500, 4000)
        
        # 3. Activity (Onset Strength) - Typical range 0.0 to 2.0
        norm_onset = self._normalize(np.mean(onset_env), 0.0, 1.5)
        
        # Weighted Average: Loudness is dominant
        return (norm_rms * 0.5) + (norm_cent * 0.25) + (norm_onset * 0.25)

    def _calculate_danceability(self, onset_env, beat_frames, tempo):
        if len(beat_frames) < 2:
            return 0.0
            
        # 1. Beat Strength (Average onset strength at beat locations)
        beat_strengths = onset_env[beat_frames]
        norm_beat_strength = self._normalize(np.mean(beat_strengths), 0.0, 3.0)
        
        # 2. Pulse Clarity (Regularity of beat intervals)
        intervals = np.diff(beat_frames)
        var_intervals = np.var(intervals)
        # Lower variance = Higher clarity. Map variance 0-200 to 1-0
        pulse_clarity = 1.0 / (1.0 + var_intervals / 50.0)
        
        # 3. Tempo Penalty (Too slow or too fast is hard to dance to)
        # Sweet spot: 100-130 BPM
        if tempo < 50 or tempo > 200:
            tempo_factor = 0.5
        elif 90 <= tempo <= 140:
            tempo_factor = 1.0
        else:
            tempo_factor = 0.8
            
        return (norm_beat_strength * 0.4) + (pulse_clarity * 0.4) + (tempo_factor * 0.2)

    def _calculate_acousticness(self, spec_flat, spec_roll):
        # 1. Spectral Flatness (Tonality)
        # Low flatness = Tonal (Acoustic). High flatness = Noisy (Electric/Distorted).
        # Invert flatness: 1.0 means perfectly tonal.
        norm_flatness = 1.0 - self._normalize(np.mean(spec_flat), 0.0, 0.1)
        
        # 2. Spectral Rolloff (High Frequency Content)
        # Acoustic instruments often have lower rolloff than synthesized sounds.
        # Typical range 1000Hz to 8000Hz.
        # Lower rolloff -> Higher acousticness
        norm_rolloff = 1.0 - self._normalize(np.mean(spec_roll), 1000, 7000)
        
        return (norm_flatness * 0.6) + (norm_rolloff * 0.4)

    def _calculate_valence(self, y, sr, y_harmonic, y_percussive):
        # 1. Key/Mode (Major = Happy, Minor = Sad)
        chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
        chroma_sum = np.sum(chroma, axis=1)
        tonic_idx = np.argmax(chroma_sum)
        chroma_rotated = np.roll(chroma_sum, -tonic_idx)
        
        # Major (0, 4, 7) vs Minor (0, 3, 7)
        major_strength = chroma_rotated[4]
        minor_strength = chroma_rotated[3]
        
        if major_strength > minor_strength:
            mode_score = 0.75 # Major
        else:
            mode_score = 0.35 # Minor
            
        # 2. Harmonic vs Percussive Ratio
        # More harmonic = more melodic/emotional (Higher Valence potential)
        # More percussive = more aggressive/energetic (Lower Valence potential)
        h_energy = np.mean(librosa.feature.rms(y=y_harmonic))
        p_energy = np.mean(librosa.feature.rms(y=y_percussive))
        
        if h_energy + p_energy > 0:
            ratio = h_energy / (h_energy + p_energy) # 1.0 = Pure Harmonic, 0.0 = Pure Percussive
        else:
            ratio = 0.5
            
        # Combine: Mode sets the baseline, Ratio adjusts it
        # If Ratio is high (Melodic), pull towards mode_score
        # If Ratio is low (Percussive), pull towards 0.5 (Neutral/Aggressive)
        valence = (mode_score * 0.7) + (ratio * 0.3)
        return np.clip(valence, 0, 1)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        extractor = AudioFeatureExtractor()
        print(extractor.extract_features(sys.argv[1]))
    else:
        print("Usage: python features.py <audio_file>")
