//STATUS DOTS

async function updateStatus() {
    try {
        const res = await fetch("/api/status");

        if (!res.ok) {
            console.error("Status API error");
            return;
        }

        const data = await res.json();

        setDot("dot-ai", data.ai);
        setDot("dot-gsm", data.gsm);
        setDot("dot-cameras", data.cameras);

    } catch (e) {
        console.error("Status fetch failed:", e);
    }
}

function setDot(id, ok) {
    const el = document.getElementById(id);
    if (!el) return;

    el.classList.remove("ok", "warn", "err");

    if (ok === true) {
        el.classList.add("ok");
    } else if (ok === false) {
        el.classList.add("err");
    } else {
        el.classList.add("warn");
    }
}

// Update every 3 seconds
setInterval(updateStatus, 3000);

// Initial call
updateStatus();