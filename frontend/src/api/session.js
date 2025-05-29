import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001'; // Flask backend port

export const createSession = async (token) => {
  return axios.post(`${BASE_URL}/session/create`, {}, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const deleteSession = async (token) => {
  return axios.delete(`${BASE_URL}/session/delete`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const deleteAllSessions = async (token) => {
  return axios.delete(`${BASE_URL}/session/delete_all`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const checkSession = async (token) => {
  return axios.get(`${BASE_URL}/session/check`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

