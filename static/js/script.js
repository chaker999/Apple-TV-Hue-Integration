///////////////////////////////
// UTILITY for appending logs
///////////////////////////////
function appendDebug(selector, msg) {
  const el = document.querySelector(selector);
  if (el) {
    el.textContent += msg + "\n";
    el.scrollTop = el.scrollHeight;
  }
}

///////////////////////////////
// manage_rooms.html SCRIPTS
///////////////////////////////
function setupManageRooms() {
  const formAddRoom = document.getElementById("formAddRoom");
  if (!formAddRoom) return; // If we're not on manage_rooms page, bail.

  formAddRoom.addEventListener("submit", function (e) {
    e.preventDefault();
    const roomName = document.getElementById("roomName").value.trim();
    const appleHost = document.getElementById("appleHost").value.trim();
    const appleCreds = document.getElementById("appleCreds").value.trim();
    const hueBridgeIp = document.getElementById("hueBridgeIp").value.trim();
    const hueUser = document.getElementById("hueUser").value.trim();
    const lightIds = document.getElementById("lightIds").value
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0)
      .map((s) => parseInt(s));

    axios
      .post("/add_room", {
        room_name: roomName,
        apple_tv_host: appleHost,
        apple_tv_credentials: appleCreds,
        hue_bridge_ip: hueBridgeIp,
        hue_user: hueUser,
        light_ids: lightIds,
      })
      .then((resp) => {
        appendDebug("#debugConsole", JSON.stringify(resp.data, null, 2));
        refreshRoomsList();
      })
      .catch((err) => {
        appendDebug("#debugConsole", "Error: " + err);
      });
  });

  const refreshRoomsBtn = document.getElementById("refreshRoomsBtn");
  refreshRoomsBtn.addEventListener("click", refreshRoomsList);
  refreshRoomsList();
}

function refreshRoomsList() {
  axios
    .get("/rooms")
    .then((resp) => {
      const roomsList = document.getElementById("roomsList");
      roomsList.innerHTML = "";
      const data = resp.data;
      Object.keys(data).forEach((roomName) => {
        const info = data[roomName];
        const li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.textContent = `${roomName} - AppleTV: ${info.apple_tv_host}, Connected: ${info.is_connected}`;
        roomsList.appendChild(li);
      });
      appendDebug("#debugConsole", JSON.stringify(data, null, 2));
    })
    .catch((err) => {
      appendDebug("#debugConsole", "Error fetching rooms: " + err);
    });
}

///////////////////////////////
// pair.html SCRIPTS
///////////////////////////////
function setupPairPage() {
  const formStartPairing = document.getElementById("formStartPairing");
  if (!formStartPairing) return; // Not on pair page

  formStartPairing.addEventListener("submit", function (e) {
    e.preventDefault();
    const roomName = document.getElementById("pairRoomName").value.trim();
    const host = document.getElementById("pairHost").value.trim();
    const protocol = document.getElementById("protocolType").value;

    axios
      .post("/start_pairing", {
        room_name: roomName,
        apple_tv_host: host,
        protocol: protocol,
      })
      .then((resp) => {
        appendDebug("#debugConsolePair", JSON.stringify(resp.data, null, 2));
      })
      .catch((err) => {
        appendDebug("#debugConsolePair", "Error: " + err);
      });
  });

  const formSendPin = document.getElementById("formSendPin");
  formSendPin.addEventListener("submit", function (e) {
    e.preventDefault();
    const roomName = document.getElementById("pinRoomName").value.trim();
    const pin = document.getElementById("pinCode").value.trim();

    axios
      .post("/send_pin", {
        room_name: roomName,
        pin: pin,
      })
      .then((resp) => {
        appendDebug("#debugConsolePair", JSON.stringify(resp.data, null, 2));
      })
      .catch((err) => {
        appendDebug("#debugConsolePair", "Error: " + err);
      });
  });
}

///////////////////////////////
// On DOMContentLoaded, init
///////////////////////////////
document.addEventListener("DOMContentLoaded", function () {
  setupManageRooms();
  setupPairPage();
});
