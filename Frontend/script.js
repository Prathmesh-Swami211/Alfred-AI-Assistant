const micButton = document.getElementById("micButton");
const sendButton = document.getElementById("sendButton");
const messageInput = document.getElementById("messageInput");
const communicationLog = document.getElementById("communicationLog");
const coreStatus = document.getElementById("coreStatus");
const clock = document.getElementById("clock");


// ============================================================
// CLOCK
// ============================================================

function updateClock() {

    if (!clock) {
        return;
    }

    clock.textContent =
        new Date().toLocaleTimeString();
}

updateClock();

setInterval(
    updateClock,
    1000
);


// ============================================================
// HTML ESCAPING
// ============================================================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent =
        String(text);

    return div.innerHTML;
}


// ============================================================
// COMMUNICATION LOG
// ============================================================

function addCommunication(
    sender,
    message,
    type = "system"
) {

    if (!communicationLog) {

        console.log(
            sender + ":",
            message
        );

        return;
    }

    const entry =
        document.createElement("div");

    entry.className =
        "communication-message " + type;

    entry.innerHTML = `
        <div class="communication-sender">
            ${escapeHTML(sender)}
        </div>

        <div class="communication-text">
            ${escapeHTML(message)}
        </div>
    `;

    communicationLog.appendChild(
        entry
    );

    communicationLog.scrollTop =
        communicationLog.scrollHeight;
}


// ============================================================
// CORE STATUS
// ============================================================

function setCoreStatus(
    status,
    active = false
) {

    if (coreStatus) {

        coreStatus.textContent =
            status;
    }

    if (micButton) {

        micButton.classList.toggle(
            "active",
            active
        );
    }
}


// ============================================================
// STOP ALFRED SPEAKING
// ============================================================

async function stopSpeaking() {

    try {

        await fetch(
            "/api/stop",
            {
                method: "POST"
            }
        );

    } catch (error) {

        console.error(
            "Stop speaking error:",
            error
        );
    }
}


// ============================================================
// VOICE
// ============================================================

async function activateVoice() {

    if (!micButton ||
        micButton.disabled) {

        return;
    }

    // Stop Alfred before listening.
    await stopSpeaking();

    micButton.disabled =
        true;

    setCoreStatus(
        "LISTENING...",
        true
    );

    addCommunication(
        "ALFRED",
        "Listening...",
        "system"
    );

    try {

        const response =
            await fetch(
                "/api/voice",
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Voice request failed."
            );
        }

        if (data.transcript) {

            addCommunication(
                "YOU",
                data.transcript,
                "user"
            );
        }

        if (data.response) {

            const provider =
                data.provider
                    ? " • " + data.provider
                    : "";

            addCommunication(
                "ALFRED" + provider,
                data.response,
                "alfred"
            );
        }

        setCoreStatus(
            "SYSTEM ONLINE",
            false
        );

    } catch (error) {

        console.error(
            "Voice error:",
            error
        );

        addCommunication(
            "SYSTEM",
            error.message ||
            "Voice system unavailable.",
            "error"
        );

        setCoreStatus(
            "VOICE ERROR",
            false
        );

    } finally {

        micButton.disabled =
            false;
    }
}


if (micButton) {

    micButton.addEventListener(
        "click",
        activateVoice
    );
}


// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage() {

    if (!messageInput) {
        return;
    }

    const message =
        messageInput.value.trim();

    if (!message) {
        return;
    }

    // IMPORTANT:
    // Stop Alfred immediately before sending
    // the new message.
    await stopSpeaking();

    addCommunication(
        "YOU",
        message,
        "user"
    );

    messageInput.value =
        "";

    setCoreStatus(
        "THINKING...",
        true
    );

    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Chat request failed."
            );
        }

        const provider =
            data.provider
                ? " • " + data.provider
                : "";

        addCommunication(
            "ALFRED" + provider,
            data.response ||
            "No response received.",
            "alfred"
        );

        setCoreStatus(
            "SYSTEM ONLINE",
            false
        );

    } catch (error) {

        console.error(
            "Chat error:",
            error
        );

        addCommunication(
            "SYSTEM",
            error.message ||
            "Communication system unavailable.",
            "error"
        );

        setCoreStatus(
            "SYSTEM ERROR",
            false
        );
    }
}


// ============================================================
// SEND BUTTON
// ============================================================

if (sendButton) {

    sendButton.addEventListener(
        "click",
        sendMessage
    );
}


// ============================================================
// ENTER TO SEND
// ============================================================

if (messageInput) {

    messageInput.addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();
            }
        }
    );
}


// ============================================================
// SYSTEM TELEMETRY
// ============================================================

async function updateSystemTelemetry() {

    try {

        const response =
            await fetch(
                "/api/system"
            );

        if (!response.ok) {

            throw new Error(
                "Telemetry request failed."
            );
        }

        const data =
            await response.json();


        // CPU
        const cpuValue =
            document.getElementById(
                "cpuValue"
            );

        const cpuBar =
            document.getElementById(
                "cpuBar"
            );

        if (
            cpuValue &&
            data.cpu
        ) {

            cpuValue.textContent =
                data.cpu.usage + "%";
        }

        if (
            cpuBar &&
            data.cpu
        ) {

            cpuBar.style.width =
                data.cpu.usage + "%";
        }


        // RAM
        const ramValue =
            document.getElementById(
                "ramValue"
            );

        const ramBar =
            document.getElementById(
                "ramBar"
            );

        if (
            ramValue &&
            data.memory
        ) {

            ramValue.textContent =
                data.memory.usage + "%";
        }

        if (
            ramBar &&
            data.memory
        ) {

            ramBar.style.width =
                data.memory.usage + "%";
        }


        // DISK
        const diskValue =
            document.getElementById(
                "diskValue"
            );

        const diskBar =
            document.getElementById(
                "diskBar"
            );

        if (
            diskValue &&
            data.disk
        ) {

            diskValue.textContent =
                data.disk.usage + "%";
        }

        if (
            diskBar &&
            data.disk
        ) {

            diskBar.style.width =
                data.disk.usage + "%";
        }


        // TEMPERATURE
        const tempValue =
            document.getElementById(
                "tempValue"
            );

        if (tempValue) {

            if (
                data.temperature !== null &&
                data.temperature !== undefined
            ) {

                tempValue.textContent =
                    data.temperature + "°C";

            } else {

                tempValue.textContent =
                    "N/A";
            }
        }


        // DOWNLOAD
        const downloadValue =
            document.getElementById(
                "downloadValue"
            );

        if (
            downloadValue &&
            data.network
        ) {

            downloadValue.textContent =
                data.network.download_mbps +
                " Mbps";
        }


        // UPLOAD
        const uploadValue =
            document.getElementById(
                "uploadValue"
            );

        if (
            uploadValue &&
            data.network
        ) {

            uploadValue.textContent =
                data.network.upload_mbps +
                " Mbps";
        }


        // BATTERY
        const batteryValue =
            document.getElementById(
                "batteryValue"
            );

        if (
            batteryValue &&
            data.battery
        ) {

            if (
                data.battery.available
            ) {

                batteryValue.textContent =
                    data.battery.percent +
                    "%";

            } else {

                batteryValue.textContent =
                    "N/A";
            }
        }


        // UPTIME
        const uptimeValue =
            document.getElementById(
                "uptimeValue"
            );

        if (
            uptimeValue &&
            data.uptime
        ) {

            uptimeValue.textContent =
                data.uptime.days +
                "d " +
                data.uptime.hours +
                "h " +
                data.uptime.minutes +
                "m";
        }


        // HOSTNAME
        const hostname =
            document.getElementById(
                "hostname"
            );

        if (
            hostname &&
            data.system
        ) {

            hostname.textContent =
                data.system.hostname;
        }

    } catch (error) {

        console.error(
            "Telemetry error:",
            error
        );
    }
}


updateSystemTelemetry();

setInterval(
    updateSystemTelemetry,
    2000
);


// ============================================================
// INITIALIZATION
// ============================================================

window.addEventListener(
    "load",
    function() {

        addCommunication(
            "SYSTEM",
            "Alfred command interface ready.",
            "system"
        );

        addCommunication(
            "SYSTEM",
            "Interruptible voice interface connected.",
            "system"
        );

        setCoreStatus(
            "SYSTEM ONLINE",
            false
        );
    }
);