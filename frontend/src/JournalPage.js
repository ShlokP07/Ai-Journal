
// src/JournalPage.js
import React, { useState } from 'react';
import axios from 'axios';

export default function JournalPage() {
  const [audioFile, setAudioFile] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState('');
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const token = localStorage.getItem('token');
  const authHeader = { Authorization: `Bearer ${token}` };

  const handleTranscribe = async () => {
    const formData = new FormData();
    formData.append('file', audioFile);
    const res = await axios.post('http://localhost:8000/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    setTranscript(res.data.transcript);
  };

  const handleSummarize = async () => {
    const res = await axios.post('http://localhost:8000/summarize', {
      transcript
    }, { headers: authHeader });
    setSummary(res.data.summary);
  };

  const handleSearch = async () => {
    const res = await axios.post('http://localhost:8000/search', {
      query_text: query
    }, { headers: authHeader });
    setSearchResults(res.data.matches);
  };

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <h1 className="text-xl font-bold mb-4">Journal App</h1>
      <div className="mb-4">
        <input type="file" accept="audio/*" onChange={(e) => setAudioFile(e.target.files[0])} />
        <button onClick={handleTranscribe} className="ml-2 px-4 py-1 bg-blue-500 text-white rounded">Transcribe</button>
      </div>
      {transcript && (
        <div className="mb-4">
          <h2 className="font-semibold">Transcript:</h2>
          <textarea value={transcript} onChange={(e) => setTranscript(e.target.value)} className="w-full h-32 border p-2" />
          <button onClick={handleSummarize} className="mt-2 px-4 py-1 bg-green-500 text-white rounded">Summarize</button>
        </div>
      )}
      {summary && (
        <div className="mb-4">
          <h2 className="font-semibold">Summary & Feedback:</h2>
          <div className="border p-2 bg-gray-100">{summary}</div>
        </div>
      )}
      <div className="mb-4">
        <h2 className="font-semibold">Search Entries:</h2>
        <input type="text" placeholder="Search query..." value={query} onChange={(e) => setQuery(e.target.value)} className="w-full border p-2 mb-2" />
        <button onClick={handleSearch} className="px-4 py-1 bg-purple-500 text-white rounded">Search</button>
        {searchResults.length > 0 && (
          <ul className="mt-4 list-disc pl-5">
            {searchResults.map((entry, i) => (
              <li key={i}><strong>Transcript:</strong> {entry.transcript}<br /><strong>Summary:</strong> {entry.summary}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
