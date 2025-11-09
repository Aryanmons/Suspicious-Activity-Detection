import React, { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { FaUpload } from "react-icons/fa";
import "./Upload.css";

function Upload() {
  const [file, setFile] = useState(null);
  const [videoURL, setVideoURL] = useState(null);
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setVideoURL(URL.createObjectURL(selectedFile));
    setResult(null);
    setProgress(0);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a video file first!");
      return;
    }

    setUploading(true);
    setProgress(0);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://127.0.0.1:8000/predict/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => {
          const percent = Math.round((event.loaded * 100) / event.total);
          setProgress(percent);
        },
      });

      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Error analyzing video!");
    } finally {
      setUploading(false);
    }
  };

  const handleExit = () => {
    setFile(null);
    setVideoURL(null);
    setProgress(0);
    setResult(null);
    setUploading(false);
  };

  return (
    <motion.div
      className="upload-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      <h1 className="title">Suspicious Activity Detection System</h1>

      <div className="upload-box">
        <label htmlFor="video-upload" className="upload-label">
          {videoURL ? (
            <video
              src={videoURL}
              loop
              autoPlay
              muted
              className="preview-video"
            ></video>
          ) : (
            <>
              <FaUpload size={45} />
              <p>{file ? file.name : "Click to choose a video file"}</p>
            </>
          )}
        </label>

        <input
          id="video-upload"
          type="file"
          accept="video/mp4,video/avi,video/mov"
          onChange={handleFileChange}
        />

        <div className="btn-group">
          <button onClick={handleUpload} disabled={uploading}>
            {uploading ? "Analyzing..." : "Upload & Analyze"}
          </button>

          {file && (
            <button className="exit-btn" onClick={handleExit}>
              Exit
            </button>
          )}
        </div>

        {uploading && (
          <div className="progress-bar">
            <div className="progress" style={{ width: `${progress}%` }}></div>
          </div>
        )}

        {result && (
          <motion.div
            className="result-box"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <h2>
              Result:{" "}
              <span
                className={
                  result.result === "Suspicious Activity" ? "danger" : "safe"
                }
              >
                {result.result}
              </span>
            </h2>
            <p>
              Frames analyzed: {result.total_frames} <br />
              Suspicious frames: {result.suspicious_frames}
            </p>
            <p>
              Confidence: <strong>{result.confidence}%</strong>
            </p>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

export default Upload;
    