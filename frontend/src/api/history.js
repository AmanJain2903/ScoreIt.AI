import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001'; // Flask backend port


export const addHistory = async (token, resume_text, resume_json, jd_text, jd_json, match_report) => {
    return axios.post(`${BASE_URL}/history/add`, { resume_text, resume_json, jd_text, jd_json, match_report }, 
        { headers: { Authorization: `Bearer ${token}` } });
};

export const getHistory = async (token) => {
    return axios.get(`${BASE_URL}/history/get_all`, { headers: { Authorization: `Bearer ${token}` } });
};

export const deleteAll = async (token) => {
    return axios.delete(`${BASE_URL}/history/delete_all`, { headers: { Authorization: `Bearer ${token}` } });
};

export const deleteOne = async (token, match_id) => {
    return axios.delete(`${BASE_URL}/history/delete_one`, {
        data: { match_id }, 
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });
};