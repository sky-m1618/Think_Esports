import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {     
    apiKey: "AIzaSyC7ytCM06N5GecYkGZPlWrp0AWCRUcT8_g",
    authDomain: "esports-app-c2c46.firebaseapp.com",
    projectId: "esports-app-c2c46",
    storageBucket: "esports-app-c2c46.firebasestorage.app",
    messagingSenderId: "532199698792",
    appId: "1:532199698792:web:bf3fbaffb91a81d27da6dd",
    measurementId: "G-S2FBBK3MQC"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);