import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001'; // Flask backend port


export const addHistory = async (email, resume_text, resume_json, jd_text, jd_json, match_report) => {
    return axios.post(`${BASE_URL}/history/add`, { email, resume_text, resume_json, jd_text, jd_json, match_report });
};

export const getHistory = async (email) => {
    return axios.post(`${BASE_URL}/history/get_all`, { email });
};

export const deleteAll = async (email) => {
    return axios.delete(`${BASE_URL}/history/delete_all`, { data: { email } });
};

export const deleteOne = async (email, match_id) => {
    return axios.delete(`${BASE_URL}/history/delete_one`, {
        data: { email, match_id },
        headers: {
            'Content-Type': 'application/json'
        }
    });
};