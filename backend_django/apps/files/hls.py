from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import shutil as _shutil
from pathlib import Path

from django.conf import settings

from apps.files.minio_client import s3_client


def _guess_content_type(key: str) -> str:
    k = (key or "").lower()
    if k.endswith(".m3u8"):
        return "application/vnd.apple.mpegurl"
    if k.endswith(".ts"):
        return "video/mp2t"
    if k.endswith(".m4s"):
        return "video/iso.segment"
    if k.endswith(".mp4"):
        return "video/mp4"
    return "application/octet-stream"


def is_ffmpeg_available() -> bool:
    return _shutil.which("ffmpeg") is not None


def download_object_to_file(key: str, dst_path: Path) -> None:
    client = s3_client()
    obj = client.get_object(Bucket=settings.MINIO_BUCKET, Key=key)
    body = obj["Body"]
    with dst_path.open("wb") as f:
        for chunk in iter(lambda: body.read(1024 * 1024), b""):
            f.write(chunk)


def upload_folder(prefix: str, folder: Path) -> None:
    client = s3_client()
    for root, _dirs, files in os.walk(folder):
        for name in files:
            full_path = Path(root) / name
            rel = full_path.relative_to(folder).as_posix()
            key = f"{prefix.rstrip('/')}/{rel}"
            client.upload_file(
                str(full_path),
                settings.MINIO_BUCKET,
                key,
                ExtraArgs={"ContentType": _guess_content_type(key)},
            )


def transcode_mp4_to_hls(source_key: str, output_prefix: str) -> str:
    """
    Transcode MP4 in MinIO to multi-bitrate HLS and upload to MinIO.
    Returns master playlist object key.
    """
    source_key = source_key.lstrip("/")
    output_prefix = output_prefix.lstrip("/").rstrip("/")

    if not is_ffmpeg_available():
        raise RuntimeError(
            "ffmpeg is not installed or not in PATH on the backend host. "
            "Install ffmpeg and restart the backend."
        )

    tmpdir = Path(tempfile.mkdtemp(prefix="atg_hls_"))
    try:
        input_path = tmpdir / "input.mp4"
        download_object_to_file(source_key, input_path)

        out_dir = tmpdir / "out"
        out_dir.mkdir(parents=True, exist_ok=True)

        # 3 renditions: 360p, 480p, 720p (fast + good enough for most)
        # NOTE: This requires ffmpeg installed on the backend host.
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-filter_complex",
            (
                "[0:v]split=3[v360][v480][v720];"
                "[v360]scale=w=640:h=360:force_original_aspect_ratio=decrease[v360out];"
                "[v480]scale=w=854:h=480:force_original_aspect_ratio=decrease[v480out];"
                "[v720]scale=w=1280:h=720:force_original_aspect_ratio=decrease[v720out]"
            ),
            "-map",
            "[v360out]",
            "-map",
            "a:0?",
            "-map",
            "[v480out]",
            "-map",
            "a:0?",
            "-map",
            "[v720out]",
            "-map",
            "a:0?",
            "-c:v:0",
            "libx264",
            "-b:v:0",
            "800k",
            "-maxrate:v:0",
            "856k",
            "-bufsize:v:0",
            "1200k",
            "-c:v:1",
            "libx264",
            "-b:v:1",
            "1400k",
            "-maxrate:v:1",
            "1498k",
            "-bufsize:v:1",
            "2100k",
            "-c:v:2",
            "libx264",
            "-b:v:2",
            "2800k",
            "-maxrate:v:2",
            "2996k",
            "-bufsize:v:2",
            "4200k",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-ac",
            "2",
            "-ar",
            "48000",
            "-preset",
            "veryfast",
            "-g",
            "48",
            "-sc_threshold",
            "0",
            "-hls_time",
            "4",
            "-hls_playlist_type",
            "vod",
            "-hls_flags",
            "independent_segments",
            "-hls_segment_filename",
            str(out_dir / "v%v" / "seg_%06d.ts"),
            "-master_pl_name",
            "master.m3u8",
            "-var_stream_map",
            "v:0,a:0 v:1,a:1 v:2,a:2",
            str(out_dir / "v%v" / "prog_index.m3u8"),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {proc.stderr[-2000:]}")

        upload_folder(output_prefix, out_dir)
        return f"{output_prefix}/master.m3u8"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


