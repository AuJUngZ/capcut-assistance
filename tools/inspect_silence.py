from __future__ import annotations

import argparse
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ffmpeg", required=True)
    parser.add_argument("--media", required=True)
    parser.add_argument("--noise", default="-35dB")
    parser.add_argument("--duration", default="0.25")
    args = parser.parse_args()

    command = [
        args.ffmpeg,
        "-hide_banner",
        "-nostats",
        "-i",
        args.media,
        "-af",
        f"silencedetect=noise={args.noise}:d={args.duration}",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    for line in result.stderr.splitlines():
        if "silence_start" in line or "silence_end" in line:
            print(line)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
