import axios from 'axios';

const BASE_URL = 'http://localhost:5001'; // Flask backend port

export const makeMatch = async (resume_json, jd_json) => {
  return axios.post(`${BASE_URL}/make_match`, 
    { resume_json, jd_json },
    {
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );
};