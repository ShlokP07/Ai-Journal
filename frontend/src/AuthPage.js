// AuthPage.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function AuthPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleRegister = async () => {
    try {
      await axios.post('http://localhost:8000/register', { username, password });
      alert('User registered! Now login.');
    } catch (err) {
      alert('Registration failed.');
    }
  };

  const handleLogin = async () => {
    try {
      const res = await axios.post('http://localhost:8000/token', new URLSearchParams({ username, password }), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      localStorage.setItem('token', res.data.access_token);
      navigate('/');
    } catch (err) {
      alert('Login failed.');
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <h2 className="text-xl font-bold mb-4">Login / Register</h2>
      <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} className="border p-2 w-full mb-2" />
      <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} className="border p-2 w-full mb-4" />
      <button onClick={handleRegister} className="px-4 py-2 bg-gray-600 text-white mr-2">Register</button>
      <button onClick={handleLogin} className="px-4 py-2 bg-blue-600 text-white">Login</button>
    </div>
  );
}
