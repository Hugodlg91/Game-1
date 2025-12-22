"""Generate 8-bit style background music for the game."""
import wave
import math
import random

# Constants
SAMPLE_RATE = 44100
DURATION = 30  # 30 seconds loop
BPM = 100
BEAT_DURATION = 60.0 / BPM
AMPLITUDE = 0.15  # Keep it moderate (not aggressive)

def square_wave(frequency, duration, sample_rate=SAMPLE_RATE):
    """Generate a square wave at given frequency."""
    num_samples = int(duration * sample_rate)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        value = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
        samples.append(int(value * AMPLITUDE * 32767))
    return samples

def generate_melody():
    """Generate a simple 8-bit melody."""
    # Simple pentatonic scale (C major pentatonic)
    # C4=261.63, D4=293.66, E4=329.63, G4=392.00, A4=440.00
    notes = {
        'C4': 261.63,
        'D4': 293.66,
        'E4': 329.63,
        'G4': 392.00,
        'A4': 440.00,
        'C5': 523.25,
    }
    
    # Simple repeating pattern (8 bars, 4 beats each)
    # Pattern: C4 E4 G4 A4 | G4 E4 D4 C4 | E4 G4 A4 C5 | A4 G4 E4 D4 | repeat
    pattern = [
        ('C4', 0.5), ('E4', 0.5), ('G4', 0.5), ('A4', 0.5),
        ('G4', 0.5), ('E4', 0.5), ('D4', 0.5), ('C4', 0.5),
        ('E4', 0.5), ('G4', 0.5), ('A4', 0.5), ('C5', 0.5),
        ('A4', 0.5), ('G4', 0.5), ('E4', 0.5), ('D4', 1.0),
    ]
    
    all_samples = []
    
    # Repeat pattern to fill duration
    loops_needed = int(DURATION / (len(pattern) * 0.5)) + 1
    
    for _ in range(loops_needed):
        for note, duration in pattern:
            freq = notes[note]
            samples = square_wave(freq, duration * BEAT_DURATION)
            all_samples.extend(samples)
    
    # Trim to exact duration
    total_samples_needed = int(DURATION * SAMPLE_RATE)
    return all_samples[:total_samples_needed]

def save_wav(filename, samples):
    """Save samples to WAV file."""
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        
        # Convert to bytes
        for sample in samples:
            wav_file.writeframes(sample.to_bytes(2, byteorder='little', signed=True))

if __name__ == "__main__":
    print("Generating 8-bit background music...")
    melody = generate_melody()
    
    output_path = "assets/sounds/background.wav"
    save_wav(output_path, melody)
    
    print(f"✓ Music saved to {output_path}")
    print(f"  Duration: {DURATION}s")
    print(f"  BPM: {BPM}")
    print(f"  Volume: {AMPLITUDE * 100}%")
