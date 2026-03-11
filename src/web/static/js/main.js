let statusInterval = null;
let eventSource = null;


//STATUS UPDATE
async function updateStatus() {

    try {

        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 3000);

        const res = await fetch("/api/status", {
            signal: controller.signal
        });

        clearTimeout(timeout);

        if (!res.ok) {
            setOffline();
            return;
        }

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

        console.warn("Status unreachable");

        setOffline();

    }
}


//DOT STATUS
function setDot(id, ok) {

    const el = document.getElementById(id);
    if (!el) return;

    el.classList.remove("ok", "warn", "err");

    if (ok === true) el.classList.add("ok");
    else if (ok === false) el.classList.add("err");
    else el.classList.add("warn");
}


//LABEL STATUS
function setLabel(id, text) {

    const el = document.getElementById(id);
    if (el) el.textContent = text;
}


//OFFLINE STATE
function setOffline() {

    setDot("dot-ai", null);
    setDot("dot-gsm", null);
    setDot("dot-cameras", null);

    setLabel("label-ai", "AI: OFFLINE");
    setLabel("label-gsm", "GSM: OFFLINE");
    setLabel("label-cameras", "Cameras: OFFLINE");
}


//STATUS INTERVAL
function startStatusUpdates() {

    if (statusInterval) return;

    statusInterval = setInterval(updateStatus, 3000);

    updateStatus();
}


function stopStatusUpdates() {

    if (!statusInterval) return;

    clearInterval(statusInterval);
    statusInterval = null;
}


//PAGE VISIBILITY
document.addEventListener("visibilitychange", () => {

    if (document.hidden) {
        stopStatusUpdates();
    } else {
        startStatusUpdates();
    }

});


startStatusUpdates();


//========================
// LIVE EVENT STREAM (SSE)
//========================
function startEventStream() {

    if (eventSource) return;

    eventSource = new EventSource("/api/events");

    eventSource.onmessage = function(event) {

        try {

            const data = JSON.parse(
                event.data.replace(/'/g, '"')
            );

            showLiveEvent(data);

        } catch(e) {

            console.warn("Event parse error", e);

        }

    };

    eventSource.onerror = function() {

        console.warn("Event stream lost");

        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }

        setTimeout(startEventStream, 5000);

    };

}


function showLiveEvent(data) {

    const container = document.getElementById("live-events");

    if (!container) return;

    const item = document.createElement("div");

    item.className = "live-event";

    item.textContent =
        "Presence detected on " +
        data.camera +
        " at " +
        data.time;

    container.prepend(item);

    //LIMIT EVENTS
    const events = container.children;

    if (events.length > 5) {
        container.removeChild(events[events.length - 1]);
    }

}


startEventStream();