import React, { useState, useRef, useCallback } from 'react';

export default function FileDropZone({ onFileLoaded }) {
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef(null);

  const readFile = useCallback((file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      onFileLoaded(file.name, e.target.result);
    };
    reader.readAsText(file);
  }, [onFileLoaded]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) readFile(file);
  }, [readFile]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragging(false);
  }, []);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) readFile(file);
  };

  return (
    <>
      <div
        className={`drop-zone ${dragging ? 'dragover' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
      >
        <div className="icon">📂</div>
        <div className="label">Drop your file here</div>
        <div className="hint">or click to browse — any code file works!</div>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".py,.js,.ts,.jsx,.tsx,.go,.rs,.java,.rb,.php,.c,.cpp,.h,.cs"
        style={{ display: 'none' }}
        onChange={handleFileInput}
      />
    </>
  );
}
