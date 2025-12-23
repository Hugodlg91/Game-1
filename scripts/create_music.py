"""Generate 'Nostalgic NES' 8-bit background music.

Style:
- Voice 1: Bass (Triangle Wave) - Steady 8th note rhythm.
- Voice 2: Melody (Square Wave 50%) - Catchy, thoughtful melody.
- Voice 3: Counter-melody (Pulse 25%) - Texture.
- Scale: A Minor (Thoughtful/Concentration).
- BPM: 110.
"""
import wave
import struct
import random

# Audio configuration
SAMPLE_RATE = 44100
BPM = 120
BEAT_DURATION = 60.0 / BPM  # 0.5s
MEASURE_DURATION = BEAT_DURATION * 4  # 2.0s

# Volume settings
BASS_VOLUME = 0.4
MELODY_VOLUME = 0.3
HARMONY_VOLUME = 0.15
NOISE_VOLUME = 0.1
MASTER_VOLUME = 0.3

# Scale: A Minor (A B C D E F G)
SCALE = {
    'E2': 82.41, 'G2': 98.00, 'A2': 110.00, 'B2': 123.47,
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00,
    'B5': 987.77, 'C6': 1046.50
}

def triangle_wave(freq, duration):
    """Generate triangle wave (Bass)."""
    samples = []
    num_samples = int(duration * SAMPLE_RATE)
    if freq == 0: return [0.0] * num_samples
    
    period_samples = SAMPLE_RATE / freq
    half_period = period_samples / 2
    
    for i in range(num_samples):
        # Optimized triangle
        cycle_pos = (i % period_samples)
        if cycle_pos < half_period:
            val = -1.0 + (2.0 * cycle_pos / half_period)
        else:
            val = 1.0 - (2.0 * (cycle_pos - half_period) / half_period)
        samples.append(val)
    return samples

def pulse_wave(freq, duration, duty=0.5):
    """Generate pulse wave."""
    samples = []
    num_samples = int(duration * SAMPLE_RATE)
    if freq == 0: return [0.0] * num_samples
    
    period_samples = SAMPLE_RATE / freq
    duty_samples = period_samples * duty
    
    for i in range(num_samples):
        val = 1.0 if (i % period_samples) < duty_samples else -1.0
        samples.append(val)
    return samples

def noise_burst(duration):
    """Simple white noise burst for percussion."""
    num_samples = int(duration * SAMPLE_RATE)
    return [random.uniform(-1, 1) for _ in range(num_samples)]

def apply_envelope(samples, attack=0.01, decay=0.05, sustain=0.5, release=0.05):
    """ADSR Envelope."""
    n = len(samples)
    env = [0.0] * n
    a_len = int(attack * SAMPLE_RATE)
    d_len = int(decay * SAMPLE_RATE)
    r_len = int(release * SAMPLE_RATE)
    s_len = max(0, n - a_len - d_len - r_len)
    
    for i in range(n):
        if i < a_len:
            lvl = i / a_len
        elif i < a_len + d_len:
            lvl = 1.0 - ((1.0 - sustain) * ((i - a_len) / d_len))
        elif i < a_len + d_len + s_len:
            lvl = sustain
        else:
            rem = (i - (a_len + d_len + s_len))
            lvl = sustain * (1.0 - (rem / r_len)) if r_len > 0 else 0
        
        env[i] = lvl * samples[i]
    return env

def create_song():
    bass_track = []
    melody_track = []
    
    # Chord Progression: Am - F - C - G (Classic, nostalgic)
    progression = [
        {'root': 'A2', 'chord': 'Am'},
        {'root': 'F2', 'chord': 'F'},
        {'root': 'C3', 'chord': 'C'},
        {'root': 'G2', 'chord': 'G'}
    ]
    
    # Bass Pattern: Steady 8th notes (Root-Root-Octave-Root)
    # Melody Pattern: Slower, lyrical
    
    # 4 Measures loop, repeated twice
    for _ in range(2):
        for p in progression:
            root = p['root']
            # Bass: 8 x 8th notes
            bass_meas = []
            note_dur = BEAT_DURATION / 2 # 8th note
            
            # Pattern: Root Root Octave Root Root Root Octave Root
            octave = root[0] + str(int(root[1]) + 1)
            pattern = [root, root, octave, root, root, root, octave, root]
            
            for b_note in pattern:
                s = triangle_wave(SCALE.get(b_note, 110), note_dur)
                s = apply_envelope(s, attack=0.01, decay=0.1, sustain=0.8, release=0.01)
                bass_meas.extend(s)
            bass_track.extend(bass_meas)
            
            # Melody (simplified for this chord)
            # Am: A C E
            # F: F A C
            # C: C E G
            # G: G B D
            mel_meas = []
            if p['chord'] == 'Am':
                # E A C A
                notes = [('E4', 1), ('A4', 1), ('C5', 1), ('A4', 1)]
            elif p['chord'] == 'F':
                # F A C A
                notes = [('F4', 1), ('A4', 1), ('C5', 1), ('A4', 1)]
            elif p['chord'] == 'C':
                # E G C G
                notes = [('E4', 1), ('G4', 1), ('C5', 1), ('G4', 1)]
            elif p['chord'] == 'G':
                # D G B G
                notes = [('D4', 1), ('G4', 1), ('B4', 1), ('G4', 1)]
                
            for m_note, beats in notes:
                dur = beats * BEAT_DURATION
                s = pulse_wave(SCALE[m_note], dur, duty=0.5) # Square wave
                s = apply_envelope(s, attack=0.02, decay=0.1, sustain=0.6, release=0.1)
                mel_meas.extend(s)
            melody_track.extend(mel_meas)

    return bass_track, melody_track

def mix_and_save(filename):
    print("Generating NES chiptune...")
    bass, melody = create_song()
    
    max_len = max(len(bass), len(melody))
    bass += [0.0] * (max_len - len(bass))
    melody += [0.0] * (max_len - len(melody))
    
    mixed = []
    
    # Simple percussion (noise on beats 2 and 4)
    # 4 beats per measure * 4 measures * 2 loops = 32 beats
    # Noise at beat index 1, 3, 5... (0-indexed)
    
    total_samples = max_len
    percussion = [0.0] * total_samples
    samples_per_beat = int(BEAT_DURATION * SAMPLE_RATE)
    
    for beat in range(32):
        if beat % 2 == 1: # Beats 2 and 4
            start_idx = beat * samples_per_beat
            snare = noise_burst(0.1) # Short snare
            snare = apply_envelope(snare, attack=0.001, decay=0.05, sustain=0.0, release=0.0)
            
            for i, samp in enumerate(snare):
                if start_idx + i < total_samples:
                    percussion[start_idx + i] += samp * NOISE_VOLUME

    for i in range(max_len):
        val = (bass[i] * BASS_VOLUME + 
               melody[i] * MELODY_VOLUME +
               percussion[i]) * MASTER_VOLUME
        
        if val > 1.0: val = 1.0
        if val < -1.0: val = -1.0
        mixed.append(val)
        
    print(f"Saving to {filename}...")
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        for s in mixed:
            int_val = int(s * 32767)
            wf.writeframes(struct.pack('<h', int_val))
    print("Done!")

if __name__ == "__main__":
    mix_and_save("assets/sounds/background.wav")
