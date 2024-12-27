###############################################################################
# app.py
###############################################################################
import asyncio
import threading
import traceback
import sqlite3
import json
import os
from collections import deque
import datetime
import webbrowser

from flask import Flask, render_template, request, jsonify
from phue import Bridge
import pyatv
from pyatv.const import DeviceState
from pyatv.interface import PushListener

# For system tray
import pystray
from pystray import MenuItem as item
from PIL import Image  # For tray icon image (pystray requires Pillow)

###############################################################################
# LOAD CONFIG (HOST & PORT)
###############################################################################
CONFIG_FILE = "config.json"

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE) as f:
        conf = json.load(f)
    HOST = conf.get("host", "127.0.0.1")
    PORT = int(conf.get("port", 8888))
else:
    HOST = "127.0.0.1"
    PORT = 8888

###############################################################################
# OTHER CONSTANTS
###############################################################################
DB_PATH = "rnr_automation.db"
ICON_PATH = os.path.join("static", "favicon.ico")

###############################################################################
# CREATE A GLOBAL EVENT LOOP
###############################################################################
loop = asyncio.new_event_loop()

###############################################################################
# FLASK APP
###############################################################################
app = Flask(__name__)

###############################################################################
# REAL-TIME LOG BUFFER
###############################################################################
server_logs = deque(maxlen=300)

def append_log(msg: str):
    """Add a timestamped line to our in-memory log buffer and print to console."""
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{now_str}] {msg}"
    server_logs.append(line)
    print(line)

@app.route("/api/logs", methods=["GET"])
def get_logs():
    """Return all logs as a JSON list of strings."""
    return jsonify(list(server_logs))

###############################################################################
# DATABASE SETUP
###############################################################################
def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    """Create tables for Apple TVs, Hue bridge, and user-defined rooms."""
    conn = get_connection()
    c = conn.cursor()

    # Apple TVs
    c.execute("""
    CREATE TABLE IF NOT EXISTS apple_tvs (
        atv_id TEXT PRIMARY KEY,
        atv_name TEXT,
        host TEXT,
        credentials TEXT,
        is_connected INTEGER DEFAULT 0
    )
    """)

    # Hue Bridge
    c.execute("""
    CREATE TABLE IF NOT EXISTS hue_bridge (
        id INTEGER PRIMARY KEY CHECK(id=1),
        ip TEXT,
        user TEXT
    )
    """)

    # Rooms (store brightness in 0–100)
    c.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        room_name TEXT PRIMARY KEY,
        apple_tv_id TEXT,
        hue_bridge_ip TEXT,
        hue_user TEXT,
        light_ids TEXT,  -- JSON array
        playing_bri INTEGER DEFAULT 60,
        paused_bri  INTEGER DEFAULT 80,
        stopped_bri INTEGER DEFAULT 100
    )
    """)

    conn.commit()
    conn.close()

###############################################################################
# APPLE TV UTILS
###############################################################################
def save_apple_tv(atv_id, atv_name, host, creds):
    """Insert or update an Apple TV row."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO apple_tvs(atv_id, atv_name, host, credentials, is_connected)
    VALUES (?, ?, ?, ?, 0)
    ON CONFLICT(atv_id) DO UPDATE SET
      atv_name=excluded.atv_name,
      host=excluded.host,
      credentials=excluded.credentials
    """, (atv_id, atv_name, host, creds))
    conn.commit()
    conn.close()
    append_log(f"AppleTV saved => id={atv_id}, name='{atv_name}', host={host}")

def update_apple_tv_connected(atv_id, connected: bool):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE apple_tvs SET is_connected=? WHERE atv_id=?", (1 if connected else 0, atv_id))
    conn.commit()
    conn.close()
    append_log(f"AppleTV => id={atv_id}, connected={connected}")

###############################################################################
# HUE UTILS
###############################################################################
def save_hue_bridge_db(ip, user):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO hue_bridge(id, ip, user)
    VALUES(1, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
      ip=excluded.ip,
      user=excluded.user
    """, (ip, user))
    conn.commit()
    conn.close()
    append_log(f"Hue Bridge => ip={ip}, user={user}")

def load_hue_bridge():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT ip, user FROM hue_bridge WHERE id=1")
    row = c.fetchone()
    conn.close()
    if row:
        (ip, usr) = row
        return {"ip": ip, "user": usr}
    return None

###############################################################################
# ROOMS UTILS
###############################################################################
def save_room_db(room_name, atv_id, hue_bridge_ip, hue_user,
                 light_ids, playing_bri, paused_bri, stopped_bri):
    lids_json = json.dumps(light_ids)
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO rooms
    (room_name, apple_tv_id, hue_bridge_ip, hue_user,
     light_ids, playing_bri, paused_bri, stopped_bri)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(room_name) DO UPDATE SET
      apple_tv_id=excluded.apple_tv_id,
      hue_bridge_ip=excluded.hue_bridge_ip,
      hue_user=excluded.hue_user,
      light_ids=excluded.light_ids,
      playing_bri=excluded.playing_bri,
      paused_bri=excluded.paused_bri,
      stopped_bri=excluded.stopped_bri
    """, (
        room_name, atv_id, hue_bridge_ip, hue_user,
        lids_json, playing_bri, paused_bri, stopped_bri
    ))
    conn.commit()
    conn.close()
    append_log(f"Room saved => room='{room_name}', apple_tv_id='{atv_id}', "
               f"hue_ip={hue_bridge_ip}, user={hue_user}, lights={light_ids}, "
               f"playing={playing_bri}, paused={paused_bri}, stopped={stopped_bri}")

def load_rooms_from_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT room_name, apple_tv_id, hue_bridge_ip, hue_user,
           light_ids, playing_bri, paused_bri, stopped_bri
    FROM rooms
    """)
    rows = c.fetchall()
    conn.close()

    out = {}
    for (rn, aid, hbip, hbusr, lids_j, pb, pab, sb) in rows:
        lids = json.loads(lids_j) if lids_j else []
        out[rn] = {
            "apple_tv_id":   aid,
            "hue_bridge_ip": hbip,
            "hue_user":      hbusr,
            "light_ids":     lids,
            "playing_bri":   pb,
            "paused_bri":    pab,
            "stopped_bri":   sb
        }
    return out

def delete_room_db(room_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM rooms WHERE room_name=?", (room_name,))
    rc = c.rowcount
    conn.commit()
    conn.close()
    return rc

###############################################################################
# HUE LIGHT CONTROL (0–100 => 0–254)
###############################################################################
def set_hue_lights(room_name, new_state):
    all_rooms = load_rooms_from_db()
    if room_name not in all_rooms:
        append_log(f"[WARN] set_hue_lights => no such room '{room_name}'")
        return
    
    rinfo = all_rooms[room_name]
    ip  = rinfo["hue_bridge_ip"]
    usr = rinfo["hue_user"]
    lids= rinfo["light_ids"]
    if not ip or not usr or not lids:
        append_log(f"[WARN] incomplete Hue => room='{room_name}', ip={ip}, user={usr}, lids={lids}")
        return
    
    p_bri = rinfo["playing_bri"]
    pa_bri= rinfo["paused_bri"]
    s_bri = rinfo["stopped_bri"]
    
    def pct_to_254(x):
        return int(round((x / 100) * 254))
    
    if new_state == "playing":
        final_pct = p_bri
    elif new_state == "paused":
        final_pct = pa_bri
    else:
        final_pct = s_bri
    
    final_bri = pct_to_254(final_pct)
    
    try:
        b = Bridge(ip, username=usr)
        b.connect()
        
        for lid in lids:
            if final_bri <= 0:
                b.set_light(lid, "on", False)
            else:
                b.set_light(lid, "on", True)
                b.set_light(lid, "bri", final_bri)
        
        append_log(
            f"Setting Hue lights => room='{room_name}', state='{new_state}', "
            f"final_bri={final_bri} (userRequested={final_pct}%)"
        )
    except Exception as ex:
        append_log(f"[ERROR] set_hue_lights => {ex}")
        traceback.print_exc()

###############################################################################
# APPLE TV MONITOR
###############################################################################
atv_connections = {}

class RnRAppleTVListener(PushListener):
    def __init__(self, atv_id):
        super().__init__()
        self.atv_id = atv_id

    def playstatus_update(self, updater, playstate):
        try:
            devmap = {
                DeviceState.Playing: "playing",
                DeviceState.Paused:  "paused",
                DeviceState.Stopped: "stopped",
                DeviceState.Idle:    "stopped"
            }
            new_state = devmap.get(playstate.device_state, "stopped")
            append_log(f"AppleTV atv_id='{self.atv_id}' => {new_state}")

            # For each room referencing this atv_id
            rdict = load_rooms_from_db()
            for rnm, rcfg in rdict.items():
                if rcfg["apple_tv_id"] == self.atv_id:
                    set_hue_lights(rnm, new_state)
        except Exception as e:
            append_log(f"[ERROR] playstatus_update => {e}")
            traceback.print_exc()

    def playstatus_error(self, updater, exception):
        append_log(f"[ERROR] push error => {self.atv_id}, ex={exception}")
        traceback.print_exc()

async def monitor_apple_tv(atv_id):
    while True:
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT host, credentials FROM apple_tvs WHERE atv_id=?", (atv_id,))
            row = c.fetchone()
            conn.close()
            if not row:
                raise Exception(f"No AppleTV => id={atv_id} in DB.")
            (host, creds) = row
            if not host:
                raise Exception(f"No host for AppleTV => id={atv_id}")

            append_log(f"Connecting to AppleTV => id={atv_id}, host={host}")
            sr = await pyatv.scan(loop, hosts=[host])
            if not sr:
                raise Exception(f"No AppleTV discovered => host={host}")
            conf = sr[0]
            conf.set_credentials(pyatv.Protocol.AirPlay, creds or "")
            atv = await pyatv.connect(conf, loop)
            update_apple_tv_connected(atv_id, True)
            atv_connections[atv_id] = atv

            listener = RnRAppleTVListener(atv_id)
            atv.push_updater.listener = listener
            atv.push_updater.start()

            while True:
                await asyncio.sleep(10)

        except Exception as ex:
            append_log(f"[ERROR] monitor_apple_tv => atv_id={atv_id}, ex={ex}")
            update_apple_tv_connected(atv_id, False)
            await asyncio.sleep(5)
        finally:
            if atv_id in atv_connections:
                try:
                    atv_connections[atv_id].push_updater.stop()
                    atv_connections[atv_id].close()
                except:
                    pass
                del atv_connections[atv_id]

###############################################################################
# BACKGROUND EVENT LOOP
###############################################################################
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

###############################################################################
# FLASK ROUTES (HTML)
###############################################################################
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/manage_rooms")
def manage_rooms():
    return render_template("manage_rooms.html")

@app.route("/pair")
def pair():
    return render_template("pair.html")

@app.route("/hue")
def hue():
    return render_template("hue.html")

###############################################################################
# HUE APIs
###############################################################################
@app.route("/api/hue/pair", methods=["POST"])
def api_hue_pair():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON"}), 400
    ip = data.get("bridge_ip")
    if not ip:
        return jsonify({"error": "bridge_ip required"}), 400
    try:
        b = Bridge(ip)
        user = None
        try:
            tmp_user = b.register_app()
            if tmp_user:
                user = tmp_user
        except Exception as e:
            append_log(f"[WARN] hue register_app => {e}")
        b.connect()
        if user is None:
            user = b.username
        if not user:
            return jsonify({"error": "No user. Did you press link button?"}), 400

        save_hue_bridge_db(ip, user)
        append_log(f"Hue Bridge => ip={ip}, user={user}")
        return jsonify({"status": "hue_paired", "hue_user": user})
    except Exception as ex:
        append_log(f"[ERROR] hue_pair => {ex}")
        traceback.print_exc()
        return jsonify({"error": str(ex)}), 500

@app.route("/api/hue/status", methods=["GET"])
def api_hue_status():
    hb = load_hue_bridge()
    if not hb:
        return jsonify({"error": "No HueBridge in DB"}), 404
    return jsonify({"bridge_ip": hb["ip"], "hue_user": hb["user"]})

@app.route("/api/hue/lights", methods=["GET"])
def api_hue_lights():
    hb = load_hue_bridge()
    if not hb:
        return jsonify({})
    try:
        b = Bridge(hb["ip"], hb["user"])
        b.connect()
        all_lights = b.get_light_objects("id")
        out = {}
        for lid, obj in all_lights.items():
            out[str(lid)] = obj.name
        return jsonify(out)
    except Exception as ex:
        append_log(f"[ERROR] hue_lights => {ex}")
        traceback.print_exc()
        return jsonify({"error": str(ex)}), 500

###############################################################################
# APPLE TV PAIRING
###############################################################################
pairing_sessions = {}

@app.route("/api/start_pairing", methods=["POST"])
def start_pairing():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON"}), 400
    atv_id   = data.get("apple_tv_id")
    atv_name = data.get("apple_tv_name")
    host     = data.get("ip_address")
    protocol = data.get("protocol", "airplay")

    if not atv_id or not atv_name or not host:
        return jsonify({"error": "apple_tv_id, apple_tv_name, ip_address required"}), 400

    async def do_start():
        scan_res = await pyatv.scan(loop, hosts=[host])
        if not scan_res:
            raise Exception(f"No AppleTV at {host}")
        conf = scan_res[0]
        try:
            p = getattr(pyatv.Protocol, protocol.capitalize())
        except AttributeError:
            p = pyatv.Protocol.AirPlay
        pair_obj = await pyatv.pair(conf, p, loop=loop)
        pairing_sessions[atv_id] = {
            "pairing": pair_obj,
            "host": host,
            "name": atv_name
        }
        await pair_obj.begin()

    try:
        save_apple_tv(atv_id, atv_name, host, creds="")
        fut = asyncio.run_coroutine_threadsafe(do_start(), loop)
        fut.result()
        append_log(f"start_pairing => ID={atv_id}, name={atv_name}, ip={host}")
        return jsonify({"status": "pairing_started"})
    except Exception as ex:
        append_log(f"[ERROR] start_pairing => {ex}")
        traceback.print_exc()
        return jsonify({"error": str(ex)}), 500

@app.route("/api/enter_pin", methods=["POST"])
def enter_pin():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON"}), 400
    atv_id = data.get("apple_tv_id")
    pin    = data.get("pin")
    if not atv_id or not pin:
        return jsonify({"error": "Missing atv_id or pin"}), 400

    if atv_id not in pairing_sessions:
        return jsonify({"error": "No active pairing session for that atv_id"}), 400

    pairing_info = pairing_sessions[atv_id]
    pairing_obj  = pairing_info["pairing"]
    host         = pairing_info["host"]
    friendlyName = pairing_info["name"]

    async def do_finish():
        pairing_obj.pin(pin)
        await pairing_obj.finish()
        if pairing_obj.has_paired:
            cred = pairing_obj.service.credentials
            save_apple_tv(atv_id, friendlyName, host, cred)
            append_log(f"Pairing => finished, id={atv_id}, name={friendlyName}")
            loop.create_task(monitor_apple_tv(atv_id))
            return "pairing_finished"
        else:
            return "pairing_failed"

    try:
        fut = asyncio.run_coroutine_threadsafe(do_finish(), loop)
        ret = fut.result()
        if ret == "pairing_finished":
            del pairing_sessions[atv_id]
        return jsonify({"status": ret})
    except Exception as ex:
        append_log(f"[ERROR] enter_pin => {ex}")
        return jsonify({"error": f"Pairing failed => {ex}"}), 500

@app.route("/api/apple_tvs", methods=["GET"])
def api_list_apple_tvs():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT atv_id, atv_name, host, credentials, is_connected FROM apple_tvs WHERE credentials<>''")
    rows = c.fetchall()
    conn.close()

    out = {}
    for (aid, aname, h, creds, ic) in rows:
        out[aname] = {
            "apple_tv_id": aid,
            "ip": h,
            "connected": bool(ic)
        }
    return jsonify(out)

###############################################################################
# ROOMS
###############################################################################
@app.route("/api/rooms", methods=["GET"])
def api_list_rooms():
    """Return user-defined rooms as { roomName: {...} }, brightness in 0–100."""
    return jsonify(load_rooms_from_db())

@app.route("/api/rooms", methods=["POST"])
def add_room():
    data = request.json
    room_name = data["room_name"]
    atv_id    = data.get("apple_tv_id", "")
    lids      = data.get("light_ids", [])

    p_bri = int(data.get("playing_bri", 60))
    pa_bri= int(data.get("paused_bri", 80))
    s_bri = int(data.get("stopped_bri", 100))

    hb = load_hue_bridge()
    ip_  = hb["ip"]  if hb else ""
    usr_ = hb["user"] if hb else ""

    save_room_db(room_name, atv_id, ip_, usr_, lids, p_bri, pa_bri, s_bri)
    return jsonify({"status": "room_added", "room_name": room_name})

@app.route("/api/rooms/<room_name>/automation", methods=["POST"])
def update_room_automation(room_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT apple_tv_id, hue_bridge_ip, hue_user, light_ids
        FROM rooms
        WHERE room_name=?
    """, (room_name,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Room not found"}), 404

    (aid, hb_ip, hb_usr, lids_j) = row
    lids = json.loads(lids_j) if lids_j else []

    data  = request.json
    p_bri = int(data.get("playing_bri", 60))
    pa_bri= int(data.get("paused_bri", 80))
    s_bri = int(data.get("stopped_bri", 100))

    save_room_db(room_name, aid, hb_ip, hb_usr, lids, p_bri, pa_bri, s_bri)
    return jsonify({"status": "automation_updated", "room": room_name})

@app.route("/api/rooms/<room_name>", methods=["DELETE"])
def api_delete_room(room_name):
    rc = delete_room_db(room_name)
    if rc > 0:
        append_log(f"Room => deleted name='{room_name}'")
        return jsonify({"status": "room_deleted", "room_name": room_name})
    else:
        return jsonify({"error": "Room not found"}), 404

###############################################################################
# TRAY ICON
###############################################################################
tray_icon = None

def launch_browser(_icon=None, _item=None):
    webbrowser.open(f"http://{HOST}:{PORT}")

def on_exit(_icon=None, _item=None):
    """Stop the Flask app and close the tray."""
    append_log("Exiting RnR Automation...")
    # Stop the event loop
    loop.stop()
    # Stop the tray icon
    tray_icon.stop()

def setup_tray_icon():
    global tray_icon
    
    # Try loading favicon.ico from the static folder
    try:
        icon_image = Image.open(ICON_PATH)
    except Exception as e:
        print(f"Could not load tray icon from {ICON_PATH}: {e}")
        # Fallback: create a placeholder image if favicon.ico is missing
        icon_image = Image.new("RGB", (32, 32), color="white")
        d = ImageDraw.Draw(icon_image)
        d.text((4, 10), "RnR", fill="black")

    # Build your tray menu items, e.g. "Launch Browser" and "Exit"
    menu = (
        pystray.MenuItem("Launch Browser", launch_browser),
        pystray.MenuItem("Exit", on_exit),
    )
    
    tray_icon = pystray.Icon("ATV & Hue", icon_image, "ATV & Hue", menu)
    tray_icon.run()
###############################################################################
# MAIN LAUNCH
###############################################################################
if __name__ == "__main__":
    create_tables()

    # Start Apple TV monitors for any Apple TVs that are fully paired
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT atv_id FROM apple_tvs WHERE credentials<>''")
    existing_tvs = c.fetchall()
    conn.close()

    for (aid,) in existing_tvs:
        loop.create_task(monitor_apple_tv(aid))

    # Start the asyncio loop in a background thread
    t = threading.Thread(target=start_loop, args=(loop,), daemon=True)
    t.start()

    # Start Flask in another thread so it won't block the tray icon
    flask_thread = threading.Thread(
        target=lambda: app.run(host=HOST, port=PORT, debug=False),
        daemon=True
    )
    flask_thread.start()

    # Finally, set up and show the tray icon (blocking call).
    setup_tray_icon()
