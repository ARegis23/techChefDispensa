import { auth } from "./firebase_init.js";

import {
    GoogleAuthProvider,
    signInWithPopup,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    updateProfile
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js";


const formLogin = document.getElementById("form-login");
const btnCriarConta = document.getElementById("btn-criar-conta");
const btnGoogle = document.getElementById("btn-google");
const authMessage = document.getElementById("auth-message");


function mostrarMensagem(texto, tipo = "info") {
    if (!authMessage) {
        return;
    }

    authMessage.innerText = texto;
    authMessage.dataset.tipo = tipo;
}


function bloquearBotoes(bloquear) {
    const botoes = [
        formLogin?.querySelector("button[type='submit']"),
        btnCriarConta,
        btnGoogle
    ];

    botoes.forEach((botao) => {
        if (botao) {
            botao.disabled = bloquear;
        }
    });
}


function traduzirErroFirebase(error) {
    const codigo = error?.code || "";

    const mensagens = {
        "auth/invalid-email": "O e-mail informado não é válido.",
        "auth/missing-email": "Informe um e-mail para continuar.",
        "auth/missing-password": "Informe uma senha para continuar.",
        "auth/weak-password": "A senha está fraca. Use pelo menos 6 caracteres.",
        "auth/email-already-in-use": "Este e-mail já está cadastrado. Tente fazer login.",
        "auth/user-not-found": "Nenhuma conta foi encontrada com este e-mail.",
        "auth/wrong-password": "A senha informada está incorreta.",
        "auth/invalid-credential": "E-mail ou senha inválidos.",
        "auth/too-many-requests": "Muitas tentativas em pouco tempo. Aguarde alguns minutos e tente novamente.",
        "auth/network-request-failed": "Falha de conexão. Verifique sua internet.",
        "auth/operation-not-allowed": "Este método de login não está habilitado no Firebase.",
        "auth/popup-closed-by-user": "A janela de login foi fechada antes da conclusão.",
        "auth/cancelled-popup-request": "A solicitação de login foi cancelada.",
        "auth/popup-blocked": "O navegador bloqueou a janela de login. Libere pop-ups para continuar.",
        "auth/account-exists-with-different-credential": "Já existe uma conta com este e-mail usando outro método de login."
    };

    return mensagens[codigo] || "Não foi possível concluir a autenticação. Tente novamente.";
}


function validarCamposLogin(email, senha) {
    if (!email || !senha) {
        return "Informe e-mail e senha para continuar.";
    }

    if (!email.includes("@")) {
        return "Informe um e-mail válido.";
    }

    if (senha.length < 6) {
        return "A senha deve ter pelo menos 6 caracteres.";
    }

    return null;
}


function validarCamposCadastro(nome, email, senha) {
    if (!nome || !email || !senha) {
        return "Informe nome, e-mail e senha para criar a conta.";
    }

    if (!email.includes("@")) {
        return "Informe um e-mail válido.";
    }

    if (senha.length < 6) {
        return "A senha deve ter pelo menos 6 caracteres.";
    }

    return null;
}


async function enviarTokenParaBackend(usuarioFirebase) {
    const idToken = await usuarioFirebase.getIdToken();

    const resposta = await fetch("/auth/session-login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            idToken: idToken
        })
    });

    let dados = {};

    try {
        dados = await resposta.json();
    } catch {
        throw new Error("Resposta inválida do servidor.");
    }

    if (!resposta.ok || !dados.ok) {
        throw new Error(dados.erro || "Erro ao criar sessão no servidor.");
    }

    window.location.href = dados.redirect;
}


if (formLogin) {
    formLogin.addEventListener("submit", async function (event) {
        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const senha = document.getElementById("senha").value;

        const erroValidacao = validarCamposLogin(email, senha);

        if (erroValidacao) {
            mostrarMensagem(erroValidacao, "erro");
            return;
        }

        try {
            bloquearBotoes(true);
            mostrarMensagem("Entrando...", "info");

            const credencial = await signInWithEmailAndPassword(
                auth,
                email,
                senha
            );

            await enviarTokenParaBackend(credencial.user);
        } catch (error) {
            console.error("Erro no login:", error);

            const mensagem = traduzirErroFirebase(error);
            mostrarMensagem(mensagem, "erro");
        } finally {
            bloquearBotoes(false);
        }
    });
}


if (btnCriarConta) {
    btnCriarConta.addEventListener("click", async function () {
        const nome = document.getElementById("nome").value.trim();
        const email = document.getElementById("email").value.trim();
        const senha = document.getElementById("senha").value;

        const erroValidacao = validarCamposCadastro(nome, email, senha);

        if (erroValidacao) {
            mostrarMensagem(erroValidacao, "erro");
            return;
        }

        try {
            bloquearBotoes(true);
            mostrarMensagem("Criando conta...", "info");

            const credencial = await createUserWithEmailAndPassword(
                auth,
                email,
                senha
            );

            await updateProfile(credencial.user, {
                displayName: nome
            });

            await enviarTokenParaBackend(credencial.user);
        } catch (error) {
            console.error("Erro ao criar conta:", error);

            const mensagem = traduzirErroFirebase(error);
            mostrarMensagem(mensagem, "erro");
        } finally {
            bloquearBotoes(false);
        }
    });
}


if (btnGoogle) {
    btnGoogle.addEventListener("click", async function () {
        try {
            bloquearBotoes(true);
            mostrarMensagem("Abrindo login com Google...", "info");

            const provider = new GoogleAuthProvider();

            const credencial = await signInWithPopup(
                auth,
                provider
            );

            await enviarTokenParaBackend(credencial.user);
        } catch (error) {
            console.error("Erro no login com Google:", error);

            const mensagem = traduzirErroFirebase(error);
            mostrarMensagem(mensagem, "erro");
        } finally {
            bloquearBotoes(false);
        }
    });
}