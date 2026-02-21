"""Flask entrypoint for Frame Analyzer v2."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from pipeline import run_pipeline

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input_videos"
OUTPUT_DIR = BASE_DIR / "output_results"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024  # 1GB


@app.route("/", methods=["GET", "POST"])
def home():
    """Upload route and results display."""
    if request.method == "POST":
        upload = request.files.get("video")
        if not upload or upload.filename == "":
            return render_template("home.html", error="Please select a video file.")

        filename = secure_filename(upload.filename)
        if not filename:
            return render_template("home.html", error="Invalid file name.")

        input_path = INPUT_DIR / filename
        upload.save(input_path)

        result = run_pipeline(str(input_path), str(OUTPUT_DIR))
        run_id = result["run_id"]
        return redirect(url_for("home", run_id=run_id))

    run_id = request.args.get("run_id")
    context = {
        "run_id": run_id,
        "summary": None,
        "rows": [],
        "video_url": None,
        "graph_url": None,
        "csv_url": None,
    }

    if run_id:
        run_folder = OUTPUT_DIR / run_id
        csv_path = run_folder / "results.csv"
        graph_path = run_folder / "motion_graph.png"
        video_path = run_folder / "annotated_video.mp4"

        if run_folder.exists() and csv_path.exists():
            import csv

            rows = []
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            context["rows"] = rows[:100]
            context["summary"] = {
                "total_frames": len(rows),
                "drop_events": sum(1 for r in rows if r["is_drop"] == "True"),
                "estimated_dropped_frames": sum(int(r["dropped_count"]) for r in rows),
                "merge_events": sum(1 for r in rows if r["is_merge"] == "True"),
            }
            context["video_url"] = url_for("serve_output", run_id=run_id, name="annotated_video.mp4") if video_path.exists() else None
            context["graph_url"] = url_for("serve_output", run_id=run_id, name="motion_graph.png") if graph_path.exists() else None
            context["csv_url"] = url_for("download_csv", run_id=run_id)

    return render_template("home.html", **context)


@app.route("/output/<run_id>/<name>")
def serve_output(run_id: str, name: str):
    """Serve generated files from output_results."""
    path = OUTPUT_DIR / run_id / name
    return send_file(path)


@app.route("/download/<run_id>/results.csv")
def download_csv(run_id: str):
    """Download results CSV."""
    csv_path = OUTPUT_DIR / run_id / "results.csv"
    return send_file(csv_path, as_attachment=True, download_name=f"{run_id}_results.csv")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
