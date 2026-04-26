// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBPnilPhD2HXzrmT39F6R-ye6qPAqKuLmg",
  authDomain: "techchefdispensa.firebaseapp.com",
  databaseURL: "https://techchefdispensa-default-rtdb.firebaseio.com",
  projectId: "techchefdispensa",
  storageBucket: "techchefdispensa.firebasestorage.app",
  messagingSenderId: "786975961165",
  appId: "1:786975961165:web:abcbd8a773ba6eef3aac04",
  measurementId: "G-P4ZFQ1LHK9"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);