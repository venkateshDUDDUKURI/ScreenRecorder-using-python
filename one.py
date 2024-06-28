import pyautogui
import cv2
import numpy as np
import pyaudio
import wave
import threading
import os
import ffmpeg

# Screen recording settings
resolution = (1920, 1200)
fps = 20.0
video_filename = "temp_video.mp4"
audio_filename = "temp_audio.wav"
output_filename = 'Recording_with_Audio.mp4'

# Audio recording settings
audio_format = pyaudio.paInt16
channels = 2
rate = 44100
chunk = 1024

# Initialize PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(format=audio_format, channels=channels,
                    rate=rate, input=True,
                    frames_per_buffer=chunk)

# Store audio frames
audio_frames = []

# Function to record audio
def record_audio():
    while recording:
        data = stream.read(chunk)
        audio_frames.append(data)

# Start recording audio in a separate thread
recording = True
audio_thread = threading.Thread(target=record_audio)
audio_thread.start()

# Create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 'mp4v' for mp4 format
out = cv2.VideoWriter(video_filename, fourcc, fps, resolution)

# Create OpenCV window
cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Live", 480, 270)

try:
    while True:
        # Capture screenshot
        img = pyautogui.screenshot()

        # Convert screenshot to numpy array and BGR format
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Write frame to video file
        out.write(frame)

        # Display the recording screen (optional)
        cv2.imshow('Live', frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) == ord('q'):
            break
except KeyboardInterrupt:
    print("Recording stopped by user.")

# Stop recording
recording = False
audio_thread.join()

# Release the video writer and audio stream
out.release()
stream.stop_stream()
stream.close()
audio.terminate()

# Save audio to WAV file
with wave.open(audio_filename, 'wb') as wf:
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(audio_format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(audio_frames))

# Verify that the files exist and contain data
if not os.path.isfile(video_filename) or os.path.getsize(video_filename) == 0:
    print(f"Error: Video file '{video_filename}' is missing or empty.")
    exit(1)

if not os.path.isfile(audio_filename) or os.path.getsize(audio_filename) == 0:
    print(f"Error: Audio file '{audio_filename}' is missing or empty.")
    exit(1)

# Combine audio and video using ffmpeg
try:
    video_input = ffmpeg.input(video_filename)
    audio_input = ffmpeg.input(audio_filename)
    ffmpeg.concat(video_input, audio_input, v=1, a=1).output(
        output_filename,
        vcodec='libx264',
        acodec='aac',
        audio_bitrate='192k',
        movflags='faststart'
    ).run(overwrite_output=True)
    print(f"Recording completed successfully. Output file: {output_filename}")
except ffmpeg.Error as e:
    print("FFmpeg error:", e)

# Clean up temporary files
os.remove(video_filename)
os.remove(audio_filename)

# Destroy all windows
cv2.destroyAllWindows()
