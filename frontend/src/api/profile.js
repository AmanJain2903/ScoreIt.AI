import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001'; // Flask backend port


export const createProfile = async (email) => {
  return axios.post(`${BASE_URL}/profile/create`, { email });
};

export const readProfile = async (token) => {
  return axios.get(`${BASE_URL}/profile/read`, { headers: { Authorization: `Bearer ${token}` } });
};

export const updateProfile = async (token, updateData) => {
  return axios.post(`${BASE_URL}/profile/update`, { update_data: updateData }, { headers: { Authorization: `Bearer ${token}` } });
};

export const deleteProfile = async (token) => {
  return axios.delete(`${BASE_URL}/profile/delete`, { headers: { Authorization: `Bearer ${token}` } });
};
