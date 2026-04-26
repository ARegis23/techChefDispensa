// static/js/firebase_init.js

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyA2GlGVui5VSGognQwzb_OYbE64yzvTOmc",
    authDomain: "techchefdispensa.firebaseapp.com",
    projectId: "techchefdispensa",
    storageBucket: "techchefdispensa.firebasestorage.app",
    messagingSenderId: "786975961165",
    appId: "1:786975961165:web:abcbd8a773ba6eef3aac04"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { app, auth };