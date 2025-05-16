
// src/ProfileSetup.js
import React, { useState } from 'react';
import axios from 'axios';

export default function ProfileSetup() {
  const [goals, setGoals] = useState(['']);
  const [principles, setPrinciples] = useState(['']);
  const [message, setMessage] = useState('');

  const handleChange = (index, value, setState, state) => {
    const updated = [...state];
    updated[index] = value;
    setState(updated);
  };

  const handleAddField = (setState, state) => {
    setState([...state, '']);
  };

  const handleSubmit = async () => {
    const token = localStorage.getItem('token');
    try {
      await axios.post('http://localhost:8000/setup-profile', {
        goals,
        principles
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage('Profile setup successful!');
    } catch (err) {
      setMessage('Failed to set up profile.');
    }
  };

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Set Up Your Profile</h1>
      <div className="mb-4">
        <h2 className="font-semibold mb-2">Long-Term Goals</h2>
        {goals.map((goal, i) => (
          <input
            key={i}
            type="text"
            value={goal}
            onChange={(e) => handleChange(i, e.target.value, setGoals, goals)}
            className="w-full border p-2 mb-2"
          />
        ))}
        <button onClick={() => handleAddField(setGoals, goals)} className="px-3 py-1 bg-blue-500 text-white rounded">Add Goal</button>
      </div>
      <div className="mb-4">
        <h2 className="font-semibold mb-2">Core Principles</h2>
        {principles.map((principle, i) => (
          <input
            key={i}
            type="text"
            value={principle}
            onChange={(e) => handleChange(i, e.target.value, setPrinciples, principles)}
            className="w-full border p-2 mb-2"
          />
        ))}
        <button onClick={() => handleAddField(setPrinciples, principles)} className="px-3 py-1 bg-green-500 text-white rounded">Add Principle</button>
      </div>
      <button onClick={handleSubmit} className="px-4 py-2 bg-purple-600 text-white rounded">Submit</button>
      {message && <p className="mt-4 text-sm text-gray-700">{message}</p>}
    </div>
  );
}