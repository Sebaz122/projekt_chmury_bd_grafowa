function show_output(data) {
    document.getElementById("output").textContent =
        JSON.stringify(data, null, 2);
}

function load_users() {
    fetch("/api/users")
        .then(res => res.json())
        .then(show_output)
        .catch(err => alert("error: " + err));
}

function add_user() {
    const name = document.getElementById("userName").value.trim();
    if (!name) return alert("Podaj nazwę użytkownika");

    fetch("/api/users", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ name })
    })
    .then(res => res.json())
    .then(show_output)
    .catch(err => alert("error: " + err));
}

function delete_user() {
    const name = document.getElementById("deleteUserName").value.trim();
    if (!name) return alert("Podaj nazwę użytkownika");

    fetch("/api/delete_user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user: name })
    })
    .then(async res => {
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            show_output(data);
            throw new Error(data.error || "error: usuwanie nie udało się");
        }
        show_output(data);
    })
    .catch(err => alert("error: " + err));
}

function change_username() {
    const old_username = document.getElementById("oldUsername").value.trim();
    const new_username = document.getElementById("newUsername").value.trim();
    if (!old_username) return alert("Podaj obecną nazwę użytkownika");
    if (!new_username) return alert("Podaj nową nazwę użytkownika");

    fetch("/api/change_username", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ old_username, new_username })
    })
    .then(res => res.json())
    .then(data => {
        show_output(data);
    })
    .catch(err => alert("error: " + err));
}

function add_user_information() {
    const user = document.getElementById("infoUser").value.trim();
    const info_key = document.getElementById("infoKey").value.trim();
    const info_value = document.getElementById("infoValue").value.trim();
    if (!user) return alert("Podaj użytkownika");
    if (!info_key) return alert("Podaj rodzaj informacji");
    if (!info_value) return alert("Podaj wartość informacji");

    fetch("/api/add_user_information", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user, info_key, info_value })
    })
    .then(res => res.json())
    .then(show_output)
    .catch(err => alert("error: " + err));
}

function find_user_friends() {
    const user = document.getElementById("friendsOfUser").value.trim();
    if (!user) return alert("Podaj nazwę użytkownika");

    fetch("/api/find_user_friends", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ user })
    })
    .then(res => res.json())
    .then(show_output)
    .catch(err => alert("error: " + err));
}

function load_interests(silent = false) {
    fetch("/api/interests")
        .then(res => res.json())
        .then(data => {
            if (!silent) {
                show_output(data);
            }
            update_interests_dropdown(data);
        })
        .catch(err => alert("error: " + err));
}

function add_interest() {
    const name = document.getElementById("interestName").value.trim();
    if (!name) return alert("Podaj zainteresowanie");

    fetch("/api/interests", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ name })
    })
    .then(res => res.json())
    .then(data => {
        show_output(data);
        load_interests(true); 
    })
    .catch(err => alert("error: " + err));
}

function delete_interest() {
    const interest = document.getElementById("deleteInterestName").value.trim();
    if (!interest) return alert("Podaj zainteresowanie");

    fetch("/api/delete_interest", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ interest })
    })
    .then(res => res.json())
    .then(data => {
        show_output(data);
        load_interests(true);
    })
    .catch(err => alert("error: " + err));
}

function update_interests_dropdown(interests) {
    const fill = (selectId) => {
        const el = document.getElementById(selectId);
        if (!el) return;
        el.innerHTML = "";
        interests.forEach(i => {
            const opt = document.createElement("option");
            opt.value = i.name;
            opt.textContent = i.name;
            el.appendChild(opt);
        });
    };
    fill("likesInterest");
    fill("deleteLikesInterest");
}

function find_user_interests() {
    const user = document.getElementById("interestsOfUser").value.trim();
    if (!user) return alert("Podaj nazwę użytkownika");

    fetch("/api/find_user_interests", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ user })
    })
    .then(res => res.json())
    .then(show_output)
    .catch(err => alert("error: " + err));
}

function add_friendship() {
    const a = document.getElementById("friendA").value.trim();
    const b = document.getElementById("friendB").value.trim();

    if (!a || !b) return alert("Podaj oba pola");

    fetch("/api/friends", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ from: a, to: b })
    })
    .then(res => res.json())
    .then(show_output)
    .catch(err => alert("error: " + err));
}

function add_likes() {
    const user = document.getElementById("likesUser").value.trim();
    const interest = document.getElementById("likesInterest").value;

    if (!user) return alert("Podaj nazwę użytkownika");

    fetch("/api/likes", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ user, interest })
    })
    .then(res => res.json())
    .then(show_output)
    .catch(err => alert("error: " + err));
}

function delete_friendship() {
    const a = document.getElementById("delFriendA").value.trim();
    const b = document.getElementById("delFriendB").value.trim();
    if (!a || !b) return alert("Podaj oba pola");

    fetch("/api/delete_friendship", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ user_a: a, user_b: b })
    })
    .then(res => res.json())
    .then(show_output)
    .catch(err => alert("error: " + err));
}

function delete_likes() {
    const user = document.getElementById("delLikesUser").value.trim();
    const interest = document.getElementById("deleteLikesInterest").value;
    if (!user) return alert("Podaj nazwę użytkownika");

    fetch("/api/delete_likes", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ user, interest })
    })
    .then(res => res.json())
    .then(show_output)
    .catch(err => alert("error: " + err));
}

load_interests(true);
