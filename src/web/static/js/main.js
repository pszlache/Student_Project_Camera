async function updateStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;

        const data = await res.json();

        setDot("dot-ai", data.ai);
        setDot("dot-gsm", data.gsm);
        setDot("dot-cameras", data.cameras);

        setLabel("label-ai", data.ai ? "AI: OK" : "AI: ERROR");
        setLabel("label-gsm", data.gsm ? "GSM: READY" : "GSM: OFF");
        setLabel(
            "label-cameras",
            data.cameras ? "Cameras: ONLINE" : "Cameras: NONE"
        );

    } catch (e) {
        console.error("Status error:", e);
    }
}

function setDot(id, ok) {
    const el = document.getElementById(id);
    if (!el) return;

    el.classList.remove("ok", "warn", "err");

    if (ok === true) el.classList.add("ok");
    else if (ok === false) el.classList.add("err");
    else el.classList.add("warn");
}

function setLabel(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

setInterval(updateStatus, 3000);
updateStatus();