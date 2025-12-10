#!/usr/bin/env python3
import sys
import subprocess
import os
import platform
import shutil

def play_sound(sound_file):
    """Plays a sound file using a portable method."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run(["afplay", sound_file], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
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
        files_reformatted = "reformatted" in result.stderr or "reformatted" in result.stdout

    except FileNotFoundError:
        print("Error: 'ruff' executable not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running ruff: {e}", file=sys.stderr)
        sys.exit(1)

    should_bark = exit_code != 0 or files_reformatted

    if should_bark:
        # Find the sound file relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sound_file = os.path.join(script_dir, "bark.mp3")
        
        if os.path.exists(sound_file):
            play_sound(sound_file)
        
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
