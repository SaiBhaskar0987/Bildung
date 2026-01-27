import os
import django
import whisper
from pathlib import Path
from langchain_core.documents import Document
import os
from django.conf import settings

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

_WHISPER_MODEL = whisper.load_model("tiny")


def transcribe_video(video_path: Path):
    """
    Transcribe a video file using Whisper.
    Returns a list of text segments.
    """

    if not video_path.exists():
        print("ERROR → Video file missing:", video_path)
        return []

    try:
        result = _WHISPER_MODEL.transcribe(str(video_path),fp16=False)

    except Exception as e:
        print("ERROR → Whisper failed:", e)
        return []   

    segments = []

    for seg in result.get("segments", []):
        text = seg.get("text", "").strip()
        if text:
            segments.append(text)

    return segments


def load_videos(videos):

    documents = []

    for video in videos:
        video_path = Path(settings.MEDIA_ROOT) / video

        print("DEBUG → video path:", video_path)

        texts = transcribe_video(video_path)

        if not texts:
            print("WARNING → No transcript for:", video)
            continue

        for text in texts:
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": video,
                        "source_type": "video",
                    }
                )
            )

    return documents
