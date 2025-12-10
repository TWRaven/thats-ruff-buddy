#!/usr/bin/env python3
import sys
import subprocess
import os
import platform
import shutil
import random

def get_current_volume_mac():
    """Gets the current volume (0-100)."""
    result = subprocess.run("osascript -e 'output volume of (get volume settings)'", shell=True, capture_output=True, text=True)
    return int(result.stdout.strip())

def set_volume_mac(volume_level):
    """Sets the volume to a specific level (0-100)."""
    subprocess.run(f"osascript -e 'set volume output volume {volume_level}'", shell=True)

def play_sound(sound_file):
    """Plays a sound file using a portable method."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        current_volume = get_current_volume_mac()
        set_volume_mac(50)
        subprocess.run(["afplay", sound_file], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        set_volume_mac(current_volume)
    elif system == "Linux":
        if shutil.which("aplay"):
            subprocess.run(["aplay", sound_file], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        elif shutil.which("ffplay"):
             subprocess.run(["ffplay", "-nodisp", "-autoexit", sound_file], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    elif system == "Windows":
        # Using powershell to play sound
        cmd = f"(New-Object Media.SoundPlayer '{sound_file}').PlaySync()"
        subprocess.run(["powershell", "-c", cmd], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    else:
        # Fallback to ffplay if available everywhere else
        if shutil.which("ffplay"):
             subprocess.run(["ffplay", "-nodisp", "-autoexit", sound_file], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

failure_strings = ("reformatted", "error")

def main():
    # The first argument is the script name, the rest are arguments for ruff
    args = sys.argv[1:]
    
    # Run ruff (or whatever command is passed)
    # We assume 'ruff' is executable in the path or environment
    cmd = ["ruff"] + args
    
    try:
        # We need to capture output to check for "reformatted"
        # but also stream it to the real stdout/stderr
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Print output to real stdout/stderr
        print(result.stdout, end='', file=sys.stdout)
        print(result.stderr, end='', file=sys.stderr)
        
        exit_code = result.returncode
        
        # Check if files were reformatted (usually in stderr for ruff format)
        # Ruff format exit code is 0 even if files are changed, so we check output
        files_reformatted = any(s in result.stderr or s in result.stdout for s in failure_strings)

    except FileNotFoundError:
        print("Error: 'ruff' executable not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running ruff: {e}", file=sys.stderr)
        sys.exit(1)

    should_bark = exit_code != 0 or files_reformatted

    if should_bark:
        sound_file = choose_random_mp3()
        
        if os.path.exists(sound_file):
            play_sound(sound_file)
        
    sys.exit(exit_code)

def choose_random_mp3():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mp3_files = [f for f in os.listdir(script_dir) if f.endswith(".mp3")]
    return os.path.join(script_dir, random.choice(mp3_files))

if __name__ == "__main__":
    main()
