import wave
import math
import struct
import random
import os

def generate_sounds():
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sounds')
    os.makedirs(output_dir, exist_ok=True)
    
    # Audio parameters
    sample_rate = 44100
    
    def save_wav(filename, data):
        filepath = os.path.join(output_dir, filename)
        with wave.open(filepath, 'w') as f:
            f.setnchannels(1)  # Mono
            f.setsampwidth(2)  # 2 bytes per sample (16-bit PCM)
            f.setframerate(sample_rate)
            
            # Convert float samples (-1.0 to 1.0) to 16-bit integers
            packed_data = b''
            for sample in data:
                # Clip
                sample = max(-1.0, min(1.0, sample))
                int_sample = int(sample * 32767)
                packed_data += struct.pack('<h', int_sample)
            
            f.writeframes(packed_data)
        print(f"Generated {filepath}")

    # 1. Move Sound: Quick "Swish" / noise burst with fade
    # White noise with exponential decay
    move_duration = 0.15 # seconds
    move_data = []
    num_samples = int(move_duration * sample_rate)
    for i in range(num_samples):
        t = i / sample_rate
        # Envelope: Fast attack, exponential decay
        if t < 0.01:
            envelope = t / 0.01
        else:
            envelope = math.exp(-30 * (t - 0.01))
            
        noise = random.uniform(-1, 1)
        # Low pass filter approximation (simple rolling average could work, but let's just use raw noise shaped by envelope for "air" sound)
        # Actually a simple sine sweep + noise sounds more like a "whoosh"
        
        # Swish component: High frequency sine sweep + noise
        freq = 800 - (600 * t / move_duration)
        sine = math.sin(2 * math.pi * freq * t)
        
        sample = (0.3 * sine + 0.7 * noise) * envelope * 0.5
        move_data.append(sample)
    
    save_wav('move.wav', move_data)

    # 2. Merge Sound: "Pop" / "Ding"
    # Sine wave with pitch envelope (slide up) and short decay
    merge_duration = 0.2
    merge_data = []
    num_samples = int(merge_duration * sample_rate)
    for i in range(num_samples):
        t = i / sample_rate
        # Envelope
        if t < 0.01:
            envelope = t / 0.01
        else:
            envelope = math.exp(-15 * (t - 0.01))
        
        # Frequency slide up for "pop" effect
        # Start at 400, go to 800
        # Instantaneous frequency f(t), Phase is integral of f(t)
        # Linear frequency ramp: f(t) = start + (end-start)*t/duration
        # Phase phi(t) = 2*pi * (start*t + 0.5*(end-start)*t^2/duration)
        
        start_f = 400
        end_f = 900
        phase = 2 * math.pi * (start_f * t + 0.5 * (end_f - start_f) * t**2 / merge_duration)
        
        # Add a bit of harmonics (square-ish) for "digital" feel
        sine = math.sin(phase)
        harmonic = math.sin(phase * 2) * 0.3
        
        sample = (sine + harmonic) * envelope * 0.5
        merge_data.append(sample)

    save_wav('merge.wav', merge_data)

    # 3. Game Over: Descending heavy tone
    # Sawtooth/Square wave sliding down
    go_duration = 1.0
    go_data = []
    num_samples = int(go_duration * sample_rate)
    for i in range(num_samples):
        t = i / sample_rate
        
        # Envelope
        if t < 0.05:
            envelope = t / 0.05
        else:
            envelope = math.exp(-3 * (t - 0.05)) # Slower decay
        
        # Slide down
        start_f = 200
        end_f = 50
        # Phase
        phase = 2 * math.pi * (start_f * t + 0.5 * (end_f - start_f) * t**2 / go_duration)
        
        # Sawtooth approximation
        # simple way: (phase / 2pi) % 1  -> 0..1, shift to -1..1
        val = ((phase / (2 * math.pi)) % 1.0) * 2.0 - 1.0
        
        sample = val * envelope * 0.5
        go_data.append(sample)
        
    save_wav('gameover.wav', go_data)

if __name__ == '__main__':
    generate_sounds()
