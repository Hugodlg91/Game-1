"""Generate 'Pleasant & Chill' 8-bit background music.

Designed to be non-annoying, harmonic, and soft.
- Voice 1: Bass (Triangle Wave) - Smooth low end.
- Voice 2: Melody (Pulse 25%) - Gentler than square wave.
- Voice 3: Harmony (Pulse 50%) - Quiet backing arpeggios.
- Scale: C Major (Happy/Safe).
- BPM: 100 (Andante).
"""
import wave
import math
import struct
import random

# Audio configuration
SAMPLE_RATE = 44100
BPM = 100
BEAT_DURATION = 60.0 / BPM  # 0.6s
MEASURE_DURATION = BEAT_DURATION * 4  # 2.4s

# Volume settings (Soft mix)
BASS_VOLUME = 0.35
MELODY_VOLUME = 0.25
HARMONY_VOLUME = 0.15
MASTER_VOLUME = 0.25  # Reduced significantly for background use

# Scale: C Major (C D E F G A B)
# Frequencies calculated from A4=440Hz
SCALE = {
    'C2': 65.41, 'D2': 73.42, 'E2': 82.41, 'F2': 87.31, 'G2': 98.00, 'A2': 110.00, 'B2': 123.47,
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00,
    'C6': 1046.50
}

def triangle_wave(freq, duration):
    """Generate smooth triangle wave (Bass)."""
    samples = []
    num_samples = int(duration * SAMPLE_RATE)
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        phase = (freq * t) % 1.0
        if phase < 0.5:
            val = 4.0 * phase - 1.0
        else:
            val = -4.0 * phase + 3.0
        samples.append(val)
    return samples

def pulse_wave(freq, duration, duty=0.25):
    """Generate pulse wave (Melody). 25% duty is classic 'NES Lead'."""
    samples = []
    num_samples = int(duration * SAMPLE_RATE)
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        phase = (freq * t) % 1.0
        val = 1.0 if phase < duty else -1.0
        samples.append(val)
    return samples

def apply_envelope(samples, attack=0.02, decay=0.1, sustain=0.7, release=0.1):
    """Apply soft ADSR envelope."""
    n = len(samples)
    env = [0.0] * n
    
    a_len = int(attack * SAMPLE_RATE)
    d_len = int(decay * SAMPLE_RATE)
    r_len = int(release * SAMPLE_RATE)
    s_len = n - a_len - d_len - r_len
    
    # Attack
    for i in range(a_len):
        if i < n: env[i] = i / a_len
        
    # Decay
    for i in range(d_len):
        idx = a_len + i
        if idx < n: env[idx] = 1.0 - (1.0 - sustain) * (i / d_len)
        
    # Sustain
    for i in range(s_len):
        idx = a_len + d_len + i
        if idx < n: env[idx] = sustain
        
    # Release
    for i in range(r_len):
        idx = a_len + d_len + s_len + i
        if idx < n: env[idx] = sustain * (1.0 - i / r_len)
        
    return [s * e for s, e in zip(samples, env)]

def get_chord_tones(chord_name):
    """Simple chord tone lookup for C Major scale."""
    # C Major: C E G
    if chord_name == 'C': return ['C3', 'E3', 'G3', 'C4']
    # G Major: G B D
    if chord_name == 'G': return ['G2', 'B2', 'D3', 'G3']
    # A Minor: A C E
    if chord_name == 'Am': return ['A2', 'C3', 'E3', 'A3']
    # F Major: F A C
    if chord_name == 'F': return ['F2', 'A2', 'C3', 'F3']
    return ['C3', 'E3', 'G3']

def create_arpeggio(chord, duration):
    """Gentle background arpeggio."""
    notes = get_chord_tones(chord)
    samples = []
    # Slow arpeggio: 8th notes
    note_dur = duration / 4 
    for i in range(4):
        note = notes[i % len(notes)]
        freq = SCALE[note]
        # Use 50% square for harmony (flute-ish if filtered, but we stick to raw here)
        s = pulse_wave(freq, note_dur, duty=0.5)
        s = apply_envelope(s, attack=0.05, decay=0.2, sustain=0.5, release=0.05)
        samples.extend(s)
    return samples

# --- Composition Sections ---

def section_intro():
    """Simple C Major Intro."""
    bass = []
    melody = []
    harmony = []
    
    # 2 Measures of C
    for _ in range(2):
        # Bass: Root note pulse
        b = triangle_wave(SCALE['C3'], MEASURE_DURATION)
        b = apply_envelope(b, sustain=0.8, release=0.2)
        bass.extend(b)
        
        # Melody: Silence intro
        melody.extend([0.0] * int(MEASURE_DURATION * SAMPLE_RATE))
        
        # Harmony: C Arpeggio
        harmony.extend(create_arpeggio('C', MEASURE_DURATION))
        
    return bass, melody, harmony

def section_theme_a():
    """Main Theme - Catchy but simple."""
    bass = []
    melody = []
    harmony = []
    
    progression = ['C', 'G', 'Am', 'F']
    
    # Melody Pattern (simple quarter notes mostly)
    # C: E G E C
    # G: D G D B
    # Am: C E C A
    # F: A C A F
    melodies = [
        [('E4', 1), ('G4', 1), ('E4', 1), ('C4', 1)], # Over C
        [('D4', 1), ('G4', 1), ('D4', 1), ('B3', 1)], # Over G
        [('C4', 1), ('E4', 1), ('C4', 1), ('A3', 1)], # Over Am
        [('A3', 1), ('C4', 1), ('F4', 2)],            # Over F (Long note end)
    ]
    
    for i, chord in enumerate(progression):
        # Bass roots
        root = chord[0] + ('2' if chord[0] in ['A','G','F'] else '3')
        b = triangle_wave(SCALE[root], MEASURE_DURATION)
        b = apply_envelope(b)
        bass.extend(b)
        
        # Harmony Arp
        harmony.extend(create_arpeggio(chord, MEASURE_DURATION))
        
        # Melody
        m_meas = []
        for note, beats in melodies[i]:
            dur = beats * BEAT_DURATION
            s = pulse_wave(SCALE[note], dur, duty=0.25)
            s = apply_envelope(s, attack=0.02, decay=0.1, sustain=0.6, release=0.1)
            m_meas.extend(s)
        melody.extend(m_meas)
        
    return bass, melody, harmony

def create_song():
    full_bass = []
    full_melody = []
    full_harmony = []
    
    # Structure: Intro -> A -> A -> FadeOut
    
    # Intro
    b, m, h = section_intro()
    full_bass.extend(b)
    full_melody.extend(m)
    full_harmony.extend(h)
    
    # Theme A (2 loops)
    for _ in range(2):
        b, m, h = section_theme_a()
        full_bass.extend(b)
        full_melody.extend(m)
        full_harmony.extend(h)
        
    return full_bass, full_melody, full_harmony

def mix_and_save(filename):
    print("Generating pleasant tunes...")
    bass, melody, harmony = create_song()
    
    # Equalize lengths
    max_len = max(len(bass), len(melody), len(harmony))
    bass += [0.0] * (max_len - len(bass))
    melody += [0.0] * (max_len - len(melody))
    harmony += [0.0] * (max_len - len(harmony))
    
    mixed = []
    for i in range(max_len):
        # Mix
        val = (bass[i] * BASS_VOLUME + 
               melody[i] * MELODY_VOLUME + 
               harmony[i] * HARMONY_VOLUME) * MASTER_VOLUME
        
        # Soft Clip Limiter (Tape Saturation Simulation) to avoid harsh digital clipping
        if val > 1.0: val = 1.0
        if val < -1.0: val = -1.0
        
        mixed.append(val)
        
    # Write WAV
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
